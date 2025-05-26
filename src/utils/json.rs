use serde::{Serialize, Deserialize};
use serde_json::{Value, json};
use anyhow::{Result, Context};

/// Сериализация объекта в JSON строку
pub fn to_json<T: Serialize>(value: &T) -> Result<String> {
    serde_json::to_string_pretty(value)
        .context("Failed to serialize to JSON")
}

/// Десериализация JSON строки в объект
pub fn from_json<T: Deserialize<'static>>(json_str: &str) -> Result<T> {
    serde_json::from_str(json_str)
        .context("Failed to deserialize from JSON")
}

/// Парсинг JSON строки в Value
pub fn parse_json(json_str: &str) -> Result<Value> {
    serde_json::from_str(json_str)
        .context("Failed to parse JSON")
}

/// Создание JSON объекта с указанными полями
pub fn create_json_object(fields: &[(&str, Value)]) -> Value {
    let mut obj = json!({});
    for (key, value) in fields {
        obj[key] = value.clone();
    }
    obj
}

/// Получение значения из JSON по пути
pub fn get_json_value(json: &Value, path: &str) -> Option<&Value> {
    let parts: Vec<&str> = path.split('.').collect();
    let mut current = json;
    
    for part in parts {
        current = current.get(part)?;
    }
    
    Some(current)
}

/// Установка значения в JSON по пути
pub fn set_json_value(json: &mut Value, path: &str, value: Value) -> Result<()> {
    let parts: Vec<&str> = path.split('.').collect();
    let mut current = json;
    
    for (i, part) in parts.iter().enumerate() {
        if i == parts.len() - 1 {
            current[part] = value;
        } else {
            if !current.is_object() {
                *current = json!({});
            }
            current = &mut current[part];
        }
    }
    
    Ok(())
}

pub fn to_pretty_json<T: Serialize>(value: &T) -> Result<String> {
    Ok(serde_json::to_string_pretty(value)?)
}

pub fn validate_json(json: &str) -> bool {
    serde_json::from_str::<serde_json::Value>(json).is_ok()
} 