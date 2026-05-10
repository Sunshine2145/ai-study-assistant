# AI Study Assistant - Main Application Module

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.config.settings import settings
from src.modules.feishu.bot import router as feishu_router
from src.routes import user, learning, knowledge, chat, questions, answers, wrong_questions, report, reminders, upload, question_bank, ai_qa

app = FastAPI(title="AI伴学系统", version="1.0.0")

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(feishu_router, prefix="/feishu", tags=["飞书"])
app.include_router(user.router)
app.include_router(learning.router)
app.include_router(knowledge.router)
app.include_router(chat.router)
app.include_router(questions.router)
app.include_router(answers.router)
app.include_router(wrong_questions.router)
app.include_router(report.router)
app.include_router(reminders.router)
app.include_router(upload.router)
app.include_router(question_bank.router)
app.include_router(ai_qa.router)


@app.get("/")
async def root():
    return {"message": "AI伴学系统 API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10088)