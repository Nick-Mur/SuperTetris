# Руководство по безопасности

## Аутентификация

### JWT токены

```python
# src/python_server/auth.py
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class JWTBearer:
    def __init__(self):
        self.security = HTTPBearer()
        self.secret_key = "your-secret-key"
        self.algorithm = "HS256"

    def create_token(self, user_id: str) -> str:
        payload = {
            "exp": datetime.utcnow() + timedelta(days=1),
            "iat": datetime.utcnow(),
            "sub": user_id
        }
        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm
        )

    def verify_token(self, credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> str:
        try:
            payload = jwt.decode(
                credentials.credentials,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
```

### OAuth 2.0

```python
# src/python_server/oauth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
```

### Двухфакторная аутентификация

```python
# src/python_server/2fa.py
import pyotp
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer

router = APIRouter()
security = HTTPBearer()

@router.post("/2fa/generate")
async def generate_2fa(user_id: str):
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    return {
        "secret": secret,
        "qr_code": totp.provisioning_uri(
            user_id,
            issuer_name="Tetris"
        )
    }

@router.post("/2fa/verify")
async def verify_2fa(
    user_id: str,
    token: str,
    credentials: HTTPBearer = Depends(security)
):
    secret = get_user_2fa_secret(user_id)
    totp = pyotp.TOTP(secret)
    if not totp.verify(token):
        raise HTTPException(
            status_code=401,
            detail="Invalid 2FA token"
        )
    return {"status": "success"}
```

## Авторизация

### RBAC (Role-Based Access Control)

```python
# src/python_server/rbac.py
from enum import Enum
from fastapi import Depends, HTTPException
from typing import List

class Role(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"

class RBAC:
    def __init__(self):
        self.roles = {
            Role.ADMIN: ["*"],
            Role.MODERATOR: ["read", "write"],
            Role.USER: ["read"]
        }

    def check_permission(
        self,
        role: Role,
        permission: str
    ) -> bool:
        if role not in self.roles:
            return False
        return (
            "*" in self.roles[role] or
            permission in self.roles[role]
        )

def require_permission(permission: str):
    def decorator(func):
        async def wrapper(
            role: Role = Depends(get_current_role),
            *args,
            **kwargs
        ):
            rbac = RBAC()
            if not rbac.check_permission(role, permission):
                raise HTTPException(
                    status_code=403,
                    detail="Permission denied"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### ACL (Access Control Lists)

```python
# src/python_server/acl.py
from fastapi import Depends, HTTPException
from typing import Dict, List

class ACL:
    def __init__(self):
        self.acls: Dict[str, List[str]] = {}

    def add_permission(
        self,
        resource: str,
        user_id: str,
        permission: str
    ):
        if resource not in self.acls:
            self.acls[resource] = []
        self.acls[resource].append(f"{user_id}:{permission}")

    def check_permission(
        self,
        resource: str,
        user_id: str,
        permission: str
    ) -> bool:
        if resource not in self.acls:
            return False
        return f"{user_id}:{permission}" in self.acls[resource]

def require_resource_permission(
    resource: str,
    permission: str
):
    def decorator(func):
        async def wrapper(
            user_id: str = Depends(get_current_user),
            *args,
            **kwargs
        ):
            acl = ACL()
            if not acl.check_permission(
                resource,
                user_id,
                permission
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Permission denied"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## Шифрование

### TLS/SSL

```python
# src/python_server/ssl.py
import ssl
from fastapi import FastAPI
import uvicorn

app = FastAPI()

if __name__ == "__main__":
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(
        "cert.pem",
        keyfile="key.pem"
    )
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem"
    )
```

### Асимметричное шифрование

```python
# src/python_server/encryption.py
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    
    return {
        "private_key": private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ),
        "public_key": public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    }

def encrypt_message(message: str, public_key: bytes) -> bytes:
    public_key = serialization.load_pem_public_key(
        public_key,
        backend=default_backend()
    )
    return public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def decrypt_message(
    encrypted_message: bytes,
    private_key: bytes
) -> str:
    private_key = serialization.load_pem_private_key(
        private_key,
        password=None,
        backend=default_backend()
    )
    return private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    ).decode()
```

### Симметричное шифрование

```python
# src/python_server/symmetric.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

def generate_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_data(data: str, key: bytes) -> bytes:
    f = Fernet(key)
    return f.encrypt(data.encode())

def decrypt_data(encrypted_data: bytes, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()
```

## Безопасность данных

### Хеширование

```python
# src/python_server/hashing.py
from passlib.context import CryptContext
from hashlib import sha256
import hmac

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_data(data: str, key: str) -> str:
    return hmac.new(
        key.encode(),
        data.encode(),
        sha256
    ).hexdigest()
```

### Цифровые подписи

```python
# src/python_server/signatures.py
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend

def sign_message(message: str, private_key: bytes) -> bytes:
    private_key = serialization.load_pem_private_key(
        private_key,
        password=None,
        backend=default_backend()
    )
    return private_key.sign(
        message.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

def verify_signature(
    message: str,
    signature: bytes,
    public_key: bytes
) -> bool:
    public_key = serialization.load_pem_public_key(
        public_key,
        backend=default_backend()
    )
    try:
        public_key.verify(
            signature,
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except:
        return False
```

## Безопасность API

### Rate Limiting

```python
# src/python_server/rate_limit.py
from fastapi import HTTPException
from datetime import datetime, timedelta
from typing import Dict, Tuple

class RateLimiter:
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}

    def check_rate_limit(self, user_id: str) -> bool:
        now = datetime.utcnow()
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Удаление старых запросов
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < timedelta(minutes=1)
        ]
        
        # Проверка лимита
        if len(self.requests[user_id]) >= self.requests_per_minute:
            return False
        
        # Добавление нового запроса
        self.requests[user_id].append(now)
        return True

def rate_limit(requests_per_minute: int):
    limiter = RateLimiter(requests_per_minute)
    
    def decorator(func):
        async def wrapper(
            user_id: str = Depends(get_current_user),
            *args,
            **kwargs
        ):
            if not limiter.check_rate_limit(user_id):
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### CORS

```python
# src/python_server/cors.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tetris.example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Защита от атак

```python
# src/python_server/security.py
from fastapi import FastAPI, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

# HTTPS редирект
app.add_middleware(HTTPSRedirectMiddleware)

# Доверенные хосты
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["tetris.example.com"]
)

# Сжатие
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Защита от XSS
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

## Мониторинг безопасности

### Логирование

```python
# src/python_server/logging.py
import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime

class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger("security")
        self.logger.setLevel(logging.INFO)
        
        handler = RotatingFileHandler(
            "logs/security.log",
            maxBytes=10000000,
            backupCount=5
        )
        
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)

    def log_security_event(
        self,
        event_type: str,
        user_id: str,
        details: dict
    ):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "details": details
        }
        self.logger.info(json.dumps(log_entry))
```

### Алерты

```python
# src/python_server/alerts.py
from fastapi import BackgroundTasks
import smtplib
from email.mime.text import MIMEText
from typing import List

class SecurityAlert:
    def __init__(self):
        self.alert_recipients: List[str] = []
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_username = "alerts@tetris.example.com"
        self.smtp_password = "your-password"

    def send_alert(
        self,
        background_tasks: BackgroundTasks,
        alert_type: str,
        details: dict
    ):
        background_tasks.add_task(
            self._send_email,
            alert_type,
            details
        )

    def _send_email(self, alert_type: str, details: dict):
        msg = MIMEText(
            f"Security Alert: {alert_type}\n\n"
            f"Details: {json.dumps(details, indent=2)}"
        )
        msg["Subject"] = f"Security Alert: {alert_type}"
        msg["From"] = self.smtp_username
        msg["To"] = ", ".join(self.alert_recipients)

        with smtplib.SMTP(
            self.smtp_server,
            self.smtp_port
        ) as server:
            server.starttls()
            server.login(
                self.smtp_username,
                self.smtp_password
            )
            server.send_message(msg)
```

## Аудит

### Аудит действий

```python
# src/python_server/audit.py
from fastapi import Depends
from typing import Dict, Any
import json
from datetime import datetime

class AuditLog:
    def __init__(self):
        self.log_file = "logs/audit.log"

    def log_action(
        self,
        user_id: str,
        action: str,
        resource: str,
        details: Dict[str, Any]
    ):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "details": details
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

def audit_action(action: str, resource: str):
    def decorator(func):
        async def wrapper(
            user_id: str = Depends(get_current_user),
            *args,
            **kwargs
        ):
            audit_log = AuditLog()
            result = await func(*args, **kwargs)
            
            audit_log.log_action(
                user_id,
                action,
                resource,
                {
                    "args": args,
                    "kwargs": kwargs,
                    "result": result
                }
            )
            
            return result
        return wrapper
    return decorator
```

### Отчеты по безопасности

```python
# src/python_server/security_reports.py
from fastapi import APIRouter
from typing import List, Dict
import pandas as pd
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/security/reports/activity")
async def get_activity_report(
    start_date: datetime,
    end_date: datetime
) -> Dict:
    # Чтение логов
    logs = []
    with open("logs/security.log", "r") as f:
        for line in f:
            log = json.loads(line)
            if start_date <= datetime.fromisoformat(log["timestamp"]) <= end_date:
                logs.append(log)
    
    # Анализ данных
    df = pd.DataFrame(logs)
    report = {
        "total_events": len(df),
        "events_by_type": df["event_type"].value_counts().to_dict(),
        "events_by_user": df["user_id"].value_counts().to_dict(),
        "suspicious_activities": df[
            df["event_type"].isin([
                "failed_login",
                "unauthorized_access",
                "rate_limit_exceeded"
            ])
        ].to_dict("records")
    }
    
    return report
``` 