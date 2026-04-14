from models import  AsyncSessionMaker

async def get_session():
    session = AsyncSessionMaker()
    try:
        yield session
    finally:
        await session.close() 