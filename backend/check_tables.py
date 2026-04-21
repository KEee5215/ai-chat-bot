from app.models import sync_engine
from sqlalchemy import inspect

inspector = inspect(sync_engine)

print("=" * 60)
print("rag_chat_message 表结构:")
print("=" * 60)

columns = inspector.get_columns('rag_chat_message')
for col in columns:
    print(f"  {col['name']:20s} : {col['type']}")

print("\n" + "=" * 60)
print("session_documents 表结构:")
print("=" * 60)

columns = inspector.get_columns('session_documents')
for col in columns:
    print(f"  {col['name']:20s} : {col['type']}")
