from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://ddclass:iTiipYXa64BjM7bF@81.70.103.192:5432/ddclass"

def create_tables():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS homeworks (
                id SERIAL PRIMARY KEY,
                title VARCHAR NOT NULL,
                content VARCHAR,
                class_id INTEGER NOT NULL REFERENCES classes(id),
                subject_id INTEGER REFERENCES subjects(id),
                due_date TIMESTAMP WITH TIME ZONE,
                created_by INTEGER NOT NULL REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                title VARCHAR NOT NULL,
                content VARCHAR,
                priority VARCHAR DEFAULT 'normal',
                is_pinned BOOLEAN DEFAULT FALSE,
                created_by INTEGER NOT NULL REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS notification_reads (
                id SERIAL PRIMARY KEY,
                notification_id INTEGER NOT NULL REFERENCES notifications(id),
                user_id INTEGER NOT NULL REFERENCES users(id),
                is_read BOOLEAN DEFAULT FALSE,
                read_at TIMESTAMP WITH TIME ZONE,
                UNIQUE(notification_id, user_id)
            )
        """))
        
        conn.commit()
        
    print("✅ 数据库表创建成功！")

if __name__ == "__main__":
    create_tables()
