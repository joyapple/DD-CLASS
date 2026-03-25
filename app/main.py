from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, classes, students, scores, attendance, dashboard, subjects, users, semesters, logs, points, settings, homework, notifications

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="班级管理系统 API",
    description="轻量化班级管理系统后端API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(classes.router)
app.include_router(students.router)
app.include_router(scores.router)
app.include_router(attendance.router)
app.include_router(dashboard.router)
app.include_router(subjects.router)
app.include_router(users.router)
app.include_router(semesters.router)
app.include_router(logs.router)
app.include_router(points.router)
app.include_router(settings.router)
app.include_router(homework.router)
app.include_router(notifications.router)

@app.get("/")
def root():
    return {"message": "班级管理系统 API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/bing-background")
def get_bing_background():
    """获取Bing每日一图"""
    import httpx
    try:
        response = httpx.get(
            "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN",
            timeout=10.0
        )
        data = response.json()
        if data.get("images") and len(data["images"]) > 0:
            image_url = "https://www.bing.com" + data["images"][0]["url"]
            return {"url": image_url}
    except Exception as e:
        print(f"获取Bing背景失败: {e}")
    return {"url": ""}
