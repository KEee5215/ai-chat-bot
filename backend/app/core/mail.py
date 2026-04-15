from fastapi_mail import FastMail, ConnectionConfig
from pydantic import SecretStr

from app.settings import (
    MAIL_USERNAME,
    MAIL_PASSWORD,
    MAIL_FROM,
    MAIL_PORT,
    MAIL_SERVER,
    MAIL_FROM_NAME,
    MAIL_STARTTLS,
    MAIL_SSL_TLS,
)


def create_mail_instance() -> FastMail:
    """创建邮件发送实例"""
    conf = ConnectionConfig(
        MAIL_USERNAME=MAIL_USERNAME,
        MAIL_PASSWORD=SecretStr(MAIL_PASSWORD),
        MAIL_FROM=MAIL_FROM,
        MAIL_PORT=MAIL_PORT,
        MAIL_SERVER=MAIL_SERVER,
        MAIL_FROM_NAME=MAIL_FROM_NAME,
        MAIL_STARTTLS=MAIL_STARTTLS,
        MAIL_SSL_TLS=MAIL_SSL_TLS,
    )
    return FastMail(conf)
