from pydantic import BaseModel, ConfigDict


#写一个不暴露密码给响应的返回类
class UserSchemaOut(BaseModel):
    id: int
    username: str
    email: str
    
    # 允许从 ORM 模型直接创建
    model_config = ConfigDict(from_attributes=True)

