use tokio;
use log::{info, error};
use std::env;
use anyhow::Result;
use tetris_towers_server::{TetrisTowersServer, ServerConfig};

mod physics;
mod game;
mod network;
mod session;
mod utils;
mod types;

#[tokio::main]
async fn main() -> Result<()> {
    // Инициализация логгера
    env_logger::init();
    info!("Starting Tetris Server...");
    
    // Загрузка конфигурации
    let config_path = env::var("CONFIG_PATH").unwrap_or_else(|_| "config/server.toml".to_string());
    info!("Loading configuration from {}", config_path);
    
    let config = ServerConfig::from_file(&config_path)?;
    
    // Создание и запуск сервера
    let server = TetrisTowersServer::new(config).await?;
    
    info!("Tetris Towers Server initialized successfully");
    
    // Обработка сигналов завершения
    let server_clone = server.clone();
    tokio::spawn(async move {
        tokio::signal::ctrl_c().await.expect("Failed to listen for Ctrl+C");
        info!("Received shutdown signal");
        if let Err(e) = server_clone.stop().await {
            error!("Error during server shutdown: {}", e);
        }
    });
    
    // Запуск сервера (блокирующий вызов)
    server.start().await?;
    
    info!("Server shutdown complete");
    Ok(())
}
