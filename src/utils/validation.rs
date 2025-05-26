use std::collections::HashMap;
use regex::Regex;
use anyhow::Result;

#[derive(Debug, Clone)]
pub struct ValidationError {
    pub field: String,
    pub message: String,
}

#[derive(Debug)]
pub struct Validator {
    errors: HashMap<String, String>,
}

impl Validator {
    pub fn new() -> Self {
        Self {
            errors: HashMap::new(),
        }
    }

    pub fn add_error(&mut self, field: &str, message: &str) {
        self.errors.insert(field.to_string(), message.to_string());
    }

    pub fn has_errors(&self) -> bool {
        !self.errors.is_empty()
    }

    pub fn get_errors(&self) -> &HashMap<String, String> {
        &self.errors
    }

    pub fn validate_min_length(&mut self, field: &str, value: &str, min: usize, message: Option<&str>) -> &mut Self {
        if value.len() < min {
            let msg = message.unwrap_or_else(|| format!("Field must be at least {} characters long", min));
            self.add_error(field, &msg);
        }
        self
    }

    pub fn validate_max_length(&mut self, field: &str, value: &str, max: usize, message: Option<&str>) -> &mut Self {
        if value.len() > max {
            let msg = message.unwrap_or_else(|| format!("Field must be at most {} characters long", max));
            self.add_error(field, &msg);
        }
        self
    }

    pub fn validate_length_range(&mut self, field: &str, value: &str, min: usize, max: usize, message: Option<&str>) -> &mut Self {
        if value.len() < min || value.len() > max {
            let msg = message.unwrap_or_else(|| format!("Field must be between {} and {} characters long", min, max));
            self.add_error(field, &msg);
        }
        self
    }

    pub fn validate_number_range(&mut self, field: &str, value: &str, min: f64, max: f64, message: Option<&str>) -> &mut Self {
        if let Ok(num) = value.parse::<f64>() {
            if num < min || num > max {
                let msg = message.unwrap_or_else(|| format!("Field must be between {} and {}", min, max));
                self.add_error(field, &msg);
            }
        } else {
            let msg = message.unwrap_or("Field must be a number");
            self.add_error(field, msg);
        }
        self
    }
}

pub fn validate_email(email: &str) -> bool {
    let email_regex = Regex::new(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$").unwrap();
    email_regex.is_match(email)
}

pub fn validate_username(username: &str) -> bool {
    let username_regex = Regex::new(r"^[a-zA-Z0-9_-]{3,16}$").unwrap();
    username_regex.is_match(username)
}

pub fn validate_password(password: &str) -> bool {
    let password_regex = Regex::new(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$").unwrap();
    password_regex.is_match(password)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_email_validation() {
        assert!(validate_email("test@example.com"));
        assert!(!validate_email("invalid-email"));
    }

    #[test]
    fn test_username_validation() {
        assert!(validate_username("user123"));
        assert!(!validate_username("a")); // Too short
        assert!(!validate_username("invalid@username")); // Invalid characters
    }

    #[test]
    fn test_password_validation() {
        assert!(validate_password("Password123"));
        assert!(!validate_password("short")); // Too short
        assert!(!validate_password("password")); // No numbers
    }

    #[test]
    fn test_validator() {
        let mut validator = Validator::new();
        validator
            .validate_min_length("username", "a", 3, None)
            .validate_max_length("email", "test@example.com", 10, None);

        assert!(validator.has_errors());
        assert_eq!(validator.get_errors().len(), 2);
    }
} 