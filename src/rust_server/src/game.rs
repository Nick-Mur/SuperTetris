use std::sync::Arc;
use std::collections::HashMap;
use tokio::sync::RwLock;
use uuid::Uuid;
use serde::{Serialize, Deserialize};
use anyhow::{Result, Context};
use log::{info, error, debug, warn};
use chrono::{DateTime, Utc};
use dashmap::DashMap;
use crate::physics::PhysicsManager;
use crate::ServerError;
use std::ops::Deref;

/// Конфигурация игрового менеджера
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GameConfig {
    /// Максимальное количество игроков в одной игре
    pub max_players: usize,
    /// Высота игрового поля
    pub field_height: usize,
    /// Ширина игрового поля
    pub field_width: usize,
    /// Интервал обновления игры (в миллисекундах)
    pub update_interval_ms: u64,
    /// Включить режим отладки
    pub debug_mode: bool,
    /// Путь к файлам ресурсов
    pub resources_path: String,
}

impl Default for GameConfig {
    fn default() -> Self {
        Self {
            max_players: 4,
            field_height: 20,
            field_width: 10,
            update_interval_ms: 16,
            debug_mode: false,
            resources_path: "resources".to_string(),
        }
    }
}

/// Тип игры
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum GameType {
    /// Режим гонки (кто быстрее построит башню определенной высоты)
    Race,
    /// Режим выживания (кто дольше продержится)
    Survival,
    /// Режим головоломки (построить конструкцию по шаблону)
    Puzzle,
}

/// Состояние игры
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum GameState {
    /// Ожидание игроков
    Waiting,
    /// Игра запущена
    Running,
    /// Игра приостановлена
    Paused,
    /// Игра завершена
    Finished,
}

/// Уровень сложности
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum DifficultyLevel {
    Easy,
    Medium,
    Hard,
    Expert,
}

/// Тип заклинания
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum SpellType {
    /// Светлое заклинание (помогает игроку)
    Light,
    /// Темное заклинание (мешает противникам)
    Dark,
}

/// Заклинание
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Spell {
    /// Идентификатор заклинания
    pub id: String,
    /// Название заклинания
    pub name: String,
    /// Тип заклинания
    pub spell_type: SpellType,
    /// Описание заклинания
    pub description: String,
    /// Длительность эффекта (в секундах)
    pub duration: f32,
    /// Стоимость заклинания (в очках)
    pub cost: u32,
}

/// Игрок
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Player {
    /// Идентификатор игрока
    pub id: Uuid,
    /// Имя игрока
    pub name: String,
    /// Счет игрока
    pub score: u32,
    /// Высота башни
    pub tower_height: f32,
    /// Количество уложенных блоков
    pub blocks_placed: u32,
    /// Количество разрушенных блоков
    pub blocks_destroyed: u32,
    /// Доступные заклинания
    pub available_spells: Vec<Spell>,
    /// Активные заклинания
    pub active_spells: Vec<(Spell, DateTime<Utc>)>,
    /// Идентификаторы блоков игрока
    pub block_ids: Vec<i32>,
}

/// Игра
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Game {
    /// Идентификатор игры
    pub id: Uuid,
    /// Название игры
    pub name: String,
    /// Тип игры
    pub game_type: GameType,
    /// Состояние игры
    pub state: GameState,
    /// Уровень сложности
    pub difficulty: DifficultyLevel,
    /// Время создания игры
    pub created_at: DateTime<Utc>,
    /// Время начала игры
    pub started_at: Option<DateTime<Utc>>,
    /// Время окончания игры
    pub finished_at: Option<DateTime<Utc>>,
    /// Игроки
    pub players: HashMap<Uuid, Player>,
    /// Максимальное количество игроков
    pub max_players: usize,
    /// Высота игрового поля
    pub field_height: usize,
    /// Ширина игрового поля
    pub field_width: usize,
    /// Идентификатор победителя
    pub winner_id: Option<Uuid>,
    /// Идентификаторы блоков пола
    pub floor_block_ids: Vec<i32>,
    /// Идентификатор текущего активного блока
    pub current_block_id: Option<i32>,
    /// Следующий тип блока
    pub next_block_type: Option<crate::physics::BlockType>,
}

impl Game {
    /// Создает новую игру
    pub fn new(
        id: Uuid,
        name: String,
        game_type: GameType,
        difficulty: DifficultyLevel,
        max_players: usize,
        field_height: usize,
        field_width: usize,
    ) -> Self {
        Self {
            id,
            name,
            game_type,
            state: GameState::Waiting,
            difficulty,
            created_at: Utc::now(),
            started_at: None,
            finished_at: None,
            players: HashMap::new(),
            max_players,
            field_height,
            field_width,
            winner_id: None,
            floor_block_ids: Vec::new(),
            current_block_id: None,
            next_block_type: None,
        }
    }

    /// Добавляет игрока в игру
    pub fn add_player(&mut self, player: Player) -> Result<()> {
        if self.players.len() >= self.max_players {
            return Err(anyhow::anyhow!("Game is full"));
        }

        if self.state != GameState::Waiting {
            return Err(anyhow::anyhow!("Game already started"));
        }

        self.players.insert(player.id, player);
        Ok(())
    }

    /// Удаляет игрока из игры
    pub fn remove_player(&mut self, player_id: Uuid) -> Result<()> {
        if !self.players.contains_key(&player_id) {
            return Err(anyhow::anyhow!("Player not found"));
        }

        self.players.remove(&player_id);
        Ok(())
    }

    /// Запускает игру
    pub fn start(&mut self) -> Result<()> {
        if self.state != GameState::Waiting {
            return Err(anyhow::anyhow!("Game already started"));
        }

        if self.players.is_empty() {
            return Err(anyhow::anyhow!("No players in the game"));
        }

        self.state = GameState::Running;
        self.started_at = Some(Utc::now());
        Ok(())
    }

    /// Приостанавливает игру
    pub fn pause(&mut self) -> Result<()> {
        if self.state != GameState::Running {
            return Err(anyhow::anyhow!("Game not running"));
        }

        self.state = GameState::Paused;
        Ok(())
    }

    /// Возобновляет игру
    pub fn resume(&mut self) -> Result<()> {
        if self.state != GameState::Paused {
            return Err(anyhow::anyhow!("Game not paused"));
        }

        self.state = GameState::Running;
        Ok(())
    }

    /// Завершает игру
    pub fn finish(&mut self, winner_id: Option<Uuid>) -> Result<()> {
        if self.state == GameState::Finished {
            return Err(anyhow::anyhow!("Game already finished"));
        }

        self.state = GameState::Finished;
        self.finished_at = Some(Utc::now());
        self.winner_id = winner_id;
        Ok(())
    }

    /// Проверяет, может ли игрок присоединиться к игре
    pub fn can_join(&self) -> bool {
        self.state == GameState::Waiting && self.players.len() < self.max_players
    }

    /// Проверяет, готова ли игра к запуску
    pub fn is_ready_to_start(&self) -> bool {
        self.state == GameState::Waiting && !self.players.is_empty()
    }

    /// Проверяет, активна ли игра
    pub fn is_active(&self) -> bool {
        self.state == GameState::Running || self.state == GameState::Paused
    }

    /// Получает игрока по ID
    pub fn get_player(&self, player_id: Uuid) -> Option<&Player> {
        self.players.get(&player_id)
    }

    /// Получает игрока по ID (изменяемая ссылка)
    pub fn get_player_mut(&mut self, player_id: Uuid) -> Option<&mut Player> {
        self.players.get_mut(&player_id)
    }

    /// Обновляет счет игрока
    pub fn update_player_score(&mut self, player_id: Uuid, score: u32) -> Result<()> {
        let player = self.players.get_mut(&player_id).context("Player not found")?;
        player.score = score;
        Ok(())
    }

    /// Обновляет высоту башни игрока
    pub fn update_player_tower_height(&mut self, player_id: Uuid, height: f32) -> Result<()> {
        let player = self.players.get_mut(&player_id).context("Player not found")?;
        player.tower_height = height;
        Ok(())
    }

    /// Добавляет блок игроку
    pub fn add_player_block(&mut self, player_id: Uuid, block_id: i32) -> Result<()> {
        let player = self.players.get_mut(&player_id).context("Player not found")?;
        player.block_ids.push(block_id);
        player.blocks_placed += 1;
        Ok(())
    }

    /// Удаляет блок у игрока
    pub fn remove_player_block(&mut self, player_id: Uuid, block_id: i32) -> Result<()> {
        let player = self.players.get_mut(&player_id).context("Player not found")?;
        if let Some(index) = player.block_ids.iter().position(|&id| id == block_id) {
            player.block_ids.remove(index);
            player.blocks_destroyed += 1;
            Ok(())
        } else {
            Err(anyhow::anyhow!("Block not found"))
        }
    }

    /// Применяет заклинание
    pub fn cast_spell(&mut self, caster_id: Uuid, spell_id: &str, target_id: Option<Uuid>) -> Result<()> {
        let caster = self.players.get_mut(&caster_id).context("Caster not found")?;
        
        // Находим заклинание
        let spell_index = caster.available_spells.iter().position(|s| s.id == spell_id)
            .context("Spell not found")?;
        
        let spell = caster.available_spells.remove(spell_index);
        
        // Проверяем, достаточно ли очков
        if caster.score < spell.cost {
            // Возвращаем заклинание обратно
            caster.available_spells.push(spell);
            return Err(anyhow::anyhow!("Not enough score to cast spell"));
        }
        
        // Снимаем очки
        caster.score -= spell.cost;
        
        // Добавляем заклинание в активные
        let expires_at = Utc::now() + chrono::Duration::seconds(spell.duration as i64);
        caster.active_spells.push((spell.clone(), expires_at));
        
        // Если заклинание направлено на другого игрока
        if let Some(target_id) = target_id {
            if target_id == caster_id {
                return Err(anyhow::anyhow!("Cannot target self with this spell"));
            }
            
            let target = self.players.get_mut(&target_id).context("Target not found")?;
            
            // Применяем эффект заклинания к цели
            if spell.spell_type == SpellType::Dark {
                // Темное заклинание (негативный эффект)
                // Логика применения негативного эффекта
            }
        }
        
        Ok(())
    }

    /// Обновляет состояние активных заклинаний
    pub fn update_spells(&mut self) {
        let now = Utc::now();
        
        for player in self.players.values_mut() {
            // Удаляем истекшие заклинания
            player.active_spells.retain(|(_, expires_at)| *expires_at > now);
        }
    }
}

/// Менеджер игр
pub struct GameManager {
    /// Конфигурация игрового менеджера
    config: GameConfig,
    /// Менеджер физики
    physics_manager: Arc<PhysicsManager>,
    /// Хранилище игр
    games: Arc<DashMap<Uuid, Game>>,
    /// Флаг работы менеджера
    running: Arc<tokio::sync::RwLock<bool>>,
    /// Задача обновления игр
    update_task: Arc<tokio::sync::RwLock<Option<tokio::task::JoinHandle<()>>>>,
}

impl GameManager {
    /// Создает новый экземпляр менеджера игр
    pub fn new(config: &GameConfig, physics_manager: Arc<PhysicsManager>) -> Result<Self> {
        Ok(Self {
            config: config.clone(),
            physics_manager,
            games: Arc::new(DashMap::new()),
            running: Arc::new(tokio::sync::RwLock::new(false)),
            update_task: Arc::new(tokio::sync::RwLock::new(None)),
        })
    }

    /// Запускает менеджер игр
    pub fn start(&self) -> Result<()> {
        info!("Starting Game Manager");
        
        // Устанавливаем флаг работы
        let mut running = self.running.write().await;
        *running = true;
        drop(running);
        
        // Запускаем задачу обновления игр
        let games = self.games.clone();
        let physics_manager = self.physics_manager.clone();
        let running = self.running.clone();
        let update_interval = self.config.update_interval_ms;
        
        let update_task = tokio::spawn(async move {
            while *running.read().await {
                // Обновляем все активные игры
                for mut game_ref in games.iter_mut() {
                    let game = &mut *game_ref;
                    
                    if game.state == GameState::Running {
                        // Обновляем заклинания
                        game.update_spells();
                        
                        // Обновляем физику для текущего блока
                        if let Some(block_id) = game.current_block_id {
                            // Получаем позицию блока
                            if let Ok((x, y)) = physics_manager.get_block_position(block_id).await {
                                // Проверяем коллизии с другими блоками
                                for player in game.players.values() {
                                    for &player_block_id in &player.block_ids {
                                        if player_block_id != block_id {
                                            if let Ok(collision) = physics_manager.check_collision(block_id, player_block_id).await {
                                                if collision {
                                                    // Обработка коллизии
                                                    debug!("Collision detected between blocks {} and {}", block_id, player_block_id);
                                                }
                                            }
                                        }
                                    }
                                }
                                
                                // Проверяем коллизии с полом
                                for &floor_block_id in &game.floor_block_ids {
                                    if let Ok(collision) = physics_manager.check_collision(block_id, floor_block_id).await {
                                        if collision {
                                            // Обработка коллизии с полом
                                            debug!("Collision detected with floor block {}", floor_block_id);
                                        }
                                    }
                                }
                            }
                        }
                        
                        // Проверяем условия завершения игры
                        match game.game_type {
                            GameType::Race => {
                                // Проверяем, достиг ли кто-то из игроков нужной высоты
                                for (player_id, player) in &game.players {
                                    if player.tower_height >= game.field_height as f32 {
                                        // Игрок победил
                                        if let Err(e) = game.finish(Some(*player_id)) {
                                            error!("Error finishing game: {}", e);
                                        }
                                        break;
                                    }
                                }
                            },
                            GameType::Survival => {
                                // Проверяем, остался ли только один игрок
                                let active_players: Vec<_> = game.players.iter()
                                    .filter(|(_, p)| p.tower_height > 0.0)
                                    .collect();
                                
                                if active_players.len() == 1 && game.players.len() > 1 {
                                    // Последний оставшийся игрок победил
                                    let winner_id = *active_players[0].0;
                                    if let Err(e) = game.finish(Some(winner_id)) {
                                        error!("Error finishing game: {}", e);
                                    }
                                }
                            },
                            GameType::Puzzle => {
                                // Проверка выполнения условий головоломки
                                // (в реальной реализации здесь была бы более сложная логика)
                            },
                        }
                    }
                }
                
                // Пауза перед следующим обновлением
                tokio::time::sleep(tokio::time::Duration::from_millis(update_interval)).await;
            }
        });
        
        // Сохраняем задачу обновления
        let mut update_task_guard = self.update_task.write().await;
        *update_task_guard = Some(update_task);
        
        info!("Game Manager started successfully");
        Ok(())
    }

    /// Останавливает менеджер игр
    pub fn stop(&self) -> Result<()> {
        info!("Stopping Game Manager");
        
        // Сбрасываем флаг работы
        let mut running = self.running.write().await;
        *running = false;
        drop(running);
        
        // Ожидаем завершения задачи обновления
        let mut update_task_guard = self.update_task.write().await;
        if let Some(task) = update_task_guard.take() {
            // Ожидаем завершения задачи
            tokio::task::spawn(async move {
                if let Err(e) = task.await {
                    error!("Error joining update task: {}", e);
                }
            });
        }
        
        info!("Game Manager stopped successfully");
        Ok(())
    }

    /// Создает новую игру
    pub async fn create_game(
        &self,
        name: String,
        game_type: GameType,
        difficulty: DifficultyLevel,
    ) -> Result<Uuid> {
        let game_id = Uuid::new_v4();
        
        let game = Game::new(
            game_id,
            name,
            game_type,
            difficulty,
            self.config.max_players,
            self.config.field_height,
            self.config.field_width,
        );
        
        // Создаем пол для игры
        let floor_width = self.config.field_width as f32 * 1.5;
        let floor_height = 1.0;
        let floor_position = (0.0, -10.0);
        
        let floor_block_id = self.physics_manager.create_block(
            floor_position,
            (floor_width, floor_height),
            0.0,
            None,
            true, // статический блок
        ).await?;
        
        // Сохраняем ID блока пола
        let mut game_mut = game;
        game_mut.floor_block_ids.push(floor_block_id);
        
        // Сохраняем игру
        self.games.insert(game_id, game_mut);
        
        Ok(game_id)
    }

    /// Удаляет игру
    pub fn delete_game(&self, game_id: Uuid) -> Result<()> {
        // Проверяем, существует ли игра
        if !self.games.contains_key(&game_id) {
            return Err(anyhow::anyhow!("Game not found"));
        }
        
        // Удаляем все блоки игры из физического движка
        let game = self.games.get(&game_id).context("Game not found")?;
        
        // Удаляем блоки пола
        for &block_id in &game.floor_block_ids {
            if let Err(e) = self.physics_manager.remove_block(block_id).await {
                warn!("Error removing floor block {}: {}", block_id, e);
            }
        }
        
        // Удаляем блоки игроков
        for player in game.players.values() {
            for &block_id in &player.block_ids {
                if let Err(e) = self.physics_manager.remove_block(block_id).await {
                    warn!("Error removing player block {}: {}", block_id, e);
                }
            }
        }
        
        // Удаляем текущий активный блок
        if let Some(block_id) = game.current_block_id {
            if let Err(e) = self.physics_manager.remove_block(block_id).await {
                warn!("Error removing current block {}: {}", block_id, e);
            }
        }
        
        // Удаляем игру из хранилища
        self.games.remove(&game_id);
        
        Ok(())
    }

    /// Получает игру по ID
    pub fn get_game(&self, game_id: Uuid) -> Result<Game> {
        self.games.get(&game_id)
            .map(|g| g.clone())
            .context("Game not found")
    }

    /// Получает список всех игр
    pub fn get_all_games(&self) -> Vec<Game> {
        self.games.iter()
            .map(|g| g.clone())
            .collect()
    }

    /// Получает список доступных для присоединения игр
    pub fn get_available_games(&self) -> Vec<Game> {
        self.games.iter()
            .filter(|g| g.can_join())
            .map(|g| g.clone())
            .collect()
    }

    /// Добавляет игрока в игру
    pub async fn add_player_to_game(&self, game_id: Uuid, player_name: String) -> Result<Uuid> {
        // Проверяем, существует ли игра
        let mut game = self.games.get_mut(&game_id).context("Game not found")?;
        
        // Проверяем, можно ли присоединиться к игре
        if !game.can_join() {
            return Err(anyhow::anyhow!("Cannot join this game"));
        }
        
        // Создаем игрока
        let player_id = Uuid::new_v4();
        let player = Player {
            id: player_id,
            name: player_name,
            score: 0,
            tower_height: 0.0,
            blocks_placed: 0,
            blocks_destroyed: 0,
            available_spells: Vec::new(),
            active_spells: Vec::new(),
            block_ids: Vec::new(),
        };
        
        // Добавляем игрока в игру
        game.add_player(player)?;
        
        Ok(player_id)
    }

    /// Удаляет игрока из игры
    pub fn remove_player_from_game(&self, game_id: Uuid, player_id: Uuid) -> Result<()> {
        // Проверяем, существует ли игра
        let mut game = self.games.get_mut(&game_id).context("Game not found")?;
        
        // Удаляем игрока из игры
        game.remove_player(player_id)?;
        
        Ok(())
    }

    /// Запускает игру
    pub fn start_game(&self, game_id: Uuid) -> Result<()> {
        // Проверяем, существует ли игра
        let mut game = self.games.get_mut(&game_id).context("Game not found")?;
        
        // Проверяем, готова ли игра к запуску
        if !game.is_ready_to_start() {
            return Err(anyhow::anyhow!("Game not ready to start"));
        }
        
        // Запускаем игру
        game.start()?;
        
        Ok(())
    }

    /// Приостанавливает игру
    pub fn pause_game(&self, game_id: Uuid) -> Result<()> {
        // Проверяем, существует ли игра
        let mut game = self.games.get_mut(&game_id).context("Game not found")?;
        
        // Приостанавливаем игру
        game.pause()?;
        
        Ok(())
    }

    /// Возобновляет игру
    pub fn resume_game(&self, game_id: Uuid) -> Result<()> {
        // Проверяем, существует ли игра
        let mut game = self.games.get_mut(&game_id).context("Game not found")?;
        
        // Возобновляем игру
        game.resume()?;
        
        Ok(())
    }

    /// Завершает игру
    pub fn finish_game(&self, game_id: Uuid, winner_id: Option<Uuid>) -> Result<()> {
        // Проверяем, существует ли игра
        let mut game = self.games.get_mut(&game_id).context("Game not found")?;
        
        // Завершаем игру
        game.finish(winner_id)?;
        
        Ok(())
    }

    /// Создает новый блок Tetris в игре
    pub async fn spawn_tetris_block(&self, game_id: Uuid, player_id: Uuid) -> Result<i32> {
        // Проверяем, существует ли игра
        let mut game = self.games.get_mut(&game_id).context("Game not found")?;
        
        // Проверяем, активна ли игра
        if !game.is_active() {
            return Err(anyhow::anyhow!("Game not active"));
        }
        
        // Проверяем, существует ли игрок
        if !game.players.contains_key(&player_id) {
            return Err(anyhow::anyhow!("Player not found"));
        }
        
        // Определяем тип блока (случайный или следующий)
        let block_type = if let Some(next_type) = game.next_block_type {
            next_type
        } else {
            // Случайный выбор типа блока
            use crate::physics::BlockType;
            use rand::Rng;
            
            let types = [
                BlockType::IBlock,
                BlockType::JBlock,
                BlockType::LBlock,
                BlockType::OBlock,
                BlockType::SBlock,
                BlockType::TBlock,
                BlockType::ZBlock,
            ];
            
            let mut rng = rand::thread_rng();
            types[rng.gen_range(0..types.len())]
        };
        
        // Генерируем следующий тип блока
        use crate::physics::BlockType;
        use rand::Rng;
        
        let types = [
            BlockType::IBlock,
            BlockType::JBlock,
            BlockType::LBlock,
            BlockType::OBlock,
            BlockType::SBlock,
            BlockType::TBlock,
            BlockType::ZBlock,
        ];
        
        let mut rng = rand::thread_rng();
        game.next_block_type = Some(types[rng.gen_range(0..types.len())]);
        
        // Определяем начальную позицию блока
        let position = (0.0, game.field_height as f32 - 2.0);
        
        // Создаем блок в физическом движке
        let block_ids = self.physics_manager.create_tetris_block(
            block_type,
            position,
            1.0, // размер блока
            0.0, // угол
            None, // материал по умолчанию
        ).await?;
        
        if block_ids.is_empty() {
            return Err(anyhow::anyhow!("Failed to create tetris block"));
        }
        
        // Сохраняем ID блока
        let block_id = block_ids[0]; // Используем первый блок как основной
        game.current_block_id = Some(block_id);
        
        // Добавляем все блоки игроку
        for &id in &block_ids {
            game.add_player_block(player_id, id)?;
        }
        
        Ok(block_id)
    }

    /// Перемещает текущий блок
    pub async fn move_current_block(&self, game_id: Uuid, direction: (f32, f32)) -> Result<()> {
        // Проверяем, существует ли игра
        let game = self.games.get(&game_id).context("Game not found")?;
        
        // Проверяем, активна ли игра
        if !game.is_active() {
            return Err(anyhow::anyhow!("Game not active"));
        }
        
        // Проверяем, есть ли текущий блок
        let block_id = game.current_block_id.context("No current block")?;
        
        // Получаем текущую позицию блока
        let (x, y) = self.physics_manager.get_block_position(block_id).await?;
        
        // Вычисляем новую позицию
        let new_position = (x + direction.0, y + direction.1);
        
        // Устанавливаем новую позицию
        self.physics_manager.set_block_position(block_id, new_position).await?;
        
        Ok(())
    }

    /// Вращает текущий блок
    pub async fn rotate_current_block(&self, game_id: Uuid, angle_delta: f32) -> Result<()> {
        // Проверяем, существует ли игра
        let game = self.games.get(&game_id).context("Game not found")?;
        
        // Проверяем, активна ли игра
        if !game.is_active() {
            return Err(anyhow::anyhow!("Game not active"));
        }
        
        // Проверяем, есть ли текущий блок
        let block_id = game.current_block_id.context("No current block")?;
        
        // Получаем текущий угол блока
        let current_angle = self.physics_manager.get_block_angle(block_id).await?;
        
        // Вычисляем новый угол
        let new_angle = current_angle + angle_delta;
        
        // Устанавливаем новый угол
        self.physics_manager.set_block_angle(block_id, new_angle).await?;
        
        Ok(())
    }

    /// Применяет заклинание
    pub fn cast_spell(&self, game_id: Uuid, caster_id: Uuid, spell_id: &str, target_id: Option<Uuid>) -> Result<()> {
        // Проверяем, существует ли игра
        let mut game = self.games.get_mut(&game_id).context("Game not found")?;
        
        // Проверяем, активна ли игра
        if !game.is_active() {
            return Err(anyhow::anyhow!("Game not active"));
        }
        
        // Применяем заклинание
        game.cast_spell(caster_id, spell_id, target_id)?;
        
        Ok(())
    }

    /// Проверяет, работает ли менеджер игр
    pub fn is_running(&self) -> bool {
        *self.running.blocking_read()
    }
}

impl Drop for GameManager {
    fn drop(&mut self) {
        // Остановка менеджера при уничтожении
        if *self.running.blocking_read() {
            if let Err(e) = self.stop() {
                error!("Error stopping Game Manager during drop: {}", e);
            }
        }
    }
}

impl Deref for Arc<GameManager> {
    type Target = GameManager;

    fn deref(&self) -> &Self::Target {
        &self
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum BlockType {
    I,
    J,
    L,
    O,
    S,
    T,
    Z,
}
