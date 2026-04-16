from dotenv import load_dotenv
import os

load_dotenv()

DB_URI = os.getenv("DB_URI", "mysql+aiomysql://root:123456@localhost:3306/ai_chat_db?charset=utf8mb4")


MAIL_USERNAME = os.getenv("MAIL_USERNAME", "keee5215@qq.com")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_FROM = os.getenv("MAIL_FROM", "keee5215@qq.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "465"))
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.qq.com")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "AI 聊天平台")
MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "True").lower() == "true"
MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS", "False").lower() == "true"

# JWT 配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


