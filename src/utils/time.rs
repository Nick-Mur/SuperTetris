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

/// Получение текущего времени в наносекундах
pub fn get_current_timestamp_nanos() -> i64 {
    Utc::now().timestamp_nanos_opt().unwrap_or(0)
}

/// Получение текущего времени в миллисекундах
pub fn get_current_timestamp_millis() -> i64 {
    Utc::now().timestamp_millis()
}

/// Конвертация DateTime в наносекунды
pub fn datetime_to_nanos(datetime: DateTime<Utc>) -> i64 {
    datetime.timestamp_nanos_opt().unwrap_or(0)
}

/// Конвертация наносекунд в DateTime
pub fn nanos_to_datetime(nanos: i64) -> DateTime<Utc> {
    DateTime::from_timestamp_nanos(nanos).unwrap_or_else(|| Utc::now())
}

/// Измерение времени выполнения функции
pub fn measure_execution_time<F, T>(f: F) -> (T, Duration)
where
    F: FnOnce() -> T,
{
    let start = Instant::now();
    let result = f();
    let duration = start.elapsed();
    (result, duration)
}

/// Форматирование длительности в читаемый вид
pub fn format_duration(duration: Duration) -> String {
    if duration.as_secs() > 0 {
        format!("{:.2}s", duration.as_secs_f64())
    } else if duration.as_millis() > 0 {
        format!("{}ms", duration.as_millis())
    } else if duration.as_micros() > 0 {
        format!("{}µs", duration.as_micros())
    } else {
        format!("{}ns", duration.as_nanos())
    }
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