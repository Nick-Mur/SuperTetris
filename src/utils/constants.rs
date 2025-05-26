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

// Основные константы приложения
pub const APP_NAME: &str = "Tetris Towers";
pub const APP_VERSION: &str = env!("CARGO_PKG_VERSION");

// Константы для игровой логики
pub const DEFAULT_GAME_WIDTH: i32 = 10;
pub const DEFAULT_GAME_HEIGHT: i32 = 20;
pub const DEFAULT_BLOCK_SIZE: i32 = 30;
pub const DEFAULT_GAME_SPEED: f32 = 1.0;

// Константы для сетевого взаимодействия
pub const DEFAULT_WS_PORT: u16 = 8081;
pub const DEFAULT_HEARTBEAT_INTERVAL: u64 = 30;
pub const DEFAULT_CLEANUP_INTERVAL: u64 = 300;

// Константы для физики
pub const GRAVITY: f32 = 9.81;
pub const FRICTION: f32 = 0.1;
pub const COLLISION_THRESHOLD: f32 = 0.01;

// Константы для логирования
pub const LOG_FILE_PATH: &str = "logs/app.log"; 