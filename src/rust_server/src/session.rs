use std::sync::Arc;
use std::collections::HashMap;
use tokio::sync::RwLock;
use uuid::Uuid;
use serde::{Serialize, Deserialize};
use anyhow::{Result, Context};
use log::{info, error, debug, warn};
use chrono::{DateTime, Utc};
use dashmap::DashMap;
use crate::game::{GameManager, Game};
use crate::ServerError;

/// Конфигурация менеджера сессий
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionConfig {
    /// Время жизни сессии (в секундах)
    pub session_ttl: u64,
    /// Интервал очистки устаревших сессий (в секундах)
    pub cleanup_interval: u64,
    /// Максимальное количество сессий
    pub max_sessions: usize,
    /// Включить проверку активности сессий
    pub enable_heartbeat: bool,
    /// Интервал проверки активности (в секундах)
    pub heartbeat_interval: u64,
    /// Таймаут неактивности (в секундах)
    pub inactivity_timeout: u64,
}

impl Default for SessionConfig {
    fn default() -> Self {
        Self {
            session_ttl: 3600,
            cleanup_interval: 300,
            max_sessions: 1000,
            enable_heartbeat: true,
            heartbeat_interval: 30,
            inactivity_timeout: 300,
        }
    }
}

/// Роль пользователя
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum UserRole {
    /// Гость
    Guest,
    /// Игрок
    Player,
    /// Наблюдатель
    Spectator,
    /// Администратор
    Admin,
}

/// Пользователь
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    /// Идентификатор пользователя
    pub id: Uuid,
    /// Имя пользователя
    pub name: String,
    /// Роль пользователя
    pub role: UserRole,
    /// Время создания
    pub created_at: DateTime<Utc>,
    /// Время последней активности
    pub last_activity: DateTime<Utc>,
    /// Дополнительные данные
    pub metadata: HashMap<String, String>,
}

impl User {
    /// Создает нового пользователя
    pub fn new(name: String, role: UserRole) -> Self {
        Self {
            id: Uuid::new_v4(),
            name,
            role,
            created_at: Utc::now(),
            last_activity: Utc::now(),
            metadata: HashMap::new(),
        }
    }

    /// Обновляет время последней активности
    pub fn update_activity(&mut self) {
        self.last_activity = Utc::now();
    }

    /// Проверяет, активен ли пользователь
    pub fn is_active(&self, inactivity_timeout: u64) -> bool {
        let now = Utc::now();
        let duration = now.signed_duration_since(self.last_activity);
        duration.num_seconds() < inactivity_timeout as i64
    }
}

/// Сессия
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Session {
    /// Идентификатор сессии
    pub id: Uuid,
    /// Пользователь
    pub user: User,
    /// Идентификатор игры
    pub game_id: Option<Uuid>,
    /// Время создания
    pub created_at: DateTime<Utc>,
    /// Время истечения
    pub expires_at: DateTime<Utc>,
    /// Время последней активности
    pub last_activity: DateTime<Utc>,
    /// Дополнительные данные
    pub metadata: HashMap<String, String>,
}

impl Session {
    /// Создает новую сессию
    pub fn new(user: User, ttl: u64) -> Self {
        let now = Utc::now();
        let expires_at = now + chrono::Duration::seconds(ttl as i64);
        
        Self {
            id: Uuid::new_v4(),
            user,
            game_id: None,
            created_at: now,
            expires_at,
            last_activity: now,
            metadata: HashMap::new(),
        }
    }

    /// Обновляет время последней активности
    pub fn update_activity(&mut self) {
        self.last_activity = Utc::now();
        self.user.update_activity();
    }

    /// Продлевает сессию
    pub fn extend(&mut self, ttl: u64) {
        let now = Utc::now();
        self.expires_at = now + chrono::Duration::seconds(ttl as i64);
        self.update_activity();
    }

    /// Проверяет, истекла ли сессия
    pub fn is_expired(&self) -> bool {
        Utc::now() > self.expires_at
    }

    /// Проверяет, активна ли сессия
    pub fn is_active(&self, inactivity_timeout: u64) -> bool {
        if self.is_expired() {
            return false;
        }
        
        let now = Utc::now();
        let duration = now.signed_duration_since(self.last_activity);
        duration.num_seconds() < inactivity_timeout as i64
    }

    /// Присоединяет сессию к игре
    pub fn join_game(&mut self, game_id: Uuid) {
        self.game_id = Some(game_id);
        self.update_activity();
    }

    /// Покидает игру
    pub fn leave_game(&mut self) {
        self.game_id = None;
        self.update_activity();
    }
}

/// Менеджер сессий
pub struct SessionManager {
    /// Конфигурация менеджера сессий
    config: SessionConfig,
    /// Менеджер игр
    game_manager: Arc<GameManager>,
    /// Хранилище сессий
    sessions: Arc<DashMap<Uuid, Session>>,
    /// Флаг работы менеджера
    running: Arc<tokio::sync::RwLock<bool>>,
    /// Задача очистки устаревших сессий
    cleanup_task: Arc<tokio::sync::RwLock<Option<tokio::task::JoinHandle<()>>>>,
    /// Задача проверки активности сессий
    heartbeat_task: Arc<tokio::sync::RwLock<Option<tokio::task::JoinHandle<()>>>>,
}

impl SessionManager {
    /// Создает новый экземпляр менеджера сессий
    pub fn new(config: &SessionConfig, game_manager: Arc<GameManager>) -> Result<Self> {
        Ok(Self {
            config: config.clone(),
            game_manager,
            sessions: Arc::new(DashMap::new()),
            running: Arc::new(tokio::sync::RwLock::new(false)),
            cleanup_task: Arc::new(tokio::sync::RwLock::new(None)),
            heartbeat_task: Arc::new(tokio::sync::RwLock::new(None)),
        })
    }

    /// Запускает менеджер сессий
    pub fn start(&self) -> Result<()> {
        info!("Starting Session Manager");
        
        // Устанавливаем флаг работы
        let mut running = self.running.write().await;
        *running = true;
        drop(running);
        
        // Запускаем задачу очистки устаревших сессий
        let sessions = self.sessions.clone();
        let running = self.running.clone();
        let cleanup_interval = self.config.cleanup_interval;
        
        let cleanup_task = tokio::spawn(async move {
            while *running.read().await {
                // Удаляем устаревшие сессии
                sessions.retain(|_, session| !session.is_expired());
                
                // Пауза перед следующей очисткой
                tokio::time::sleep(tokio::time::Duration::from_secs(cleanup_interval)).await;
            }
        });
        
        // Сохраняем задачу очистки
        let mut cleanup_task_guard = self.cleanup_task.write().await;
        *cleanup_task_guard = Some(cleanup_task);
        
        // Запускаем задачу проверки активности сессий, если включено
        if self.config.enable_heartbeat {
            let sessions = self.sessions.clone();
            let running = self.running.clone();
            let heartbeat_interval = self.config.heartbeat_interval;
            let inactivity_timeout = self.config.inactivity_timeout;
            
            let heartbeat_task = tokio::spawn(async move {
                while *running.read().await {
                    // Проверяем активность сессий
                    for mut session_ref in sessions.iter_mut() {
                        let session = &mut *session_ref;
                        
                        if !session.is_active(inactivity_timeout) {
                            // Сессия неактивна, помечаем ее как истекшую
                            session.expires_at = Utc::now();
                        }
                    }
                    
                    // Пауза перед следующей проверкой
                    tokio::time::sleep(tokio::time::Duration::from_secs(heartbeat_interval)).await;
                }
            });
            
            // Сохраняем задачу проверки активности
            let mut heartbeat_task_guard = self.heartbeat_task.write().await;
            *heartbeat_task_guard = Some(heartbeat_task);
        }
        
        info!("Session Manager started successfully");
        Ok(())
    }

    /// Останавливает менеджер сессий
    pub fn stop(&self) -> Result<()> {
        info!("Stopping Session Manager");
        
        // Сбрасываем флаг работы
        let mut running = self.running.write().await;
        *running = false;
        drop(running);
        
        // Ожидаем завершения задачи очистки
        let mut cleanup_task_guard = self.cleanup_task.write().await;
        if let Some(task) = cleanup_task_guard.take() {
            // Ожидаем завершения задачи
            tokio::task::spawn(async move {
                if let Err(e) = task.await {
                    error!("Error joining cleanup task: {}", e);
                }
            });
        }
        
        // Ожидаем завершения задачи проверки активности
        let mut heartbeat_task_guard = self.heartbeat_task.write().await;
        if let Some(task) = heartbeat_task_guard.take() {
            // Ожидаем завершения задачи
            tokio::task::spawn(async move {
                if let Err(e) = task.await {
                    error!("Error joining heartbeat task: {}", e);
                }
            });
        }
        
        info!("Session Manager stopped successfully");
        Ok(())
    }

    /// Создает новую сессию
    pub fn create_session(&self, user_name: String, role: UserRole) -> Result<Uuid> {
        // Проверяем, не превышено ли максимальное количество сессий
        if self.sessions.len() >= self.config.max_sessions {
            return Err(anyhow::anyhow!("Maximum number of sessions reached"));
        }
        
        // Создаем пользователя
        let user = User::new(user_name, role);
        
        // Создаем сессию
        let session = Session::new(user, self.config.session_ttl);
        let session_id = session.id;
        
        // Сохраняем сессию
        self.sessions.insert(session_id, session);
        
        Ok(session_id)
    }

    /// Удаляет сессию
    pub fn delete_session(&self, session_id: Uuid) -> Result<()> {
        // Проверяем, существует ли сессия
        if !self.sessions.contains_key(&session_id) {
            return Err(anyhow::anyhow!("Session not found"));
        }
        
        // Получаем сессию
        let session = self.sessions.get(&session_id).context("Session not found")?;
        
        // Если сессия присоединена к игре, покидаем игру
        if let Some(game_id) = session.game_id {
            // Получаем ID пользователя
            let user_id = session.user.id;
            
            // Покидаем игру
            if let Err(e) = self.game_manager.remove_player_from_game(game_id, user_id) {
                warn!("Error removing player from game: {}", e);
            }
        }
        
        // Удаляем сессию
        self.sessions.remove(&session_id);
        
        Ok(())
    }

    /// Получает сессию по ID
    pub fn get_session(&self, session_id: Uuid) -> Result<Session> {
        self.sessions.get(&session_id)
            .map(|s| s.clone())
            .context("Session not found")
    }

    /// Обновляет активность сессии
    pub fn update_session_activity(&self, session_id: Uuid) -> Result<()> {
        // Проверяем, существует ли сессия
        let mut session = self.sessions.get_mut(&session_id).context("Session not found")?;
        
        // Обновляем активность
        session.update_activity();
        
        Ok(())
    }

    /// Продлевает сессию
    pub fn extend_session(&self, session_id: Uuid) -> Result<()> {
        // Проверяем, существует ли сессия
        let mut session = self.sessions.get_mut(&session_id).context("Session not found")?;
        
        // Продлеваем сессию
        session.extend(self.config.session_ttl);
        
        Ok(())
    }

    /// Присоединяет сессию к игре
    pub async fn join_game(&self, session_id: Uuid, game_id: Uuid) -> Result<()> {
        // Проверяем, существует ли сессия
        let mut session = self.sessions.get_mut(&session_id).context("Session not found")?;
        
        // Проверяем, существует ли игра
        let game = self.game_manager.get_game(game_id)?;
        
        // Проверяем, можно ли присоединиться к игре
        if !game.can_join() {
            return Err(anyhow::anyhow!("Cannot join this game"));
        }
        
        // Если сессия уже присоединена к другой игре, покидаем ее
        if let Some(current_game_id) = session.game_id {
            if current_game_id != game_id {
                // Покидаем текущую игру
                let user_id = session.user.id;
                if let Err(e) = self.game_manager.remove_player_from_game(current_game_id, user_id) {
                    warn!("Error removing player from game: {}", e);
                }
            } else {
                // Уже присоединен к этой игре
                return Ok(());
            }
        }
        
        // Добавляем игрока в игру
        let user_id = session.user.id;
        let user_name = session.user.name.clone();
        
        self.game_manager.add_player_to_game(game_id, user_name).await?;
        
        // Присоединяем сессию к игре
        session.join_game(game_id);
        
        Ok(())
    }

    /// Покидает игру
    pub fn leave_game(&self, session_id: Uuid) -> Result<()> {
        // Проверяем, существует ли сессия
        let mut session = self.sessions.get_mut(&session_id).context("Session not found")?;
        
        // Проверяем, присоединена ли сессия к игре
        if let Some(game_id) = session.game_id {
            // Покидаем игру
            let user_id = session.user.id;
            if let Err(e) = self.game_manager.remove_player_from_game(game_id, user_id) {
                warn!("Error removing player from game: {}", e);
            }
            
            // Отсоединяем сессию от игры
            session.leave_game();
        }
        
        Ok(())
    }

    /// Получает список всех сессий
    pub fn get_all_sessions(&self) -> Vec<Session> {
        self.sessions.iter()
            .map(|s| s.clone())
            .collect()
    }

    /// Получает список активных сессий
    pub fn get_active_sessions(&self) -> Vec<Session> {
        self.sessions.iter()
            .filter(|s| !s.is_expired())
            .map(|s| s.clone())
            .collect()
    }

    /// Проверяет, работает ли менеджер сессий
    pub fn is_running(&self) -> bool {
        *self.running.blocking_read()
    }

    /// Получает менеджер игр
    pub fn game_manager(&self) -> &Arc<GameManager> {
        &self.game_manager
    }
}

impl Drop for SessionManager {
    fn drop(&mut self) {
        // Остановка менеджера при уничтожении
        if *self.running.blocking_read() {
            if let Err(e) = self.stop() {
                error!("Error stopping Session Manager during drop: {}", e);
            }
        }
    }
}
