use std::sync::{Arc, Mutex};
use tokio::sync::RwLock;
use warp::Filter;
use uuid::Uuid;
use serde::{Serialize, Deserialize};
use dashmap::DashMap;
use std::collections::HashMap;
use chrono::{DateTime, Utc};
use thiserror::Error;
use libloading::{Library, Symbol};
use std::path::Path;
use std::ffi::{CString, c_void, c_char, c_int, c_float};
use log::{info, error, warn, debug};
use crossbeam_channel::{bounded, Sender, Receiver};
use parking_lot::RwLock as PLRwLock;
use anyhow::{Result, anyhow};

// Определение модулей
mod physics;
mod game;
mod network;
mod session;
mod config;
mod utils;
mod ffi;

// Реэкспорт основных компонентов
pub use physics::PhysicsManager;
pub use game::{GameState, GameManager};
pub use network::{NetworkManager, WebSocketHandler};
pub use session::{Session, SessionManager};
pub use config::ServerConfig;

/// Основная структура сервера Tetris Towers
pub struct TetrisTowersServer {
    /// Менеджер сессий
    session_manager: Arc<SessionManager>,
    /// Менеджер физики
    physics_manager: Arc<PhysicsManager>,
    /// Менеджер игры
    game_manager: Arc<GameManager>,
    /// Менеджер сети
    network_manager: Arc<NetworkManager>,
    /// Конфигурация сервера
    config: ServerConfig,
    /// Флаг работы сервера
    running: Arc<PLRwLock<bool>>,
}

impl TetrisTowersServer {
    /// Создает новый экземпляр сервера с указанной конфигурацией
    pub async fn new(config: ServerConfig) -> Result<Self> {
        // Инициализация менеджеров
        let physics_manager = Arc::new(PhysicsManager::new(&config.physics)?);
        let game_manager = Arc::new(GameManager::new(&config.game, physics_manager.clone())?);
        let session_manager = Arc::new(SessionManager::new(&config.session, game_manager.clone())?);
        let network_manager = Arc::new(NetworkManager::new(&config.network, session_manager.clone())?);
        
        Ok(Self {
            session_manager,
            physics_manager,
            game_manager,
            network_manager,
            config,
            running: Arc::new(PLRwLock::new(false)),
        })
    }
    
    /// Запускает сервер
    pub async fn start(&self) -> Result<()> {
        info!("Starting Tetris Towers Server on {}:{}", self.config.network.host, self.config.network.port);
        
        // Устанавливаем флаг работы
        *self.running.write() = true;
        
        // Запускаем менеджеры
        self.physics_manager.start()?;
        self.game_manager.start()?;
        self.session_manager.start()?;
        
        // Запускаем сетевой менеджер (блокирующий вызов)
        self.network_manager.start().await?;
        
        Ok(())
    }
    
    /// Останавливает сервер
    pub async fn stop(&self) -> Result<()> {
        info!("Stopping Tetris Towers Server");
        
        // Сбрасываем флаг работы
        *self.running.write() = false;
        
        // Останавливаем менеджеры в обратном порядке
        self.network_manager.stop().await?;
        self.session_manager.stop()?;
        self.game_manager.stop()?;
        self.physics_manager.stop()?;
        
        Ok(())
    }
    
    /// Проверяет, работает ли сервер
    pub fn is_running(&self) -> bool {
        *self.running.read()
    }
    
    /// Возвращает ссылку на менеджер сессий
    pub fn session_manager(&self) -> Arc<SessionManager> {
        self.session_manager.clone()
    }
    
    /// Возвращает ссылку на менеджер физики
    pub fn physics_manager(&self) -> Arc<PhysicsManager> {
        self.physics_manager.clone()
    }
    
    /// Возвращает ссылку на менеджер игры
    pub fn game_manager(&self) -> Arc<GameManager> {
        self.game_manager.clone()
    }
    
    /// Возвращает ссылку на менеджер сети
    pub fn network_manager(&self) -> Arc<NetworkManager> {
        self.network_manager.clone()
    }
}

/// Ошибки сервера
#[derive(Debug, Error)]
pub enum ServerError {
    #[error("Configuration error: {0}")]
    ConfigError(String),
    
    #[error("Network error: {0}")]
    NetworkError(String),
    
    #[error("Session error: {0}")]
    SessionError(String),
    
    #[error("Game error: {0}")]
    GameError(String),
    
    #[error("Physics error: {0}")]
    PhysicsError(String),
    
    #[error("FFI error: {0}")]
    FFIError(String),
    
    #[error("Internal error: {0}")]
    InternalError(String),
}

/// Версия сервера
pub const SERVER_VERSION: &str = env!("CARGO_PKG_VERSION");
