from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://ddclass:iTiipYXa64BjM7bF@81.70.103.192:5432/ddclass"

def add_bing_setting():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO system_settings (setting_key, setting_value, description)
            VALUES ('use_bing_background', 'true', '是否使用Bing每日一图作为登录背景')
            ON CONFLICT (setting_key) DO UPDATE SET setting_value = 'true', description = '是否使用Bing每日一图作为登录背景'
        """))
        conn.commit()
    print("✅ 已添加 use_bing_background 设置项")

if __name__ == "__main__":
    add_bing_setting()
