use serde::{Serialize, Deserialize};
use std::path::{Path, PathBuf};
use anyhow::{Result, Context};
use crate::utils::file;

#[derive(Debug, Serialize, Deserialize)]
pub struct Config {
    pub server: ServerConfig,
    pub game: GameConfig,
    pub physics: PhysicsConfig,
    pub logging: LoggingConfig,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ServerConfig {
    pub host: String,
    pub port: u16,
    pub ws_port: u16,
    pub enable_cors: bool,
    pub heartbeat_interval: u64,
    pub cleanup_interval: u64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GameConfig {
    pub width: i32,
    pub height: i32,
    pub block_size: i32,
    pub game_speed: f32,
    pub max_players: usize,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct PhysicsConfig {
    pub gravity: f32,
    pub friction: f32,
    pub collision_threshold: f32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct LoggingConfig {
    pub level: String,
    pub file_path: PathBuf,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            server: ServerConfig {
                host: "127.0.0.1".to_string(),
                port: 8080,
                ws_port: 8081,
                enable_cors: true,
                heartbeat_interval: 30,
                cleanup_interval: 300,
            },
            game: GameConfig {
                width: 10,
                height: 20,
                block_size: 30,
                game_speed: 1.0,
                max_players: 4,
            },
            physics: PhysicsConfig {
                gravity: 9.81,
                friction: 0.1,
                collision_threshold: 0.01,
            },
            logging: LoggingConfig {
                level: "info".to_string(),
                file_path: PathBuf::from("logs/app.log"),
            },
        }
    }
}

/// Загрузка конфигурации из файла
pub fn load_config(path: &Path) -> Result<Config> {
    let content = file::read_file_to_string(path)?;
    let config: Config = serde_json::from_str(&content)
        .context("Failed to parse config file")?;
    Ok(config)
}

/// Сохранение конфигурации в файл
pub fn save_config(config: &Config, path: &Path) -> Result<()> {
    let content = serde_json::to_string_pretty(config)
        .context("Failed to serialize config")?;
    file::write_string_to_file(path, &content)
}

/// Создание конфигурации по умолчанию
pub fn create_default_config(path: &Path) -> Result<()> {
    let config = Config::default();
    save_config(&config, path)
}

/// Получение пути к конфигурационному файлу
pub fn get_config_path() -> PathBuf {
    let mut path = PathBuf::from("config");
    path.push("config.json");
    path
} 