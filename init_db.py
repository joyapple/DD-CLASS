from app.database import engine, SessionLocal
from app.models import Base, User, Class, Subject
from app.auth import get_password_hash
from app.config import settings

def init_database():
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成!")
    
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                real_name="系统管理员",
                role="admin"
            )
            db.add(admin)
            print("已创建默认管理员账户: admin / admin123")
        
        subjects = db.query(Subject).all()
        if not subjects:
            default_subjects = ["语文", "数学", "英语", "物理", "化学", "生物", "历史", "地理", "政治"]
            for name in default_subjects:
                subject = Subject(name=name)
                db.add(subject)
            print(f"已创建默认科目: {', '.join(default_subjects)}")
        
        db.commit()
        print("数据库初始化完成!")
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
