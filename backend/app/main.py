# app/main.py
from fastapi import FastAPI ,Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session
from app.utils import response
from models import AsyncSessionMaker

from app.api.v1 import auth, user ,item
import models
from models.user import User

app = FastAPI(
    title="AI Chat Platform API",
    description="AI 聊天平台后端接口",
    version="1.0.0"
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")
app.include_router(item.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Welcome to AI Chat Platform API"}

@app.post("/user/add")
async def add_user(session: AsyncSession = Depends(get_session)):
    # 开启事物
    async with session.begin() as transaction:
        new_user = User(username="admin123456", password="12345678910",email="admin123456@qq.com")
        session.add(new_user)
    return response.success_response(data=new_user)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
