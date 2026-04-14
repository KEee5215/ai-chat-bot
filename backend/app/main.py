# app/main.py
from fastapi import FastAPI
from app.api.v1 import auth, user ,item
import models

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
