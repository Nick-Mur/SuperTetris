use std::fs;
use std::path::Path;
use serde::{Serialize, Deserialize};
use anyhow::{Result, Context};
use crate::network::NetworkConfig;
use crate::session::SessionConfig;
use crate::game::GameConfig;
use crate::physics::PhysicsConfig;

/// Конфигурация сервера
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServerConfig {
    /// Конфигурация сети
    pub network: NetworkConfig,
    /// Конфигурация сессий
    pub session: SessionConfig,
    /// Конфигурация игры
    pub game: GameConfig,
    /// Конфигурация физики
    pub physics: PhysicsConfig,
}

impl ServerConfig {
    /// Загружает конфигурацию из файла
    pub fn from_file<P: AsRef<Path>>(path: P) -> Result<Self> {
        let contents = fs::read_to_string(path)
            .context("Failed to read config file")?;
        
        let config: ServerConfig = toml::from_str(&contents)
            .context("Failed to parse config file")?;
        
        Ok(config)
    }
    
    /// Сохраняет конфигурацию в файл
    pub fn save_to_file<P: AsRef<Path>>(&self, path: P) -> Result<()> {
        let contents = toml::to_string_pretty(self)
            .context("Failed to serialize config")?;
        
        fs::write(path, contents)
            .context("Failed to write config file")?;
        
        Ok(())
    }
    
    /// Создает конфигурацию по умолчанию
    pub fn default() -> Self {
        Self {
            network: NetworkConfig::default(),
            session: SessionConfig::default(),
            game: GameConfig::default(),
            physics: PhysicsConfig::default(),
        }
    }
} 