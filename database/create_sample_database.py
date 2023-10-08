from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dataSchema import User, get_db
from passlib.context import CryptContext
import random
import string

# 密碼哈希設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# 創建數據庫表格
DATABASE_URL = "sqlite:///./user.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# 创建User表格
Base.metadata.create_all(bind=engine, tables=[User.__table__])

# 建立與數據庫的連接
Session = sessionmaker(bind=engine)

# 生成隨機字符串的功能
def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

# 添加用戶到數據庫的功能
def add_user(session, username, email, hashed_password):
    user = User(username=username, email=email, password=hashed_password)
    session.add(user)

try:
    # 使用上下文管理器打開會話
    with Session() as session:
        # 創建10個用戶記錄
        for _ in range(10):
            # 生成隨機用戶名和電子郵件
            username = generate_random_string(8)
            email = generate_random_string(8) + "@example.com"
            print(email)
            
            # 生成一個安全哈希化的密碼
            raw_password = "your_plain_text_password"  # 這只是一個示例，請使用真正的隨機密碼
            hashed_password = get_password_hash(raw_password)
            
            # 添加用戶到數據庫
            add_user(session, username, email, hashed_password)

        # 提交事務將用戶數據保存到數據庫
        session.commit()

except Exception as e:
    print(f"發生錯誤: {e}")
