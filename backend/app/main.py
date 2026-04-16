# app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI ,Depends,Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, MessageType

from app.dependencies import get_mail
from app.exceptions import BusinessException
from app.utils.response import error_response
from models import AsyncSessionMaker,engine

from app.api.v1 import auth, user ,item




@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("应用启动成功")
    yield
    # 关闭时执行
    print("正在关闭数据库连接池...")
    await engine.dispose()
    print("数据库连接池已关闭")

app = FastAPI(
    title="AI Chat Platform API",
    description="AI 聊天平台后端接口",
    version="1.0.0"
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")
app.include_router(item.router, prefix="/api/v1")



@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    """业务异常处理"""
    return JSONResponse(
        status_code=exc.code,
        content=error_response(code=exc.code, msg=exc.message)
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理"""
    return JSONResponse(
        status_code=422,
        content=error_response(code=422, msg=str(exc.errors()))
    )


@app.get("/")
async def root():
    return {"message": "Welcome to AI Chat Platform API"}

@app.get("/mail/test")
async def mail_test(
        email: str ,
        mail: FastMail = Depends(get_mail),
):
    message = MessageSchema(
        subject="测试邮件",
        recipients=[email],
        body=f"hello!{email}",
        subtype=MessageType.plain
    )
    await mail.send_message(message)
    return {"message": "发送成功"}




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
