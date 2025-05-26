import re
from typing import Dict, Optional, List
from dataclasses import dataclass

@dataclass
class ValidationError:
    """Ошибка валидации"""
    field: str
    message: str

class Validator:
    """Валидатор полей"""
    
    def __init__(self):
        self.errors: Dict[str, str] = {}
        
    def add_error(self, field: str, message: str) -> None:
        """Добавить ошибку"""
        self.errors[field] = message
        
    def has_errors(self) -> bool:
        """Проверить наличие ошибок"""
        return bool(self.errors)
        
    def get_errors(self) -> Dict[str, str]:
        """Получить все ошибки"""
        return self.errors
        
    def validate_min_length(self, field: str, value: str, min_length: int, message: Optional[str] = None) -> 'Validator':
        """Проверить минимальную длину"""
        if len(value) < min_length:
            msg = message or f"Field must be at least {min_length} characters long"
            self.add_error(field, msg)
        return self
        
    def validate_max_length(self, field: str, value: str, max_length: int, message: Optional[str] = None) -> 'Validator':
        """Проверить максимальную длину"""
        if len(value) > max_length:
            msg = message or f"Field must be at most {max_length} characters long"
            self.add_error(field, msg)
        return self
        
    def validate_length_range(self, field: str, value: str, min_length: int, max_length: int, message: Optional[str] = None) -> 'Validator':
        """Проверить длину в диапазоне"""
        if len(value) < min_length or len(value) > max_length:
            msg = message or f"Field must be between {min_length} and {max_length} characters long"
            self.add_error(field, msg)
        return self
        
    def validate_number_range(self, field: str, value: str, min_value: float, max_value: float, message: Optional[str] = None) -> 'Validator':
        """Проверить число в диапазоне"""
        try:
            num = float(value)
            if num < min_value or num > max_value:
                msg = message or f"Field must be between {min_value} and {max_value}"
                self.add_error(field, msg)
        except ValueError:
            msg = message or "Field must be a number"
            self.add_error(field, msg)
        return self

def validate_email(email: str) -> bool:
    """Проверить email"""
    email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    return bool(email_regex.match(email))

def validate_username(username: str) -> bool:
    """Проверить имя пользователя"""
    username_regex = re.compile(r"^[a-zA-Z0-9_-]{3,16}$")
    return bool(username_regex.match(username))

def validate_password(password: str) -> bool:
    """Проверить пароль"""
    password_regex = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$")
    return bool(password_regex.match(password))

# Тесты
if __name__ == "__main__":
    # Тест валидации email
    assert validate_email("test@example.com")
    assert not validate_email("invalid-email")
    
    # Тест валидации имени пользователя
    assert validate_username("user123")
    assert not validate_username("a")  # Слишком короткое
    assert not validate_username("invalid@username")  # Недопустимые символы
    
    # Тест валидации пароля
    assert validate_password("Password123")
    assert not validate_password("short")  # Слишком короткий
    assert not validate_password("password")  # Нет цифр
    
    # Тест валидатора
    validator = Validator()
    validator.validate_min_length("username", "a", 3)
    validator.validate_max_length("email", "test@example.com", 10)
    
    assert validator.has_errors()
    assert len(validator.get_errors()) == 2 