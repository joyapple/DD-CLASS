from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://ddclass:iTiipYXa64BjM7bF@81.70.103.192:5432/ddclass"

def create_settings_table():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS system_settings (
                id SERIAL PRIMARY KEY,
                setting_key VARCHAR NOT NULL UNIQUE,
                setting_value VARCHAR,
                description VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_system_settings_key ON system_settings(setting_key)
        """))
        
        default_settings = [
            ('system_name', 'DD-CLASS 班级管理系统', '系统名称'),
            ('login_background', '', '登录页面背景图URL'),
            ('system_logo', '', '系统Logo URL'),
            ('system_intro', '一个现代化的班级管理系统', '系统简介'),
            ('copyright', '© 2024 DD-CLASS', '版权信息'),
        ]
        
        for key, value, desc in default_settings:
            conn.execute(text("""
                INSERT INTO system_settings (setting_key, setting_value, description)
                VALUES (:key, :value, :desc)
                ON CONFLICT (setting_key) DO NOTHING
            """), {"key": key, "value": value, "desc": desc})
        
        conn.commit()
        
    print("✅ 系统设置表创建成功！")
    print("✅ 默认设置已初始化！")

if __name__ == "__main__":
    create_settings_table()
