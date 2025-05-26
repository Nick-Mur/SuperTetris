use log::{info, error, debug, warn, trace, LevelFilter};
use std::path::{Path, PathBuf};
use std::fs::{self, File};
use std::io::{self, Write};
use chrono::Local;
use env_logger::Builder;
use anyhow::{Result, Context};

/// Инициализация логгера
pub fn init_logger(log_path: &Path, level: &str) -> Result<()> {
    // Создаем директорию для логов если её нет
    if let Some(parent) = log_path.parent() {
        fs::create_dir_all(parent)
            .context("Failed to create log directory")?;
    }

    // Настраиваем уровень логирования
    let level = level.parse::<LevelFilter>()
        .context("Invalid log level")?;

    // Настраиваем формат логов
    Builder::new()
        .format(|buf, record| {
            writeln!(buf,
                "{} [{}] - {}",
                Local::now().format("%Y-%m-%d %H:%M:%S"),
                record.level(),
                record.args()
            )
        })
        .filter(None, level)
        .init();

    info!("Logger initialized with level: {}", level);
    Ok(())
}

/// Запись сообщения в лог-файл
pub fn write_to_log_file(log_path: &Path, message: &str) -> Result<()> {
    let mut file = File::options()
        .create(true)
        .append(true)
        .open(log_path)
        .context("Failed to open log file")?;

    writeln!(file, "{} - {}", Local::now().format("%Y-%m-%d %H:%M:%S"), message)
        .context("Failed to write to log file")?;

    Ok(())
}

pub fn log_error(message: &str) {
    error!("{}", message);
}

pub fn log_info(message: &str) {
    info!("{}", message);
}

pub fn log_debug(message: &str) {
    debug!("{}", message);
}

pub fn log_warn(message: &str) {
    warn!("{}", message);
}

pub fn log_trace(message: &str) {
    trace!("{}", message);
} 