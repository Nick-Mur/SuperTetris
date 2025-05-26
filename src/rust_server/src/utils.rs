use std::sync::Arc;
use std::time::{Duration, Instant};
use std::collections::HashMap;
use anyhow::{Result, Context};
use log::{info, error, debug, warn};
use serde::{Serialize, Deserialize};
use tokio::sync::RwLock;
use uuid::Uuid;
use regex::Regex;
use rand::Rng;
use rand::distributions::{Distribution, Standard, Uniform};
use rand::seq::SliceRandom;
use sha2::{Sha256, Sha512, Digest};
use hmac::{Hmac, Mac};
use base64::{Engine as _, engine::general_purpose};
use chrono::{DateTime, Utc};

/// Константы для игры
pub mod constants {
    /// Версия сервера
    pub const SERVER_VERSION: &str = "1.0.0";
    
    /// Гравитация по умолчанию
    pub const DEFAULT_GRAVITY: f32 = 9.8;
    
    /// Размер блока по умолчанию
    pub const DEFAULT_BLOCK_SIZE: f32 = 1.0;
    
    /// Максимальная высота башни
    pub const MAX_TOWER_HEIGHT: f32 = 30.0;
    
    /// Максимальное количество блоков
    pub const MAX_BLOCKS: usize = 1000;
    
    /// Максимальное количество игроков
    pub const MAX_PLAYERS: usize = 4;
    
    /// Интервал обновления физики (в миллисекундах)
    pub const PHYSICS_UPDATE_INTERVAL_MS: u64 = 16;
    
    /// Интервал обновления игры (в миллисекундах)
    pub const GAME_UPDATE_INTERVAL_MS: u64 = 33;
    
    /// Интервал обновления сети (в миллисекундах)
    pub const NETWORK_UPDATE_INTERVAL_MS: u64 = 50;
    
    /// Таймаут соединения (в секундах)
    pub const CONNECTION_TIMEOUT_SEC: u64 = 60;
    
    /// Время жизни сессии (в секундах)
    pub const SESSION_TTL_SEC: u64 = 3600;
    
    /// Интервал очистки устаревших сессий (в секундах)
    pub const SESSION_CLEANUP_INTERVAL_SEC: u64 = 300;
    
    /// Интервал проверки активности сессий (в секундах)
    pub const SESSION_HEARTBEAT_INTERVAL_SEC: u64 = 30;
    
    /// Таймаут неактивности (в секундах)
    pub const INACTIVITY_TIMEOUT_SEC: u64 = 300;
    
    /// Максимальный размер сообщения (в байтах)
    pub const MAX_MESSAGE_SIZE: usize = 1024 * 1024; // 1 MB
    
    /// Порт сервера по умолчанию
    pub const DEFAULT_SERVER_PORT: u16 = 8080;
    
    /// Хост сервера по умолчанию
    pub const DEFAULT_SERVER_HOST: &str = "0.0.0.0";
    
    /// Путь к ресурсам по умолчанию
    pub const DEFAULT_RESOURCES_PATH: &str = "resources";
    
    /// Путь к логам по умолчанию
    pub const DEFAULT_LOGS_PATH: &str = "logs";
    
    /// Путь к конфигурации по умолчанию
    pub const DEFAULT_CONFIG_PATH: &str = "config";
    
    /// Имя файла конфигурации по умолчанию
    pub const DEFAULT_CONFIG_FILE: &str = "config.json";
    
    /// Имя файла логов по умолчанию
    pub const DEFAULT_LOG_FILE: &str = "server.log";
    
    /// Уровень логирования по умолчанию
    pub const DEFAULT_LOG_LEVEL: &str = "info";
    
    /// Максимальное количество соединений
    pub const MAX_CONNECTIONS: usize = 1000;
    
    /// Максимальное количество игр
    pub const MAX_GAMES: usize = 100;
    
    /// Максимальное количество сессий
    pub const MAX_SESSIONS: usize = 1000;
    
    /// Максимальное количество заклинаний
    pub const MAX_SPELLS: usize = 10;
    
    /// Максимальное количество активных заклинаний
    pub const MAX_ACTIVE_SPELLS: usize = 5;
    
    /// Максимальное количество блоков в одной игре
    pub const MAX_BLOCKS_PER_GAME: usize = 200;
    
    /// Максимальное количество блоков у одного игрока
    pub const MAX_BLOCKS_PER_PLAYER: usize = 50;
    
    /// Максимальная скорость блока
    pub const MAX_BLOCK_VELOCITY: f32 = 20.0;
    
    /// Максимальный угол поворота блока
    pub const MAX_BLOCK_ROTATION: f32 = 360.0;
    
    /// Максимальная сила, применяемая к блоку
    pub const MAX_BLOCK_FORCE: f32 = 100.0;
    
    /// Максимальный крутящий момент, применяемый к блоку
    pub const MAX_BLOCK_TORQUE: f32 = 50.0;
    
    /// Максимальная плотность блока
    pub const MAX_BLOCK_DENSITY: f32 = 10.0;
    
    /// Максимальное трение блока
    pub const MAX_BLOCK_FRICTION: f32 = 1.0;
    
    /// Максимальная упругость блока
    pub const MAX_BLOCK_RESTITUTION: f32 = 1.0;
    
    /// Максимальная линейная демпфирование блока
    pub const MAX_BLOCK_LINEAR_DAMPING: f32 = 1.0;
    
    /// Максимальное угловое демпфирование блока
    pub const MAX_BLOCK_ANGULAR_DAMPING: f32 = 1.0;
    
    /// Максимальная длина имени игрока
    pub const MAX_PLAYER_NAME_LENGTH: usize = 32;
    
    /// Максимальная длина имени игры
    pub const MAX_GAME_NAME_LENGTH: usize = 64;
    
    /// Максимальная длина имени заклинания
    pub const MAX_SPELL_NAME_LENGTH: usize = 32;
    
    /// Максимальная длина описания заклинания
    pub const MAX_SPELL_DESCRIPTION_LENGTH: usize = 256;
    
    /// Максимальная длина ключа метаданных
    pub const MAX_METADATA_KEY_LENGTH: usize = 32;
    
    /// Максимальная длина значения метаданных
    pub const MAX_METADATA_VALUE_LENGTH: usize = 256;
    
    /// Максимальное количество метаданных
    pub const MAX_METADATA_COUNT: usize = 10;
}

/// Утилиты для работы с временем
pub mod time {
    use std::time::{Duration, Instant};
    use chrono::{DateTime, Utc};
    
    /// Получает текущее время в формате RFC3339
    pub fn now_rfc3339() -> String {
        chrono::Utc::now().to_rfc3339()
    }
    
    /// Получает текущее время в формате ISO8601
    pub fn now_iso8601() -> String {
        chrono::Utc::now().to_rfc3339_opts(chrono::SecondsFormat::Millis, true)
    }
    
    /// Получает текущее время в формате Unix timestamp
    pub fn now_unix_timestamp() -> i64 {
        chrono::Utc::now().timestamp()
    }
    
    /// Получает текущее время в формате Unix timestamp с миллисекундами
    pub fn now_unix_timestamp_millis() -> i64 {
        chrono::Utc::now().timestamp_millis()
    }
    
    /// Получает текущее время в формате Unix timestamp с наносекундами
    pub fn now_unix_timestamp_nanos() -> i64 {
        chrono::Utc::now().timestamp_nanos()
    }
    
    /// Преобразует Unix timestamp в DateTime<Utc>
    pub fn unix_timestamp_to_datetime(timestamp: i64) -> DateTime<Utc> {
        DateTime::from_timestamp(timestamp, 0).unwrap_or(Utc::now())
    }
    
    /// Преобразует Unix timestamp с миллисекундами в DateTime<Utc>
    pub fn unix_timestamp_millis_to_datetime(timestamp: i64) -> DateTime<Utc> {
        let seconds = timestamp / 1000;
        let nanos = ((timestamp % 1000) * 1_000_000) as u32;
        DateTime::from_timestamp(seconds, nanos).unwrap_or(Utc::now())
    }
    
    /// Преобразует DateTime<Utc> в Unix timestamp
    pub fn datetime_to_unix_timestamp(datetime: DateTime<Utc>) -> i64 {
        datetime.timestamp()
    }
    
    /// Преобразует DateTime<Utc> в Unix timestamp с миллисекундами
    pub fn datetime_to_unix_timestamp_millis(datetime: DateTime<Utc>) -> i64 {
        datetime.timestamp_millis()
    }
    
    /// Преобразует DateTime<Utc> в Unix timestamp с наносекундами
    pub fn datetime_to_unix_timestamp_nanos(datetime: DateTime<Utc>) -> i64 {
        datetime.timestamp_nanos()
    }
    
    /// Измеряет время выполнения функции
    pub fn measure_time<F, T>(f: F) -> (T, Duration)
    where
        F: FnOnce() -> T,
    {
        let start = Instant::now();
        let result = f();
        let duration = start.elapsed();
        (result, duration)
    }
    
    /// Измеряет время выполнения асинхронной функции
    pub async fn measure_time_async<F, T>(f: F) -> (T, Duration)
    where
        F: std::future::Future<Output = T>,
    {
        let start = Instant::now();
        let result = f.await;
        let duration = start.elapsed();
        (result, duration)
    }
}

/// Утилиты для работы с UUID
pub mod uuid {
    use uuid::Uuid;
    
    /// Генерирует новый UUID v4
    pub fn generate_uuid_v4() -> Uuid {
        Uuid::new_v4()
    }
    
    /// Генерирует новый UUID v4 в виде строки
    pub fn generate_uuid_v4_string() -> String {
        Uuid::new_v4().to_string()
    }
    
    /// Преобразует строку в UUID
    pub fn parse_uuid(s: &str) -> anyhow::Result<Uuid> {
        Uuid::parse_str(s).map_err(|e| anyhow::anyhow!("Failed to parse UUID: {}", e))
    }
    
    /// Проверяет, является ли строка валидным UUID
    pub fn is_valid_uuid(s: &str) -> bool {
        Uuid::parse_str(s).is_ok()
    }
}

/// Утилиты для работы с JSON
pub mod json {
    use serde::{Serialize, Deserialize};
    use serde_json::{Value, json};
    
    /// Преобразует объект в JSON
    pub fn to_json<T>(value: &T) -> anyhow::Result<String>
    where
        T: Serialize,
    {
        serde_json::to_string(value).map_err(|e| anyhow::anyhow!("Failed to serialize to JSON: {}", e))
    }
    
    /// Преобразует объект в форматированный JSON
    pub fn to_pretty_json<T>(value: &T) -> anyhow::Result<String>
    where
        T: Serialize,
    {
        serde_json::to_string_pretty(value).map_err(|e| anyhow::anyhow!("Failed to serialize to pretty JSON: {}", e))
    }
    
    /// Преобразует JSON в объект
    pub fn from_json<T>(json: &str) -> anyhow::Result<T>
    where
        T: for<'de> Deserialize<'de>,
    {
        serde_json::from_str(json).map_err(|e| anyhow::anyhow!("Failed to deserialize from JSON: {}", e))
    }
    
    /// Преобразует JSON в Value
    pub fn parse_json(json: &str) -> anyhow::Result<Value> {
        serde_json::from_str(json).map_err(|e| anyhow::anyhow!("Failed to parse JSON: {}", e))
    }
    
    /// Создает JSON объект
    pub fn create_json_object() -> Value {
        json!({})
    }
    
    /// Создает JSON массив
    pub fn create_json_array() -> Value {
        json!([])
    }
    
    /// Добавляет поле в JSON объект
    pub fn add_field_to_json_object(obj: &mut Value, key: &str, value: Value) -> anyhow::Result<()> {
        if !obj.is_object() {
            return Err(anyhow::anyhow!("Value is not a JSON object"));
        }
        
        obj[key] = value;
        Ok(())
    }
    
    /// Добавляет элемент в JSON массив
    pub fn add_item_to_json_array(arr: &mut Value, value: Value) -> anyhow::Result<()> {
        if !arr.is_array() {
            return Err(anyhow::anyhow!("Value is not a JSON array"));
        }
        
        arr.as_array_mut().unwrap().push(value);
        Ok(())
    }
    
    /// Получает поле из JSON объекта
    pub fn get_field_from_json_object<'a>(obj: &'a Value, key: &str) -> anyhow::Result<&'a Value> {
        if !obj.is_object() {
            return Err(anyhow::anyhow!("Value is not a JSON object"));
        }
        
        obj.get(key).ok_or_else(|| anyhow::anyhow!("Field not found: {}", key))
    }
    
    /// Получает элемент из JSON массива
    pub fn get_item_from_json_array<'a>(arr: &'a Value, index: usize) -> anyhow::Result<&'a Value> {
        if !arr.is_array() {
            return Err(anyhow::anyhow!("Value is not a JSON array"));
        }
        
        arr.as_array().unwrap().get(index).ok_or_else(|| anyhow::anyhow!("Index out of bounds: {}", index))
    }
}

/// Утилиты для работы с файлами
pub mod file {
    use std::path::{Path, PathBuf};
    use std::fs::{self, File};
    use std::io::{self, Read, Write};
    
    /// Проверяет, существует ли файл
    pub fn file_exists<P: AsRef<Path>>(path: P) -> bool {
        Path::new(path.as_ref()).exists()
    }
    
    /// Проверяет, является ли путь директорией
    pub fn is_directory<P: AsRef<Path>>(path: P) -> bool {
        Path::new(path.as_ref()).is_dir()
    }
    
    /// Проверяет, является ли путь файлом
    pub fn is_file<P: AsRef<Path>>(path: P) -> bool {
        Path::new(path.as_ref()).is_file()
    }
    
    /// Создает директорию
    pub fn create_directory<P: AsRef<Path>>(path: P) -> io::Result<()> {
        fs::create_dir_all(path)
    }
    
    /// Удаляет файл
    pub fn delete_file<P: AsRef<Path>>(path: P) -> io::Result<()> {
        fs::remove_file(path)
    }
    
    /// Удаляет директорию
    pub fn delete_directory<P: AsRef<Path>>(path: P) -> io::Result<()> {
        fs::remove_dir_all(path)
    }
    
    /// Копирует файл
    pub fn copy_file<P: AsRef<Path>, Q: AsRef<Path>>(from: P, to: Q) -> io::Result<u64> {
        fs::copy(from, to)
    }
    
    /// Перемещает файл
    pub fn move_file<P: AsRef<Path>, Q: AsRef<Path>>(from: P, to: Q) -> io::Result<()> {
        fs::rename(from, to)
    }
    
    /// Читает содержимое файла в строку
    pub fn read_file_to_string<P: AsRef<Path>>(path: P) -> io::Result<String> {
        fs::read_to_string(path)
    }
    
    /// Читает содержимое файла в байты
    pub fn read_file_to_bytes<P: AsRef<Path>>(path: P) -> io::Result<Vec<u8>> {
        fs::read(path)
    }
    
    /// Записывает строку в файл
    pub fn write_string_to_file<P: AsRef<Path>>(path: P, content: &str) -> io::Result<()> {
        fs::write(path, content)
    }
    
    /// Записывает байты в файл
    pub fn write_bytes_to_file<P: AsRef<Path>>(path: P, content: &[u8]) -> io::Result<()> {
        fs::write(path, content)
    }
    
    /// Добавляет строку в файл
    pub fn append_string_to_file<P: AsRef<Path>>(path: P, content: &str) -> io::Result<()> {
        let mut file = fs::OpenOptions::new()
            .write(true)
            .append(true)
            .create(true)
            .open(path)?;
        
        file.write_all(content.as_bytes())
    }
    
    /// Добавляет байты в файл
    pub fn append_bytes_to_file<P: AsRef<Path>>(path: P, content: &[u8]) -> io::Result<()> {
        let mut file = fs::OpenOptions::new()
            .write(true)
            .append(true)
            .create(true)
            .open(path)?;
        
        file.write_all(content)
    }
    
    /// Получает размер файла
    pub fn get_file_size<P: AsRef<Path>>(path: P) -> io::Result<u64> {
        let metadata = fs::metadata(path)?;
        Ok(metadata.len())
    }
    
    /// Получает время последнего изменения файла
    pub fn get_file_modified_time<P: AsRef<Path>>(path: P) -> io::Result<std::time::SystemTime> {
        let metadata = fs::metadata(path)?;
        metadata.modified()
    }
    
    /// Получает время создания файла
    pub fn get_file_created_time<P: AsRef<Path>>(path: P) -> io::Result<std::time::SystemTime> {
        let metadata = fs::metadata(path)?;
        metadata.created()
    }
    
    /// Получает время последнего доступа к файлу
    pub fn get_file_accessed_time<P: AsRef<Path>>(path: P) -> io::Result<std::time::SystemTime> {
        let metadata = fs::metadata(path)?;
        metadata.accessed()
    }
    
    /// Получает список файлов в директории
    pub fn list_files<P: AsRef<Path>>(path: P) -> io::Result<Vec<PathBuf>> {
        let mut files = Vec::new();
        
        for entry in fs::read_dir(path)? {
            let entry = entry?;
            let path = entry.path();
            
            if path.is_file() {
                files.push(path);
            }
        }
        
        Ok(files)
    }
    
    /// Получает список директорий в директории
    pub fn list_directories<P: AsRef<Path>>(path: P) -> io::Result<Vec<PathBuf>> {
        let mut directories = Vec::new();
        
        for entry in fs::read_dir(path)? {
            let entry = entry?;
            let path = entry.path();
            
            if path.is_dir() {
                directories.push(path);
            }
        }
        
        Ok(directories)
    }
    
    /// Получает список всех файлов и директорий в директории
    pub fn list_all<P: AsRef<Path>>(path: P) -> io::Result<Vec<PathBuf>> {
        let mut all = Vec::new();
        
        for entry in fs::read_dir(path)? {
            let entry = entry?;
            let path = entry.path();
            
            all.push(path);
        }
        
        Ok(all)
    }
}

/// Утилиты для работы с конфигурацией
pub mod config {
    use std::path::{Path, PathBuf};
    use std::fs::{self, File};
    use std::io::{self, Read, Write};
    use serde::{Serialize, Deserialize};
    
    /// Загружает конфигурацию из JSON файла
    pub fn load_config<T, P: AsRef<Path>>(path: P) -> anyhow::Result<T>
    where
        T: for<'de> Deserialize<'de>,
    {
        let content = fs::read_to_string(path)?;
        let config = serde_json::from_str(&content)?;
        Ok(config)
    }
    
    /// Сохраняет конфигурацию в JSON файл
    pub fn save_config<T, P: AsRef<Path>>(path: P, config: &T) -> anyhow::Result<()>
    where
        T: Serialize,
    {
        let content = serde_json::to_string_pretty(config)?;
        fs::write(path, content)?;
        Ok(())
    }
    
    /// Загружает конфигурацию из YAML файла
    pub fn load_config_yaml<T, P: AsRef<Path>>(path: P) -> anyhow::Result<T>
    where
        T: for<'de> Deserialize<'de>,
    {
        let content = fs::read_to_string(path)?;
        let config = serde_yaml::from_str(&content)?;
        Ok(config)
    }
    
    /// Сохраняет конфигурацию в YAML файл
    pub fn save_config_yaml<T, P: AsRef<Path>>(path: P, config: &T) -> anyhow::Result<()>
    where
        T: Serialize,
    {
        let content = serde_yaml::to_string(config)?;
        fs::write(path, content)?;
        Ok(())
    }
    
    /// Загружает конфигурацию из TOML файла
    pub fn load_config_toml<T, P: AsRef<Path>>(path: P) -> anyhow::Result<T>
    where
        T: for<'de> Deserialize<'de>,
    {
        let content = fs::read_to_string(path)?;
        let config = toml::from_str(&content)?;
        Ok(config)
    }
    
    /// Сохраняет конфигурацию в TOML файл
    pub fn save_config_toml<T, P: AsRef<Path>>(path: P, config: &T) -> anyhow::Result<()>
    where
        T: Serialize,
    {
        let content = toml::to_string(config)?;
        fs::write(path, content)?;
        Ok(())
    }
}

/// Утилиты для работы с логированием
pub mod logging {
    use log::{info, error, debug, warn, trace, LevelFilter};
    use std::path::{Path, PathBuf};
    use std::fs::{self, File};
    use std::io::{self, Write};
    
    /// Инициализирует логирование
    pub fn init_logging<P: AsRef<Path>>(log_file: Option<P>, level: LevelFilter) -> anyhow::Result<()> {
        let mut builder = env_logger::Builder::new();
        
        builder.filter_level(level);
        
        if let Some(log_file) = log_file {
            let file = fs::OpenOptions::new()
                .write(true)
                .create(true)
                .append(true)
                .open(log_file)?;
            
            builder.target(env_logger::Target::Pipe(Box::new(file)));
        }
        
        builder.init();
        
        Ok(())
    }
    
    /// Преобразует строку в уровень логирования
    pub fn parse_log_level(level: &str) -> LevelFilter {
        match level.to_lowercase().as_str() {
            "off" => LevelFilter::Off,
            "error" => LevelFilter::Error,
            "warn" => LevelFilter::Warn,
            "info" => LevelFilter::Info,
            "debug" => LevelFilter::Debug,
            "trace" => LevelFilter::Trace,
            _ => LevelFilter::Info,
        }
    }
}

/// Утилиты для работы с математикой
pub mod math {
    use std::f32::consts::PI;
    
    /// Преобразует градусы в радианы
    pub fn degrees_to_radians(degrees: f32) -> f32 {
        degrees * PI / 180.0
    }
    
    /// Преобразует радианы в градусы
    pub fn radians_to_degrees(radians: f32) -> f32 {
        radians * 180.0 / PI
    }
    
    /// Ограничивает значение в диапазоне
    pub fn clamp<T: PartialOrd>(value: T, min: T, max: T) -> T {
        if value < min {
            min
        } else if value > max {
            max
        } else {
            value
        }
    }
    
    /// Линейная интерполяция
    pub fn lerp(a: f32, b: f32, t: f32) -> f32 {
        a + (b - a) * t
    }
    
    /// Расстояние между двумя точками
    pub fn distance(x1: f32, y1: f32, x2: f32, y2: f32) -> f32 {
        let dx = x2 - x1;
        let dy = y2 - y1;
        (dx * dx + dy * dy).sqrt()
    }
    
    /// Расстояние между двумя точками в 3D
    pub fn distance_3d(x1: f32, y1: f32, z1: f32, x2: f32, y2: f32, z2: f32) -> f32 {
        let dx = x2 - x1;
        let dy = y2 - y1;
        let dz = z2 - z1;
        (dx * dx + dy * dy + dz * dz).sqrt()
    }
    
    /// Нормализует угол в диапазоне [0, 360)
    pub fn normalize_angle_degrees(angle: f32) -> f32 {
        let mut result = angle % 360.0;
        if result < 0.0 {
            result += 360.0;
        }
        result
    }
    
    /// Нормализует угол в диапазоне [0, 2π)
    pub fn normalize_angle_radians(angle: f32) -> f32 {
        let mut result = angle % (2.0 * PI);
        if result < 0.0 {
            result += 2.0 * PI;
        }
        result
    }
    
    /// Проверяет, находится ли точка внутри прямоугольника
    pub fn point_in_rect(px: f32, py: f32, rx: f32, ry: f32, rw: f32, rh: f32) -> bool {
        px >= rx && px <= rx + rw && py >= ry && py <= ry + rh
    }
    
    /// Проверяет, находится ли точка внутри круга
    pub fn point_in_circle(px: f32, py: f32, cx: f32, cy: f32, radius: f32) -> bool {
        distance(px, py, cx, cy) <= radius
    }
    
    /// Проверяет, пересекаются ли два прямоугольника
    pub fn rect_intersects_rect(r1x: f32, r1y: f32, r1w: f32, r1h: f32, r2x: f32, r2y: f32, r2w: f32, r2h: f32) -> bool {
        r1x < r2x + r2w && r1x + r1w > r2x && r1y < r2y + r2h && r1y + r1h > r2y
    }
    
    /// Проверяет, пересекаются ли два круга
    pub fn circle_intersects_circle(c1x: f32, c1y: f32, c1r: f32, c2x: f32, c2y: f32, c2r: f32) -> bool {
        distance(c1x, c1y, c2x, c2y) <= c1r + c2r
    }
    
    /// Проверяет, пересекаются ли круг и прямоугольник
    pub fn circle_intersects_rect(cx: f32, cy: f32, cr: f32, rx: f32, ry: f32, rw: f32, rh: f32) -> bool {
        let closest_x = clamp(cx, rx, rx + rw);
        let closest_y = clamp(cy, ry, ry + rh);
        
        distance(cx, cy, closest_x, closest_y) <= cr
    }
}

/// Утилиты для работы с сетью
pub mod network {
    use std::net::{IpAddr, Ipv4Addr, Ipv6Addr, SocketAddr};
    use std::str::FromStr;
    
    /// Парсит IP-адрес
    pub fn parse_ip_addr(s: &str) -> anyhow::Result<IpAddr> {
        IpAddr::from_str(s).map_err(|e| anyhow::anyhow!("Failed to parse IP address: {}", e))
    }
    
    /// Парсит IPv4-адрес
    pub fn parse_ipv4_addr(s: &str) -> anyhow::Result<Ipv4Addr> {
        Ipv4Addr::from_str(s).map_err(|e| anyhow::anyhow!("Failed to parse IPv4 address: {}", e))
    }
    
    /// Парсит IPv6-адрес
    pub fn parse_ipv6_addr(s: &str) -> anyhow::Result<Ipv6Addr> {
        Ipv6Addr::from_str(s).map_err(|e| anyhow::anyhow!("Failed to parse IPv6 address: {}", e))
    }
    
    /// Парсит сокет-адрес
    pub fn parse_socket_addr(s: &str) -> anyhow::Result<SocketAddr> {
        SocketAddr::from_str(s).map_err(|e| anyhow::anyhow!("Failed to parse socket address: {}", e))
    }
    
    /// Проверяет, является ли IP-адрес локальным
    pub fn is_local_ip(ip: &IpAddr) -> bool {
        match ip {
            IpAddr::V4(ipv4) => {
                ipv4.is_loopback() || 
                ipv4.is_private() || 
                ipv4.is_link_local() || 
                ipv4.is_unspecified()
            },
            IpAddr::V6(ipv6) => {
                ipv6.is_loopback() || 
                ipv6.is_unspecified()
            },
        }
    }
    
    /// Создает сокет-адрес из хоста и порта
    pub fn create_socket_addr(host: &str, port: u16) -> anyhow::Result<SocketAddr> {
        let ip = parse_ip_addr(host)?;
        Ok(SocketAddr::new(ip, port))
    }
}

/// Утилиты для работы с строками
pub mod string {
    use std::collections::HashMap;
    
    /// Генерирует случайную строку заданной длины
    pub fn random_string(length: usize) -> String {
        use rand::Rng;
        use rand::distributions::Alphanumeric;
        
        rand::thread_rng()
            .sample_iter(&Alphanumeric)
            .take(length)
            .map(char::from)
            .collect()
    }
    
    /// Генерирует случайную строку из цифр заданной длины
    pub fn random_digits(length: usize) -> String {
        use rand::Rng;
        
        let mut rng = rand::thread_rng();
        (0..length)
            .map(|_| rng.gen_range(0..10).to_string())
            .collect()
    }
    
    /// Генерирует случайную строку из букв заданной длины
    pub fn random_letters(length: usize) -> String {
        use rand::Rng;
        
        let mut rng = rand::thread_rng();
        (0..length)
            .map(|_| {
                let c = rng.gen_range(0..26) as u8;
                (b'a' + c) as char
            })
            .collect()
    }
    
    /// Обрезает строку до заданной длины
    pub fn truncate(s: &str, max_length: usize) -> String {
        if s.len() <= max_length {
            s.to_string()
        } else {
            s[0..max_length].to_string()
        }
    }
    
    /// Обрезает строку до заданной длины с добавлением многоточия
    pub fn truncate_with_ellipsis(s: &str, max_length: usize) -> String {
        if s.len() <= max_length {
            s.to_string()
        } else if max_length < 3 {
            s[0..max_length].to_string()
        } else {
            format!("{}...", s[0..max_length - 3].to_string())
        }
    }
    
    /// Проверяет, является ли строка пустой или состоит только из пробельных символов
    pub fn is_blank(s: &str) -> bool {
        s.trim().is_empty()
    }
    
    /// Проверяет, является ли строка числом
    pub fn is_numeric(s: &str) -> bool {
        s.parse::<f64>().is_ok()
    }
    
    /// Проверяет, является ли строка целым числом
    pub fn is_integer(s: &str) -> bool {
        s.parse::<i64>().is_ok()
    }
    
    /// Проверяет, является ли строка действительным числом
    pub fn is_float(s: &str) -> bool {
        s.parse::<f64>().is_ok() && !s.parse::<i64>().is_ok()
    }
    
    /// Проверяет, является ли строка буквенной
    pub fn is_alphabetic(s: &str) -> bool {
        !s.is_empty() && s.chars().all(|c| c.is_alphabetic())
    }
    
    /// Проверяет, является ли строка буквенно-цифровой
    pub fn is_alphanumeric(s: &str) -> bool {
        !s.is_empty() && s.chars().all(|c| c.is_alphanumeric())
    }
    
    /// Проверяет, является ли строка действительным email-адресом
    pub fn is_email(s: &str) -> bool {
        // Простая проверка на наличие @ и точки после @
        s.contains('@') && s.split('@').nth(1).map_or(false, |domain| domain.contains('.'))
    }
    
    /// Проверяет, является ли строка действительным URL
    pub fn is_url(s: &str) -> bool {
        // Простая проверка на наличие протокола и домена
        s.starts_with("http://") || s.starts_with("https://") || s.starts_with("ftp://")
    }
    
    /// Преобразует строку в snake_case
    pub fn to_snake_case(s: &str) -> String {
        let mut result = String::new();
        let mut prev_is_upper = false;
        
        for (i, c) in s.char_indices() {
            if c.is_uppercase() {
                if i > 0 && !prev_is_upper {
                    result.push('_');
                }
                result.push(c.to_lowercase().next().unwrap());
                prev_is_upper = true;
            } else {
                result.push(c);
                prev_is_upper = false;
            }
        }
        
        result
    }
    
    /// Преобразует строку в camelCase
    pub fn to_camel_case(s: &str) -> String {
        let mut result = String::new();
        let mut capitalize_next = false;
        
        for c in s.chars() {
            if c == '_' || c == '-' || c == ' ' {
                capitalize_next = true;
            } else if capitalize_next {
                result.push(c.to_uppercase().next().unwrap());
                capitalize_next = false;
            } else {
                result.push(c);
            }
        }
        
        result
    }
    
    /// Преобразует строку в PascalCase
    pub fn to_pascal_case(s: &str) -> String {
        let mut result = String::new();
        let mut capitalize_next = true;
        
        for c in s.chars() {
            if c == '_' || c == '-' || c == ' ' {
                capitalize_next = true;
            } else if capitalize_next {
                result.push(c.to_uppercase().next().unwrap());
                capitalize_next = false;
            } else {
                result.push(c);
            }
        }
        
        result
    }
    
    /// Преобразует строку в kebab-case
    pub fn to_kebab_case(s: &str) -> String {
        let mut result = String::new();
        let mut prev_is_upper = false;
        
        for (i, c) in s.char_indices() {
            if c.is_uppercase() {
                if i > 0 && !prev_is_upper {
                    result.push('-');
                }
                result.push(c.to_lowercase().next().unwrap());
                prev_is_upper = true;
            } else if c == '_' || c == ' ' {
                result.push('-');
                prev_is_upper = false;
            } else {
                result.push(c);
                prev_is_upper = false;
            }
        }
        
        result
    }
}

/// Утилиты для работы с хешированием
pub mod hash {
    use sha2::{Sha256, Sha512, Digest};
    use hmac::{Hmac, Mac};
    use base64::{Engine as _, engine::general_purpose};
    
    /// Вычисляет SHA-256 хеш
    pub fn sha256(data: &[u8]) -> String {
        let mut hasher = Sha256::new();
        hasher.update(data);
        let result = hasher.finalize();
        format!("{:x}", result)
    }
    
    /// Вычисляет SHA-512 хеш
    pub fn sha512(data: &[u8]) -> String {
        let mut hasher = Sha512::new();
        hasher.update(data);
        let result = hasher.finalize();
        format!("{:x}", result)
    }
    
    /// Вычисляет HMAC-SHA-256
    pub fn hmac_sha256(key: &[u8], data: &[u8]) -> anyhow::Result<String> {
        let mut mac = Hmac::<Sha256>::new_from_slice(key)
            .map_err(|e| anyhow::anyhow!("Failed to create HMAC: {}", e))?;
        
        mac.update(data);
        let result = mac.finalize().into_bytes();
        
        Ok(format!("{:x}", result))
    }
    
    /// Вычисляет HMAC-SHA-512
    pub fn hmac_sha512(key: &[u8], data: &[u8]) -> anyhow::Result<String> {
        let mut mac = Hmac::<Sha512>::new_from_slice(key)
            .map_err(|e| anyhow::anyhow!("Failed to create HMAC: {}", e))?;
        
        mac.update(data);
        let result = mac.finalize().into_bytes();
        
        Ok(format!("{:x}", result))
    }
    
    /// Кодирует данные в Base64
    pub fn base64_encode(data: &[u8]) -> String {
        general_purpose::STANDARD.encode(data)
    }
    
    /// Декодирует данные из Base64
    pub fn base64_decode(data: &str) -> anyhow::Result<Vec<u8>> {
        general_purpose::STANDARD.decode(data)
            .map_err(|e| anyhow::anyhow!("Failed to decode Base64: {}", e))
    }
    
    /// Кодирует данные в URL-безопасный Base64
    pub fn base64_url_encode(data: &[u8]) -> String {
        general_purpose::URL_SAFE.encode(data)
    }
    
    /// Декодирует данные из URL-безопасного Base64
    pub fn base64_url_decode(data: &str) -> anyhow::Result<Vec<u8>> {
        general_purpose::URL_SAFE.decode(data)
            .map_err(|e| anyhow::anyhow!("Failed to decode URL-safe Base64: {}", e))
    }
}

/// Утилиты для работы с случайными числами
pub mod random {
    use rand::{Rng, thread_rng};
    use rand::distributions::{Distribution, Standard, Uniform};
    
    /// Генерирует случайное целое число в диапазоне [min, max]
    pub fn random_int(min: i32, max: i32) -> i32 {
        thread_rng().gen_range(min..=max)
    }
    
    /// Генерирует случайное число с плавающей точкой в диапазоне [min, max]
    pub fn random_float(min: f32, max: f32) -> f32 {
        thread_rng().gen_range(min..=max)
    }
    
    /// Генерирует случайное булево значение
    pub fn random_bool() -> bool {
        thread_rng().gen()
    }
    
    /// Генерирует случайное булево значение с заданной вероятностью
    pub fn random_bool_with_probability(probability: f32) -> bool {
        thread_rng().gen_bool(probability as f64)
    }
    
    /// Выбирает случайный элемент из среза
    pub fn random_choice<T: Clone>(slice: &[T]) -> Option<T> {
        if slice.is_empty() {
            None
        } else {
            let index = thread_rng().gen_range(0..slice.len());
            Some(slice[index].clone())
        }
    }
    
    /// Перемешивает срез
    pub fn shuffle<T>(slice: &mut [T]) {
        slice.shuffle(&mut thread_rng());
    }
    
    /// Генерирует случайный байтовый массив заданной длины
    pub fn random_bytes(length: usize) -> Vec<u8> {
        (0..length).map(|_| thread_rng().gen()).collect()
    }
}

/// Утилиты для работы с валидацией
pub mod validation {
    use std::collections::HashMap;
    
    /// Валидатор
    pub struct Validator {
        errors: HashMap<String, Vec<String>>,
    }
    
    impl Validator {
        /// Создает новый валидатор
        pub fn new() -> Self {
            Self {
                errors: HashMap::new(),
            }
        }
        
        /// Проверяет, что значение не пустое
        pub fn validate_not_empty(&mut self, field: &str, value: &str, message: Option<&str>) -> &mut Self {
            if value.trim().is_empty() {
                let msg = message.unwrap_or("Field cannot be empty");
                self.add_error(field, msg);
            }
            self
        }
        
        /// Проверяет, что значение имеет минимальную длину
        pub fn validate_min_length(&mut self, field: &str, value: &str, min: usize, message: Option<&str>) -> &mut Self {
            if value.len() < min {
                let msg = message.unwrap_or_else(|| format!("Field must be at least {} characters long", min));
                self.add_error(field, &msg);
            }
            self
        }
        
        /// Проверяет, что значение имеет максимальную длину
        pub fn validate_max_length(&mut self, field: &str, value: &str, max: usize, message: Option<&str>) -> &mut Self {
            if value.len() > max {
                let msg = message.unwrap_or_else(|| format!("Field must be at most {} characters long", max));
                self.add_error(field, &msg);
            }
            self
        }
        
        /// Проверяет, что значение находится в диапазоне длин
        pub fn validate_length_range(&mut self, field: &str, value: &str, min: usize, max: usize, message: Option<&str>) -> &mut Self {
            if value.len() < min || value.len() > max {
                let msg = message.unwrap_or_else(|| format!("Field must be between {} and {} characters long", min, max));
                self.add_error(field, &msg);
            }
            self
        }
        
        /// Проверяет, что значение является числом
        pub fn validate_numeric(&mut self, field: &str, value: &str, message: Option<&str>) -> &mut Self {
            if !crate::utils::string::is_numeric(value) {
                let msg = message.unwrap_or("Field must be a number");
                self.add_error(field, msg);
            }
            self
        }
        
        /// Проверяет, что значение является целым числом
        pub fn validate_integer(&mut self, field: &str, value: &str, message: Option<&str>) -> &mut Self {
            if !crate::utils::string::is_integer(value) {
                let msg = message.unwrap_or("Field must be an integer");
                self.add_error(field, msg);
            }
            self
        }
        
        /// Проверяет, что значение является числом с плавающей точкой
        pub fn validate_float(&mut self, field: &str, value: &str, message: Option<&str>) -> &mut Self {
            if !crate::utils::string::is_float(value) {
                let msg = message.unwrap_or("Field must be a floating-point number");
                self.add_error(field, msg);
            }
            self
        }
        
        /// Проверяет, что значение находится в числовом диапазоне
        pub fn validate_number_range(&mut self, field: &str, value: &str, min: f64, max: f64, message: Option<&str>) -> &mut Self {
            if let Ok(num) = value.parse::<f64>() {
                if num < min || num > max {
                    let msg = message.unwrap_or(&format!("Field must be between {} and {}", min, max));
                    self.add_error(field, msg);
                }
            } else {
                let msg = message.unwrap_or("Field must be a number");
                self.add_error(field, msg);
            }
            self
        }
        
        /// Проверяет, что значение является email-адресом
        pub fn validate_email(&mut self, field: &str, value: &str, message: Option<&str>) -> &mut Self {
            if !crate::utils::string::is_email(value) {
                let msg = message.unwrap_or("Field must be a valid email address");
                self.add_error(field, msg);
            }
            self
        }
        
        /// Проверяет, что значение является URL
        pub fn validate_url(&mut self, field: &str, value: &str, message: Option<&str>) -> &mut Self {
            if !crate::utils::string::is_url(value) {
                let msg = message.unwrap_or("Field must be a valid URL");
                self.add_error(field, msg);
            }
            self
        }
        
        /// Проверяет, что значение соответствует регулярному выражению
        pub fn validate_regex(&mut self, field: &str, value: &str, regex: &str, message: Option<&str>) -> &mut Self {
            match Regex::new(regex) {
                Ok(re) => {
                    if !re.is_match(value) {
                        let msg = message.unwrap_or("Field does not match the required pattern");
                        self.add_error(field, msg);
                    }
                }
                Err(_) => {
                    self.add_error(field, "Invalid regular expression pattern");
                }
            }
            self
        }
        
        /// Проверяет, что значение находится в списке допустимых значений
        pub fn validate_in_list<T: AsRef<str>>(&mut self, field: &str, value: &str, list: &[T], message: Option<&str>) -> &mut Self {
            if !list.iter().any(|item| item.as_ref() == value) {
                let msg = message.unwrap_or("Field must be one of the allowed values");
                self.add_error(field, msg);
            }
            self
        }
        
        /// Проверяет, что значение не находится в списке запрещенных значений
        pub fn validate_not_in_list<T: AsRef<str>>(&mut self, field: &str, value: &str, list: &[T], message: Option<&str>) -> &mut Self {
            if list.iter().any(|item| item.as_ref() == value) {
                let msg = message.unwrap_or("Field must not be one of the forbidden values");
                self.add_error(field, msg);
            }
            self
        }
        
        /// Проверяет, что значение равно другому значению
        pub fn validate_equals(&mut self, field: &str, value: &str, other: &str, message: Option<&str>) -> &mut Self {
            if value != other {
                let msg = message.unwrap_or("Fields do not match");
                self.add_error(field, msg);
            }
            self
        }
        
        /// Проверяет, что значение не равно другому значению
        pub fn validate_not_equals(&mut self, field: &str, value: &str, other: &str, message: Option<&str>) -> &mut Self {
            if value == other {
                let msg = message.unwrap_or("Field must not be equal to the other field");
                self.add_error(field, msg);
            }
            self
        }
        
        /// Добавляет ошибку
        pub fn add_error(&mut self, field: &str, message: &str) -> &mut Self {
            self.errors.entry(field.to_string())
                .or_insert_with(Vec::new)
                .push(message.to_string());
            self
        }
        
        /// Проверяет, есть ли ошибки
        pub fn has_errors(&self) -> bool {
            !self.errors.is_empty()
        }
        
        /// Получает все ошибки
        pub fn get_errors(&self) -> &HashMap<String, Vec<String>> {
            &self.errors
        }
        
        /// Получает ошибки для конкретного поля
        pub fn get_field_errors(&self, field: &str) -> Option<&Vec<String>> {
            self.errors.get(field)
        }
        
        /// Получает первую ошибку для конкретного поля
        pub fn get_first_field_error(&self, field: &str) -> Option<&String> {
            self.errors.get(field).and_then(|errors| errors.first())
        }
        
        /// Получает все ошибки в виде плоского списка
        pub fn get_all_errors(&self) -> Vec<String> {
            let mut result = Vec::new();
            
            for (field, errors) in &self.errors {
                for error in errors {
                    result.push(format!("{}: {}", field, error));
                }
            }
            
            result
        }
        
        /// Очищает все ошибки
        pub fn clear(&mut self) -> &mut Self {
            self.errors.clear();
            self
        }
    }
}

/// Утилиты для работы с кэшированием
pub mod cache {
    use std::collections::HashMap;
    use std::hash::Hash;
    use std::time::{Duration, Instant};
    use std::sync::{Arc, Mutex};
    
    /// Кэш с временем жизни
    pub struct Cache<K, V> {
        data: HashMap<K, (V, Instant)>,
        ttl: Duration,
    }
    
    impl<K, V> Cache<K, V>
    where
        K: Eq + Hash + Clone,
        V: Clone,
    {
        /// Создает новый кэш с заданным временем жизни
        pub fn new(ttl: Duration) -> Self {
            Self {
                data: HashMap::new(),
                ttl,
            }
        }
        
        /// Добавляет значение в кэш
        pub fn set(&mut self, key: K, value: V) {
            self.data.insert(key, (value, Instant::now()));
        }
        
        /// Получает значение из кэша
        pub fn get(&mut self, key: &K) -> Option<V> {
            self.cleanup();
            
            self.data.get(key).map(|(value, _)| value.clone())
        }
        
        /// Проверяет, содержится ли ключ в кэше
        pub fn contains_key(&mut self, key: &K) -> bool {
            self.cleanup();
            
            self.data.contains_key(key)
        }
        
        /// Удаляет значение из кэша
        pub fn remove(&mut self, key: &K) -> Option<V> {
            self.data.remove(key).map(|(value, _)| value)
        }
        
        /// Очищает кэш
        pub fn clear(&mut self) {
            self.data.clear();
        }
        
        /// Очищает устаревшие записи
        pub fn cleanup(&mut self) {
            let now = Instant::now();
            self.data.retain(|_, (_, timestamp)| now.duration_since(*timestamp) < self.ttl);
        }
        
        /// Получает количество записей в кэше
        pub fn len(&self) -> usize {
            self.data.len()
        }
        
        /// Проверяет, пуст ли кэш
        pub fn is_empty(&self) -> bool {
            self.data.is_empty()
        }
        
        /// Получает все ключи в кэше
        pub fn keys(&self) -> Vec<K> {
            self.data.keys().cloned().collect()
        }
        
        /// Получает все значения в кэше
        pub fn values(&self) -> Vec<V> {
            self.data.values().map(|(value, _)| value.clone()).collect()
        }
        
        /// Получает все записи в кэше
        pub fn entries(&self) -> Vec<(K, V)> {
            self.data.iter()
                .map(|(key, (value, _))| (key.clone(), value.clone()))
                .collect()
        }
        
        /// Устанавливает время жизни кэша
        pub fn set_ttl(&mut self, ttl: Duration) {
            self.ttl = ttl;
        }
        
        /// Получает время жизни кэша
        pub fn get_ttl(&self) -> Duration {
            self.ttl
        }
    }
    
    /// Потокобезопасный кэш с временем жизни
    pub struct ThreadSafeCache<K, V> {
        cache: Arc<Mutex<Cache<K, V>>>,
    }
    
    impl<K, V> ThreadSafeCache<K, V>
    where
        K: Eq + Hash + Clone,
        V: Clone,
    {
        /// Создает новый потокобезопасный кэш с заданным временем жизни
        pub fn new(ttl: Duration) -> Self {
            Self {
                cache: Arc::new(Mutex::new(Cache::new(ttl))),
            }
        }
        
        /// Добавляет значение в кэш
        pub fn set(&self, key: K, value: V) {
            let mut cache = self.cache.lock().unwrap();
            cache.set(key, value);
        }
        
        /// Получает значение из кэша
        pub fn get(&self, key: &K) -> Option<V> {
            let mut cache = self.cache.lock().unwrap();
            cache.get(key)
        }
        
        /// Проверяет, содержится ли ключ в кэше
        pub fn contains_key(&self, key: &K) -> bool {
            let mut cache = self.cache.lock().unwrap();
            cache.contains_key(key)
        }
        
        /// Удаляет значение из кэша
        pub fn remove(&self, key: &K) -> Option<V> {
            let mut cache = self.cache.lock().unwrap();
            cache.remove(key)
        }
        
        /// Очищает кэш
        pub fn clear(&self) {
            let mut cache = self.cache.lock().unwrap();
            cache.clear();
        }
        
        /// Очищает устаревшие записи
        pub fn cleanup(&self) {
            let mut cache = self.cache.lock().unwrap();
            cache.cleanup();
        }
        
        /// Получает количество записей в кэше
        pub fn len(&self) -> usize {
            let cache = self.cache.lock().unwrap();
            cache.len()
        }
        
        /// Проверяет, пуст ли кэш
        pub fn is_empty(&self) -> bool {
            let cache = self.cache.lock().unwrap();
            cache.is_empty()
        }
        
        /// Получает все ключи в кэше
        pub fn keys(&self) -> Vec<K> {
            let cache = self.cache.lock().unwrap();
            cache.keys()
        }
        
        /// Получает все значения в кэше
        pub fn values(&self) -> Vec<V> {
            let cache = self.cache.lock().unwrap();
            cache.values()
        }
        
        /// Получает все записи в кэше
        pub fn entries(&self) -> Vec<(K, V)> {
            let cache = self.cache.lock().unwrap();
            cache.entries()
        }
        
        /// Устанавливает время жизни кэша
        pub fn set_ttl(&self, ttl: Duration) {
            let mut cache = self.cache.lock().unwrap();
            cache.set_ttl(ttl);
        }
        
        /// Получает время жизни кэша
        pub fn get_ttl(&self) -> Duration {
            let cache = self.cache.lock().unwrap();
            cache.get_ttl()
        }
    }
}

/// Утилиты для работы с метриками
pub mod metrics {
    use std::collections::HashMap;
    use std::sync::{Arc, Mutex};
    use std::time::{Duration, Instant};
    
    /// Тип метрики
    #[derive(Debug, Clone, Copy, PartialEq, Eq)]
    pub enum MetricType {
        /// Счетчик
        Counter,
        /// Измеритель
        Gauge,
        /// Гистограмма
        Histogram,
        /// Таймер
        Timer,
    }
    
    /// Метрика
    #[derive(Debug, Clone)]
    pub struct Metric {
        /// Имя метрики
        pub name: String,
        /// Тип метрики
        pub metric_type: MetricType,
        /// Значение метрики
        pub value: f64,
        /// Метки метрики
        pub labels: HashMap<String, String>,
        /// Время создания метрики
        pub created_at: Instant,
        /// Время последнего обновления метрики
        pub updated_at: Instant,
    }
    
    impl Metric {
        /// Создает новую метрику
        pub fn new(name: &str, metric_type: MetricType, value: f64) -> Self {
            let now = Instant::now();
            
            Self {
                name: name.to_string(),
                metric_type,
                value,
                labels: HashMap::new(),
                created_at: now,
                updated_at: now,
            }
        }
        
        /// Добавляет метку к метрике
        pub fn with_label(mut self, key: &str, value: &str) -> Self {
            self.labels.insert(key.to_string(), value.to_string());
            self
        }
        
        /// Добавляет метки к метрике
        pub fn with_labels(mut self, labels: HashMap<String, String>) -> Self {
            self.labels.extend(labels);
            self
        }
        
        /// Обновляет значение метрики
        pub fn update(&mut self, value: f64) {
            self.value = value;
            self.updated_at = Instant::now();
        }
        
        /// Увеличивает значение метрики
        pub fn increment(&mut self, value: f64) {
            self.value += value;
            self.updated_at = Instant::now();
        }
        
        /// Уменьшает значение метрики
        pub fn decrement(&mut self, value: f64) {
            self.value -= value;
            self.updated_at = Instant::now();
        }
        
        /// Получает время с момента создания метрики
        pub fn elapsed_since_creation(&self) -> Duration {
            self.created_at.elapsed()
        }
        
        /// Получает время с момента последнего обновления метрики
        pub fn elapsed_since_update(&self) -> Duration {
            self.updated_at.elapsed()
        }
    }
    
    /// Реестр метрик
    pub struct MetricRegistry {
        metrics: HashMap<String, Metric>,
    }
    
    impl MetricRegistry {
        /// Создает новый реестр метрик
        pub fn new() -> Self {
            Self {
                metrics: HashMap::new(),
            }
        }
        
        /// Регистрирует метрику
        pub fn register(&mut self, metric: Metric) {
            self.metrics.insert(metric.name.clone(), metric);
        }
        
        /// Получает метрику по имени
        pub fn get(&self, name: &str) -> Option<&Metric> {
            self.metrics.get(name)
        }
        
        /// Получает изменяемую метрику по имени
        pub fn get_mut(&mut self, name: &str) -> Option<&mut Metric> {
            self.metrics.get_mut(name)
        }
        
        /// Удаляет метрику по имени
        pub fn remove(&mut self, name: &str) -> Option<Metric> {
            self.metrics.remove(name)
        }
        
        /// Очищает реестр метрик
        pub fn clear(&mut self) {
            self.metrics.clear();
        }
        
        /// Получает количество метрик в реестре
        pub fn len(&self) -> usize {
            self.metrics.len()
        }
        
        /// Проверяет, пуст ли реестр метрик
        pub fn is_empty(&self) -> bool {
            self.metrics.is_empty()
        }
        
        /// Получает все метрики в реестре
        pub fn get_all(&self) -> Vec<&Metric> {
            self.metrics.values().collect()
        }
        
        /// Получает все метрики заданного типа
        pub fn get_by_type(&self, metric_type: MetricType) -> Vec<&Metric> {
            self.metrics.values()
                .filter(|m| m.metric_type == metric_type)
                .collect()
        }
        
        /// Получает все метрики с заданной меткой
        pub fn get_by_label(&self, key: &str, value: &str) -> Vec<&Metric> {
            self.metrics.values()
                .filter(|m| m.labels.get(key).map_or(false, |v| v == value))
                .collect()
        }
        
        /// Создает и регистрирует счетчик
        pub fn create_counter(&mut self, name: &str) -> &mut Metric {
            let metric = Metric::new(name, MetricType::Counter, 0.0);
            self.metrics.insert(name.to_string(), metric);
            self.metrics.get_mut(name).unwrap()
        }
        
        /// Создает и регистрирует измеритель
        pub fn create_gauge(&mut self, name: &str, value: f64) -> &mut Metric {
            let metric = Metric::new(name, MetricType::Gauge, value);
            self.metrics.insert(name.to_string(), metric);
            self.metrics.get_mut(name).unwrap()
        }
        
        /// Создает и регистрирует гистограмму
        pub fn create_histogram(&mut self, name: &str) -> &mut Metric {
            let metric = Metric::new(name, MetricType::Histogram, 0.0);
            self.metrics.insert(name.to_string(), metric);
            self.metrics.get_mut(name).unwrap()
        }
        
        /// Создает и регистрирует таймер
        pub fn create_timer(&mut self, name: &str) -> &mut Metric {
            let metric = Metric::new(name, MetricType::Timer, 0.0);
            self.metrics.insert(name.to_string(), metric);
            self.metrics.get_mut(name).unwrap()
        }
        
        /// Увеличивает счетчик
        pub fn increment_counter(&mut self, name: &str, value: f64) -> anyhow::Result<()> {
            let metric = self.metrics.get_mut(name)
                .ok_or_else(|| anyhow::anyhow!("Metric not found: {}", name))?;
            
            if metric.metric_type != MetricType::Counter {
                return Err(anyhow::anyhow!("Metric is not a counter: {}", name));
            }
            
            metric.increment(value);
            Ok(())
        }
        
        /// Уменьшает счетчик
        pub fn decrement_counter(&mut self, name: &str, value: f64) -> anyhow::Result<()> {
            let metric = self.metrics.get_mut(name)
                .ok_or_else(|| anyhow::anyhow!("Metric not found: {}", name))?;
            
            if metric.metric_type != MetricType::Counter {
                return Err(anyhow::anyhow!("Metric is not a counter: {}", name));
            }
            
            metric.decrement(value);
            Ok(())
        }
        
        /// Устанавливает значение измерителя
        pub fn set_gauge(&mut self, name: &str, value: f64) -> anyhow::Result<()> {
            let metric = self.metrics.get_mut(name)
                .ok_or_else(|| anyhow::anyhow!("Metric not found: {}", name))?;
            
            if metric.metric_type != MetricType::Gauge {
                return Err(anyhow::anyhow!("Metric is not a gauge: {}", name));
            }
            
            metric.update(value);
            Ok(())
        }
        
        /// Добавляет значение в гистограмму
        pub fn observe_histogram(&mut self, name: &str, value: f64) -> anyhow::Result<()> {
            let metric = self.metrics.get_mut(name)
                .ok_or_else(|| anyhow::anyhow!("Metric not found: {}", name))?;
            
            if metric.metric_type != MetricType::Histogram {
                return Err(anyhow::anyhow!("Metric is not a histogram: {}", name));
            }
            
            // В реальной реализации здесь была бы логика добавления значения в гистограмму
            // Для простоты просто обновляем значение
            metric.update(value);
            Ok(())
        }
        
        /// Записывает время выполнения функции
        pub fn record_timer<F, T>(&mut self, name: &str, f: F) -> anyhow::Result<T>
        where
            F: FnOnce() -> T,
        {
            let metric = self.metrics.get_mut(name)
                .ok_or_else(|| anyhow::anyhow!("Metric not found: {}", name))?;
            
            if metric.metric_type != MetricType::Timer {
                return Err(anyhow::anyhow!("Metric is not a timer: {}", name));
            }
            
            let start = Instant::now();
            let result = f();
            let duration = start.elapsed();
            
            metric.update(duration.as_secs_f64());
            
            Ok(result)
        }
        
        /// Записывает время выполнения асинхронной функции
        pub async fn record_timer_async<F, T>(&mut self, name: &str, f: F) -> anyhow::Result<T>
        where
            F: std::future::Future<Output = T>,
        {
            let metric = self.metrics.get_mut(name)
                .ok_or_else(|| anyhow::anyhow!("Metric not found: {}", name))?;
            
            if metric.metric_type != MetricType::Timer {
                return Err(anyhow::anyhow!("Metric is not a timer: {}", name));
            }
            
            let start = Instant::now();
            let result = f.await;
            let duration = start.elapsed();
            
            metric.update(duration.as_secs_f64());
            
            Ok(result)
        }
    }
    
    /// Потокобезопасный реестр метрик
    pub struct ThreadSafeMetricRegistry {
        registry: Arc<Mutex<MetricRegistry>>,
    }
    
    impl ThreadSafeMetricRegistry {
        /// Создает новый потокобезопасный реестр метрик
        pub fn new() -> Self {
            Self {
                registry: Arc::new(Mutex::new(MetricRegistry::new())),
            }
        }
        
        /// Регистрирует метрику
        pub fn register(&self, metric: Metric) {
            let mut registry = self.registry.lock().unwrap();
            registry.register(metric);
        }
        
        /// Получает метрику по имени
        pub fn get(&self, name: &str) -> Option<Metric> {
            let registry = self.registry.lock().unwrap();
            registry.get(name).cloned()
        }
        
        /// Удаляет метрику по имени
        pub fn remove(&self, name: &str) -> Option<Metric> {
            let mut registry = self.registry.lock().unwrap();
            registry.remove(name)
        }
        
        /// Очищает реестр метрик
        pub fn clear(&self) {
            let mut registry = self.registry.lock().unwrap();
            registry.clear();
        }
        
        /// Получает количество метрик в реестре
        pub fn len(&self) -> usize {
            let registry = self.registry.lock().unwrap();
            registry.len()
        }
        
        /// Проверяет, пуст ли реестр метрик
        pub fn is_empty(&self) -> bool {
            let registry = self.registry.lock().unwrap();
            registry.is_empty()
        }
        
        /// Получает все метрики в реестре
        pub fn get_all(&self) -> Vec<Metric> {
            let registry = self.registry.lock().unwrap();
            registry.get_all().iter().map(|m| (*m).clone()).collect()
        }
        
        /// Получает все метрики заданного типа
        pub fn get_by_type(&self, metric_type: MetricType) -> Vec<Metric> {
            let registry = self.registry.lock().unwrap();
            registry.get_by_type(metric_type).iter().map(|m| (*m).clone()).collect()
        }
        
        /// Получает все метрики с заданной меткой
        pub fn get_by_label(&self, key: &str, value: &str) -> Vec<Metric> {
            let registry = self.registry.lock().unwrap();
            registry.get_by_label(key, value).iter().map(|m| (*m).clone()).collect()
        }
        
        /// Создает и регистрирует счетчик
        pub fn create_counter(&self, name: &str) {
            let mut registry = self.registry.lock().unwrap();
            registry.create_counter(name);
        }
        
        /// Создает и регистрирует измеритель
        pub fn create_gauge(&self, name: &str, value: f64) {
            let mut registry = self.registry.lock().unwrap();
            registry.create_gauge(name, value);
        }
        
        /// Создает и регистрирует гистограмму
        pub fn create_histogram(&self, name: &str) {
            let mut registry = self.registry.lock().unwrap();
            registry.create_histogram(name);
        }
        
        /// Создает и регистрирует таймер
        pub fn create_timer(&self, name: &str) {
            let mut registry = self.registry.lock().unwrap();
            registry.create_timer(name);
        }
        
        /// Увеличивает счетчик
        pub fn increment_counter(&self, name: &str, value: f64) -> anyhow::Result<()> {
            let mut registry = self.registry.lock().unwrap();
            registry.increment_counter(name, value)
        }
        
        /// Уменьшает счетчик
        pub fn decrement_counter(&self, name: &str, value: f64) -> anyhow::Result<()> {
            let mut registry = self.registry.lock().unwrap();
            registry.decrement_counter(name, value)
        }
        
        /// Устанавливает значение измерителя
        pub fn set_gauge(&self, name: &str, value: f64) -> anyhow::Result<()> {
            let mut registry = self.registry.lock().unwrap();
            registry.set_gauge(name, value)
        }
        
        /// Добавляет значение в гистограмму
        pub fn observe_histogram(&self, name: &str, value: f64) -> anyhow::Result<()> {
            let mut registry = self.registry.lock().unwrap();
            registry.observe_histogram(name, value)
        }
        
        /// Записывает время выполнения функции
        pub fn record_timer<F, T>(&self, name: &str, f: F) -> anyhow::Result<T>
        where
            F: FnOnce() -> T,
        {
            let mut registry = self.registry.lock().unwrap();
            registry.record_timer(name, f)
        }
        
        /// Записывает время выполнения асинхронной функции
        pub async fn record_timer_async<F, T>(&self, name: &str, f: F) -> anyhow::Result<T>
        where
            F: std::future::Future<Output = T>,
        {
            let start = Instant::now();
            let result = f.await;
            let duration = start.elapsed();
            
            let mut registry = self.registry.lock().unwrap();
            if let Some(metric) = registry.get_mut(name) {
                if metric.metric_type == MetricType::Timer {
                    metric.update(duration.as_secs_f64());
                } else {
                    return Err(anyhow::anyhow!("Metric is not a timer: {}", name));
                }
            } else {
                return Err(anyhow::anyhow!("Metric not found: {}", name));
            }
            
            Ok(result)
        }
    }
}

