use uuid::Uuid;

/// Генерация нового UUID v4
pub fn generate_uuid() -> Uuid {
    Uuid::new_v4()
}

/// Генерация нового UUID v4 в виде строки
pub fn generate_uuid_string() -> String {
    generate_uuid().to_string()
}

/// Проверка валидности UUID строки
pub fn is_valid_uuid(uuid_str: &str) -> bool {
    Uuid::parse_str(uuid_str).is_ok()
}

/// Парсинг UUID из строки
pub fn parse_uuid(uuid_str: &str) -> Option<Uuid> {
    Uuid::parse_str(uuid_str).ok()
}

/// Генерация UUID на основе имени (v5)
pub fn generate_name_based_uuid(name: &str) -> Uuid {
    let namespace = Uuid::NAMESPACE_DNS;
    Uuid::new_v5(&namespace, name.as_bytes())
} 