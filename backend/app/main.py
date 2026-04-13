import uvicorn
from fastapi import FastAPI
import time
from pydantic import BaseModel

app = FastAPI()

class LoginRequest(BaseModel):
    username: str
    password: str


@app.get("/user/{user_id}")
async def get_user(user_id: str):
    return {
        "code": 200,
        "data":{
        "user_id": user_id,
        "user_name": "John Doe",
    },
        "msg": "成功"
    }

@app.post("/login")
async def login(request: LoginRequest):
    # 当前时间戳
    timestamp = int(time.time())
    return {
        "code": 200,
        "data": {"user_id": timestamp,
                 "username": request.username,
                 "token": "123456}",},
        "msg": "成功"
     }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)