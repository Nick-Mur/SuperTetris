use std::sync::Arc;
use std::collections::HashMap;
use tokio::sync::RwLock;
use warp::{Filter, Reply, Rejection};
use warp::ws::{WebSocket, Message};
use uuid::Uuid;
use serde::{Serialize, Deserialize};
use anyhow::{Result, Context};
use log::{info, error, debug, warn};
use futures::{StreamExt, SinkExt};
use tokio::sync::mpsc;
use dashmap::DashMap;
use crate::session::{SessionManager, Session};
use crate::ServerError;

/// Конфигурация сетевого менеджера
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NetworkConfig {
    /// Хост для прослушивания
    pub host: String,
    /// Порт для прослушивания
    pub port: u16,
    /// Максимальный размер сообщения (в байтах)
    pub max_message_size: usize,
    /// Таймаут соединения (в секундах)
    pub connection_timeout: u64,
    /// Включить CORS
    pub enable_cors: bool,
    /// Разрешенные источники для CORS
    pub cors_allowed_origins: Vec<String>,
    /// Включить SSL
    pub enable_ssl: bool,
    /// Путь к сертификату SSL
    pub ssl_cert_path: String,
    /// Путь к ключу SSL
    pub ssl_key_path: String,
}

impl Default for NetworkConfig {
    fn default() -> Self {
        Self {
            host: "127.0.0.1".to_string(),
            port: 8080,
            max_message_size: 1024 * 1024, // 1 MB
            connection_timeout: 60,
            enable_cors: true,
            cors_allowed_origins: vec!["*".to_string()],
            enable_ssl: false,
            ssl_cert_path: "cert.pem".to_string(),
            ssl_key_path: "key.pem".to_string(),
        }
    }
}

/// Тип сообщения
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum MessageType {
    /// Аутентификация
    Auth,
    /// Создание игры
    CreateGame,
    /// Присоединение к игре
    JoinGame,
    /// Покидание игры
    LeaveGame,
    /// Запуск игры
    StartGame,
    /// Пауза игры
    PauseGame,
    /// Возобновление игры
    ResumeGame,
    /// Завершение игры
    FinishGame,
    /// Создание блока
    SpawnBlock,
    /// Перемещение блока
    MoveBlock,
    /// Вращение блока
    RotateBlock,
    /// Применение заклинания
    CastSpell,
    /// Обновление состояния игры
    GameState,
    /// Обновление состояния игрока
    PlayerState,
    /// Обновление состояния блока
    BlockState,
    /// Обновление состояния заклинания
    SpellState,
    /// Ошибка
    Error,
    /// Пинг
    Ping,
    /// Понг
    Pong,
}

/// Сообщение
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NetworkMessage {
    /// Тип сообщения
    pub message_type: MessageType,
    /// Идентификатор сообщения
    pub message_id: String,
    /// Идентификатор сессии
    pub session_id: Option<Uuid>,
    /// Данные сообщения
    pub data: serde_json::Value,
    /// Временная метка
    pub timestamp: i64,
}

impl NetworkMessage {
    /// Создает новое сообщение
    pub fn new(message_type: MessageType, data: serde_json::Value, session_id: Option<Uuid>) -> Self {
        Self {
            message_type,
            message_id: Uuid::new_v4().to_string(),
            session_id,
            data,
            timestamp: chrono::Utc::now().timestamp(),
        }
    }

    /// Создает сообщение об ошибке
    pub fn error(error_message: &str, session_id: Option<Uuid>) -> Self {
        let data = serde_json::json!({
            "error": error_message,
        });
        
        Self::new(MessageType::Error, data, session_id)
    }

    /// Создает сообщение пинга
    pub fn ping(session_id: Option<Uuid>) -> Self {
        Self::new(MessageType::Ping, serde_json::json!({}), session_id)
    }

    /// Создает сообщение понга
    pub fn pong(session_id: Option<Uuid>) -> Self {
        Self::new(MessageType::Pong, serde_json::json!({}), session_id)
    }
}

/// Клиентское соединение
#[derive(Debug)]
pub struct ClientConnection {
    /// Идентификатор соединения
    pub id: Uuid,
    /// Идентификатор сессии
    pub session_id: Option<Uuid>,
    /// Отправитель сообщений
    pub sender: mpsc::UnboundedSender<Result<Message, warp::Error>>,
    /// Время последней активности
    pub last_activity: std::sync::Mutex<chrono::DateTime<chrono::Utc>>,
}

impl ClientConnection {
    /// Создает новое клиентское соединение
    pub fn new(sender: mpsc::UnboundedSender<Result<Message, warp::Error>>) -> Self {
        Self {
            id: Uuid::new_v4(),
            session_id: None,
            sender,
            last_activity: std::sync::Mutex::new(chrono::Utc::now()),
        }
    }

    /// Обновляет время последней активности
    pub fn update_activity(&self) {
        let mut last_activity = self.last_activity.lock().unwrap();
        *last_activity = chrono::Utc::now();
    }

    /// Отправляет сообщение клиенту
    pub fn send_message(&self, message: NetworkMessage) -> Result<()> {
        let json = serde_json::to_string(&message)?;
        self.sender.send(Ok(Message::text(json)))
            .map_err(|e| anyhow::anyhow!("Failed to send message: {}", e))?;
        Ok(())
    }
}

/// Обработчик WebSocket
pub struct WebSocketHandler {
    /// Менеджер сессий
    session_manager: Arc<SessionManager>,
    /// Клиентские соединения
    connections: Arc<DashMap<Uuid, ClientConnection>>,
    /// Конфигурация сети
    config: NetworkConfig,
}

impl WebSocketHandler {
    /// Создает новый обработчик WebSocket
    pub fn new(session_manager: Arc<SessionManager>, config: NetworkConfig) -> Self {
        Self {
            session_manager,
            connections: Arc::new(DashMap::new()),
            config,
        }
    }

    /// Обрабатывает новое WebSocket соединение
    pub async fn handle_connection(&self, ws: WebSocket) {
        let (ws_sender, mut ws_receiver) = ws.split();
        
        // Создаем канал для отправки сообщений клиенту
        let (sender, receiver) = mpsc::unbounded_channel();
        
        // Создаем клиентское соединение
        let connection = ClientConnection::new(sender);
        let connection_id = connection.id;
        
        // Сохраняем соединение
        self.connections.insert(connection_id, connection);
        
        // Запускаем задачу для отправки сообщений клиенту
        tokio::task::spawn(Self::sender_task(receiver, ws_sender));
        
        // Отправляем приветственное сообщение
        if let Some(connection) = self.connections.get(&connection_id) {
            let welcome_message = NetworkMessage::new(
                MessageType::Auth,
                serde_json::json!({
                    "message": "Welcome to Tetris Towers Server",
                    "connection_id": connection_id.to_string(),
                }),
                None,
            );
            
            if let Err(e) = connection.send_message(welcome_message) {
                error!("Error sending welcome message: {}", e);
            }
        }
        
        // Обрабатываем входящие сообщения
        while let Some(result) = ws_receiver.next().await {
            match result {
                Ok(message) => {
                    // Обновляем время последней активности
                    if let Some(connection) = self.connections.get(&connection_id) {
                        connection.update_activity();
                    }
                    
                    // Обрабатываем сообщение
                    if message.is_text() {
                        if let Err(e) = self.handle_text_message(connection_id, message.to_str().unwrap_or_default()).await {
                            error!("Error handling text message: {}", e);
                            
                            // Отправляем сообщение об ошибке
                            if let Some(connection) = self.connections.get(&connection_id) {
                                let session_id = connection.session_id;
                                let error_message = NetworkMessage::error(&e.to_string(), session_id);
                                
                                if let Err(e) = connection.send_message(error_message) {
                                    error!("Error sending error message: {}", e);
                                }
                            }
                        }
                    } else if message.is_ping() {
                        // Отвечаем на пинг
                        if let Some(connection) = self.connections.get(&connection_id) {
                            let session_id = connection.session_id;
                            let pong_message = NetworkMessage::pong(session_id);
                            
                            if let Err(e) = connection.send_message(pong_message) {
                                error!("Error sending pong message: {}", e);
                            }
                        }
                    }
                },
                Err(e) => {
                    error!("WebSocket error: {}", e);
                    break;
                }
            }
        }
        
        // Соединение закрыто, удаляем его
        self.connections.remove(&connection_id);
        
        // Если соединение было аутентифицировано, обновляем сессию
        if let Some(connection) = self.connections.get(&connection_id) {
            if let Some(session_id) = connection.session_id {
                // Обновляем сессию
                if let Err(e) = self.session_manager.update_session_activity(session_id) {
                    error!("Error updating session activity: {}", e);
                }
            }
        }
        
        debug!("WebSocket connection closed: {}", connection_id);
    }

    /// Задача для отправки сообщений клиенту
    async fn sender_task(
        mut receiver: mpsc::UnboundedReceiver<Result<Message, warp::Error>>,
        mut ws_sender: futures::stream::SplitSink<WebSocket, Message>,
    ) -> Result<()> {
        while let Some(message) = receiver.recv().await {
            ws_sender.send(message?).await?;
        }
        Ok(())
    }

    /// Обрабатывает текстовое сообщение
    async fn handle_text_message(&self, connection_id: Uuid, text: &str) -> Result<()> {
        // Парсим сообщение
        let message: NetworkMessage = serde_json::from_str(text)
            .context("Failed to parse message")?;
        
        // Получаем соединение
        let connection = self.connections.get(&connection_id)
            .context("Connection not found")?;
        
        // Обрабатываем сообщение в зависимости от типа
        match message.message_type {
            MessageType::Auth => {
                // Аутентификация
                let data = &message.data;
                let user_name = data["user_name"].as_str()
                    .context("Missing user_name field")?;
                
                // Создаем сессию
                let session_id = self.session_manager.create_session(
                    user_name.to_string(),
                    crate::session::UserRole::Player,
                )?;
                
                // Обновляем соединение
                let mut connection = self.connections.get_mut(&connection_id)
                    .context("Connection not found")?;
                connection.session_id = Some(session_id);
                
                // Отправляем ответ
                let response = NetworkMessage::new(
                    MessageType::Auth,
                    serde_json::json!({
                        "success": true,
                        "session_id": session_id.to_string(),
                    }),
                    Some(session_id),
                );
                
                connection.send_message(response)?;
            },
            MessageType::CreateGame => {
                // Создание игры
                let session_id = connection.session_id
                    .context("Not authenticated")?;
                
                // Получаем данные из сообщения
                let data = &message.data;
                let game_name = data["game_name"].as_str()
                    .context("Missing game_name field")?;
                let game_type_str = data["game_type"].as_str()
                    .context("Missing game_type field")?;
                let difficulty_str = data["difficulty"].as_str()
                    .context("Missing difficulty field")?;
                
                // Преобразуем строки в перечисления
                let game_type = match game_type_str {
                    "race" => GameType::Race,
                    "survival" => GameType::Survival,
                    "puzzle" => GameType::Puzzle,
                    _ => return Err(anyhow::anyhow!("Invalid game_type")),
                };
                
                let difficulty = match difficulty_str {
                    "easy" => DifficultyLevel::Easy,
                    "medium" => DifficultyLevel::Medium,
                    "hard" => DifficultyLevel::Hard,
                    "expert" => DifficultyLevel::Expert,
                    _ => return Err(anyhow::anyhow!("Invalid difficulty")),
                };
                
                // Получаем сессию
                let session = self.session_manager.get_session(session_id)?;
                
                // Создаем игру
                let game_id = self.session_manager.game_manager().create_game(
                    game_name.to_string(),
                    game_type,
                    difficulty,
                ).await?;
                
                // Отправляем ответ
                let response = NetworkMessage::new(
                    MessageType::CreateGame,
                    serde_json::json!({
                        "success": true,
                        "game_id": game_id.to_string(),
                    }),
                    Some(session_id),
                );
                
                connection.send_message(response)?;
            },
            MessageType::JoinGame => {
                // Присоединение к игре
                let session_id = connection.session_id
                    .context("Not authenticated")?;
                
                // Получаем данные из сообщения
                let data = &message.data;
                let game_id_str = data["game_id"].as_str()
                    .context("Missing game_id field")?;
                
                // Преобразуем строку в UUID
                let game_id = Uuid::parse_str(game_id_str)
                    .context("Invalid game_id")?;
                
                // Присоединяемся к игре
                self.session_manager.join_game(session_id, game_id).await?;
                
                // Отправляем ответ
                let response = NetworkMessage::new(
                    MessageType::JoinGame,
                    serde_json::json!({
                        "success": true,
                        "game_id": game_id.to_string(),
                    }),
                    Some(session_id),
                );
                
                connection.send_message(response)?;
                
                // Отправляем обновление состояния игры всем игрокам
                self.broadcast_game_state(game_id).await?;
            },
            MessageType::LeaveGame => {
                // Покидание игры
                let session_id = connection.session_id
                    .context("Not authenticated")?;
                
                // Получаем сессию
                let session = self.session_manager.get_session(session_id)?;
                
                // Получаем ID игры
                let game_id = session.game_id
                    .context("Not in a game")?;
                
                // Покидаем игру
                self.session_manager.leave_game(session_id)?;
                
                // Отправляем ответ
                let response = NetworkMessage::new(
                    MessageType::LeaveGame,
                    serde_json::json!({
                        "success": true,
                    }),
                    Some(session_id),
                );
                
                connection.send_message(response)?;
                
                // Отправляем обновление состояния игры всем игрокам
                self.broadcast_game_state(game_id).await?;
            },
            MessageType::StartGame => {
                // Запуск игры
                let session_id = connection.session_id
                    .context("Not authenticated")?;
                
                // Получаем сессию
                let session = self.session_manager.get_session(session_id)?;
                
                // Получаем ID игры
                let game_id = session.game_id
                    .context("Not in a game")?;
                
                // Запускаем игру
                self.session_manager.game_manager().start_game(game_id)?;
                
                // Отправляем ответ
                let response = NetworkMessage::new(
                    MessageType::StartGame,
                    serde_json::json!({
                        "success": true,
                    }),
                    Some(session_id),
                );
                
                connection.send_message(response)?;
                
                // Отправляем обновление состояния игры всем игрокам
                self.broadcast_game_state(game_id).await?;
            },
            MessageType::PauseGame => {
                // Пауза игры
                let session_id = connection.session_id
                    .context("Not authenticated")?;
                
                // Получаем сессию
                let session = self.session_manager.get_session(session_id)?;
                
                // Получаем ID игры
                let game_id = session.game_id
                    .context("Not in a game")?;
                
                // Приостанавливаем игру
                self.session_manager.game_manager().pause_game(game_id)?;
                
                // Отправляем ответ
                let response = NetworkMessage::new(
                    MessageType::PauseGame,
                    serde_json::json!({
                        "success": true,
                    }),
                    Some(session_id),
                );
                
                connection.send_message(response)?;
                
                // Отправляем обновление состояния игры всем игрокам
                self.broadcast_game_state(game_id).await?;
            },
            MessageType::ResumeGame => {
                // Возобновление игры
                let session_id = connection.session_id
                    .context("Not authenticated")?;
                
                // Получаем сессию
                let session = self.session_manager.get_session(session_id)?;
                
                // Получаем ID игры
                let game_id = session.game_id
                    .context("Not in a game")?;
                
                // Возобновляем игру
                self.session_manager.game_manager().resume_game(game_id)?;
                
                // Отправляем ответ
                let response = NetworkMessage::new(
                    MessageType::ResumeGame,
                    serde_json::json!({
                        "success": true,
                    }),
                    Some(session_id),
                );
                
                connection.send_message(response)?;
                
                // Отправляем обновление состояния игры всем игрокам
                self.broadcast_game_state(game_id).await?;
            },
            MessageType::SpawnBlock => {
                // Создание блока
                let session_id = connection.session_id
                    .context("Not authenticated")?;
                
                // Получаем сессию
                let session = self.session_manager.get_session(session_id)?;
                
                // Получаем ID игры
                let game_id = session.game_id
                    .context("Not in a game")?;
                
                // Получаем ID пользователя
                let user_id = session.user.id;
                
                // Создаем блок
                let block_id = self.session_manager.game_manager().spawn_tetris_block(game_id, user_id).await?;
                
                // Отправляем ответ
                let response = NetworkMessage::new(
                    MessageType::SpawnBlock,
                    serde_json::json!({
                        "success": true,
                        "block_id": block_id,
                    }),
                    Some(session_id),
                );
                
                connection.send_message(response)?;
                
                // Отправляем обновление состояния игры всем игрокам
                self.broadcast_game_state(game_id).await?;
            },
            MessageType::MoveBlock => {
                // Перемещение блока
                let session_id = connection.session_id
                    .context("Not authenticated")?;
                
                // Получаем данные из сообщения
                let data = &message.data;
                let direction_x = data["direction_x"].as_f64()
                    .context("Missing direction_x field")? as f32;
                let direction_y = data["direction_y"].as_f64()
                    .context("Missing direction_y field")? as f32;
                
                // Получаем сессию
                let session = self.session_manager.get_session(session_id)?;
                
                // Получаем ID игры
                let game_id = session.game_id
                    .context("Not in a game")?;
                
                // Перемещаем блок
                self.session_manager.game_manager().move_current_block(game_id, (direction_x, direction_y)).await?;
                
                // Отправляем ответ
                let response = NetworkMessage::new(
                    MessageType::MoveBlock,
                    serde_json::json!({
                        "success": true,
                    }),
                    Some(session_id),
                );
                
                connection.send_message(response)?;
                
                // Отправляем обновление состояния игры всем игрокам
                self.broadcast_game_state(game_id).await?;
            },
            MessageType::RotateBlock => {
                // Вращение блока
                let session_id = connection.session_id
                    .context("Not authenticated")?;
                
                // Получаем данные из сообщения
                let data = &message.data;
                let angle_delta = data["angle_delta"].as_f64()
                    .context("Missing angle_delta field")? as f32;
                
                // Получаем сессию
                let session = self.session_manager.get_session(session_id)?;
                
                // Получаем ID игры
                let game_id = session.game_id
                    .context("Not in a game")?;
                
                // Вращаем блок
                self.session_manager.game_manager().rotate_current_block(game_id, angle_delta).await?;
                
                // Отправляем ответ
                let response = NetworkMessage::new(
                    MessageType::RotateBlock,
                    serde_json::json!({
                        "success": true,
                    }),
                    Some(session_id),
                );
                
                connection.send_message(response)?;
                
                // Отправляем обновление состояния игры всем игрокам
                self.broadcast_game_state(game_id).await?;
            },
            MessageType::CastSpell => {
                // Применение заклинания
                let session_id = connection.session_id
                    .context("Not authenticated")?;
                
                // Получаем данные из сообщения
                let data = &message.data;
                let spell_id = data["spell_id"].as_str()
                    .context("Missing spell_id field")?;
                let target_id_str = data["target_id"].as_str();
                
                // Преобразуем строку в UUID, если она есть
                let target_id = if let Some(id_str) = target_id_str {
                    Some(Uuid::parse_str(id_str).context("Invalid target_id")?)
                } else {
                    None
                };
                
                // Получаем сессию
                let session = self.session_manager.get_session(session_id)?;
                
                // Получаем ID игры
                let game_id = session.game_id
                    .context("Not in a game")?;
                
                // Получаем ID пользователя
                let user_id = session.user.id;
                
                // Применяем заклинание
                self.session_manager.game_manager().cast_spell(game_id, user_id, spell_id, target_id)?;
                
                // Отправляем ответ
                let response = NetworkMessage::new(
                    MessageType::CastSpell,
                    serde_json::json!({
                        "success": true,
                    }),
                    Some(session_id),
                );
                
                connection.send_message(response)?;
                
                // Отправляем обновление состояния игры всем игрокам
                self.broadcast_game_state(game_id).await?;
            },
            MessageType::Ping => {
                // Пинг
                let session_id = connection.session_id;
                
                // Отправляем понг
                let response = NetworkMessage::pong(session_id);
                connection.send_message(response)?;
            },
            _ => {
                // Неизвестный тип сообщения
                return Err(anyhow::anyhow!("Unknown message type"));
            }
        }
        
        Ok(())
    }

    /// Отправляет обновление состояния игры всем игрокам
    async fn broadcast_game_state(&self, game_id: Uuid) -> Result<()> {
        // Получаем игру
        let game = self.session_manager.game_manager().get_game(game_id)?;
        
        // Сериализуем игру
        let game_json = serde_json::to_value(&game)?;
        
        // Создаем сообщение
        let message = NetworkMessage::new(
            MessageType::GameState,
            serde_json::json!({
                "game": game_json,
            }),
            None,
        );
        
        // Отправляем сообщение всем игрокам в игре
        for player_id in game.players.keys() {
            // Находим все соединения с этим игроком
            for connection in self.connections.iter() {
                if let Some(session_id) = connection.session_id {
                    // Получаем сессию
                    if let Ok(session) = self.session_manager.get_session(session_id) {
                        // Проверяем, принадлежит ли сессия этому игроку
                        if session.user.id == *player_id {
                            // Отправляем сообщение
                            let mut message_copy = message.clone();
                            message_copy.session_id = Some(session_id);
                            
                            if let Err(e) = connection.send_message(message_copy) {
                                error!("Error sending game state update: {}", e);
                            }
                        }
                    }
                }
            }
        }
        
        Ok(())
    }

    /// Получает количество активных соединений
    pub fn connection_count(&self) -> usize {
        self.connections.len()
    }

    /// Получает список активных соединений
    pub fn get_connections(&self) -> Vec<Uuid> {
        self.connections.iter()
            .map(|c| c.id)
            .collect()
    }

    /// Отправляет сообщение всем клиентам
    pub fn broadcast_message(&self, message: NetworkMessage) -> Result<()> {
        for connection in self.connections.iter() {
            if let Err(e) = connection.send_message(message.clone()) {
                error!("Error broadcasting message: {}", e);
            }
        }
        
        Ok(())
    }

    /// Отправляет сообщение конкретному клиенту
    pub fn send_message_to_client(&self, connection_id: Uuid, message: NetworkMessage) -> Result<()> {
        if let Some(connection) = self.connections.get(&connection_id) {
            connection.send_message(message)?;
            Ok(())
        } else {
            Err(anyhow::anyhow!("Connection not found"))
        }
    }

    /// Отправляет сообщение конкретной сессии
    pub fn send_message_to_session(&self, session_id: Uuid, message: NetworkMessage) -> Result<()> {
        let mut sent = false;
        
        for connection in self.connections.iter() {
            if connection.session_id == Some(session_id) {
                if let Err(e) = connection.send_message(message.clone()) {
                    error!("Error sending message to session: {}", e);
                } else {
                    sent = true;
                }
            }
        }
        
        if sent {
            Ok(())
        } else {
            Err(anyhow::anyhow!("Session not found or no active connections"))
        }
    }
}

unsafe impl Send for WebSocketHandler {}
unsafe impl Sync for WebSocketHandler {}

/// Сетевой менеджер
pub struct NetworkManager {
    /// Конфигурация сетевого менеджера
    config: NetworkConfig,
    /// Менеджер сессий
    session_manager: Arc<SessionManager>,
    /// Обработчик WebSocket
    ws_handler: Arc<WebSocketHandler>,
    /// Флаг работы менеджера
    running: Arc<tokio::sync::RwLock<bool>>,
    /// Задача сервера
    server_task: Arc<tokio::sync::RwLock<Option<tokio::task::JoinHandle<()>>>>,
}

impl NetworkManager {
    /// Создает новый экземпляр сетевого менеджера
    pub fn new(config: &NetworkConfig, session_manager: Arc<SessionManager>) -> Result<Self> {
        let ws_handler = Arc::new(WebSocketHandler::new(
            session_manager.clone(),
            config.clone(),
        ));
        
        Ok(Self {
            config: config.clone(),
            session_manager,
            ws_handler,
            running: Arc::new(tokio::sync::RwLock::new(false)),
            server_task: Arc::new(tokio::sync::RwLock::new(None)),
        })
    }

    /// Запускает сетевой менеджер
    pub async fn start(&self) -> Result<()> {
        info!("Starting Network Manager on {}:{}", self.config.host, self.config.port);
        
        // Устанавливаем флаг работы
        let mut running = self.running.write().await;
        *running = true;
        drop(running);
        
        // Создаем маршруты
        let ws_route = self.create_ws_route();
        let health_route = self.create_health_route();
        let api_route = self.create_api_route();
        
        // Объединяем маршруты
        let routes = ws_route
            .or(health_route)
            .or(api_route);
        
        // Добавляем CORS, если включено
        let routes = if self.config.enable_cors {
            let cors = warp::cors()
                .allow_any_origin()
                .allow_methods(vec!["GET", "POST", "PUT", "DELETE", "OPTIONS"])
                .allow_headers(vec!["Content-Type", "Authorization"])
                .max_age(3600);
            
            routes.with(cors)
        } else {
            routes
        };
        
        // Создаем адрес для прослушивания
        let addr = format!("{}:{}", self.config.host, self.config.port)
            .parse::<std::net::SocketAddr>()
            .context("Invalid host or port")?;
        
        // Запускаем сервер
        let server = warp::serve(routes);
        
        // Запускаем сервер с SSL или без
        let server_task = if self.config.enable_ssl {
            // Загружаем сертификат и ключ
            let cert_path = std::path::Path::new(&self.config.ssl_cert_path);
            let key_path = std::path::Path::new(&self.config.ssl_key_path);
            
            if !cert_path.exists() || !key_path.exists() {
                return Err(anyhow::anyhow!("SSL certificate or key not found"));
            }
            
            let cert = tokio::fs::read(cert_path).await
                .context("Failed to read SSL certificate")?;
            let key = tokio::fs::read(key_path).await
                .context("Failed to read SSL key")?;
            
            // Создаем TLS конфигурацию
            // Примечание: в реальной реализации здесь был бы код для настройки TLS
            
            // Запускаем сервер с TLS
            tokio::spawn(async move {
                // В реальной реализации здесь был бы код для запуска сервера с TLS
                server.run(addr).await;
            })
        } else {
            // Запускаем сервер без TLS
            tokio::spawn(async move {
                server.run(addr).await;
            })
        };
        
        // Сохраняем задачу сервера
        let mut server_task_guard = self.server_task.write().await;
        *server_task_guard = Some(server_task);
        
        info!("Network Manager started successfully");
        Ok(())
    }

    /// Останавливает сетевой менеджер
    pub async fn stop(&self) -> Result<()> {
        info!("Stopping Network Manager");
        
        // Сбрасываем флаг работы
        let mut running = self.running.write().await;
        *running = false;
        drop(running);
        
        // Ожидаем завершения задачи сервера
        let mut server_task_guard = self.server_task.write().await;
        if let Some(task) = server_task_guard.take() {
            // Ожидаем завершения задачи
            // Примечание: в реальной реализации здесь был бы код для корректной остановки сервера
            tokio::task::spawn(async move {
                if let Err(e) = task.await {
                    error!("Error joining server task: {}", e);
                }
            });
        }
        
        info!("Network Manager stopped successfully");
        Ok(())
    }

    /// Создает маршрут для WebSocket
    fn create_ws_route(&self) -> impl Filter<Extract = impl Reply, Error = Rejection> + Clone {
        let session_manager = self.session_manager.clone();
        let config = self.config.clone();

        warp::path("ws")
            .and(warp::ws())
            .map(move |ws: warp::ws::Ws| {
                let session_manager = session_manager.clone();
                let config = config.clone();
                ws.on_upgrade(move |websocket| {
                    let handler = WebSocketHandler::new(session_manager, config);
                    Box::pin(handler.handle_connection(websocket))
                })
            })
    }

    /// Создает маршрут для проверки работоспособности
    fn create_health_route(&self) -> impl Filter<Extract = impl Reply, Error = Rejection> + Clone {
        warp::path("health")
            .map(|| {
                warp::reply::json(&serde_json::json!({
                    "status": "ok",
                    "version": crate::SERVER_VERSION,
                }))
            })
    }

    /// Создает маршрут для API
    fn create_api_route(&self) -> impl Filter<Extract = impl Reply, Error = Rejection> + Clone {
        let session_manager = self.session_manager.clone();
        let config = self.config.clone();

        let ws_route = self.create_ws_route();
        let health_route = self.create_health_route();

        let routes = ws_route.or(health_route);

        if config.enable_cors {
            let cors = warp::cors()
                .allow_any_origin()
                .allow_methods(vec!["GET", "POST", "PUT", "DELETE", "OPTIONS"])
                .allow_headers(vec!["Content-Type", "Authorization"])
                .max_age(3600);

            routes.with(cors)
        } else {
            routes.with(warp::cors().allow_any_origin())
        }
    }

    /// Проверяет, работает ли сетевой менеджер
    pub fn is_running(&self) -> bool {
        *self.running.blocking_read()
    }

    /// Получает обработчик WebSocket
    pub fn ws_handler(&self) -> Arc<WebSocketHandler> {
        self.ws_handler.clone()
    }
}

impl Drop for NetworkManager {
    fn drop(&mut self) {
        // Остановка менеджера при уничтожении
        if *self.running.blocking_read() {
            tokio::runtime::Runtime::new()
                .unwrap()
                .block_on(async {
                    if let Err(e) = self.stop().await {
                        error!("Error stopping Network Manager during drop: {}", e);
                    }
                });
        }
    }
}

impl SessionManager {
    /// Получает менеджер игр
    pub fn game_manager(&self) -> &Arc<GameManager> {
        &self.game_manager
    }
}
