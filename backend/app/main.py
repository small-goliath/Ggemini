
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from .service import rag_service
from .schemas import AskRequest
from .logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_event()
    
    yield
    
    await shutdown_event()

async def startup_event():
    """
    애플리케이션 시작 시 LangChain 파이프라인을 초기화하고, 주기적인 재색인을 설정
    """
    logger.info("애플리케이션 시작, RAG 서비스 초기화를 시작합니다.")
    try:
        rag_service.initialize()
        logger.info("RAG 서비스가 성공적으로 초기화되었습니다.")
        
        scheduler = BackgroundScheduler()
        scheduler.add_job(rag_service.initialize, 'cron', hour='8,12,15,18', minute='0')
        scheduler.start()
        logger.info("백그라운드 재색인 스케줄러가 시작되었습니다. (매일 08, 12, 15, 18시 실행)")
        
    except Exception as e:
        logger.critical(f"CRITICAL: RAG 서비스 초기화 또는 스케줄러 시작 실패: {e}", exc_info=True)

async def shutdown_event():
    """
    애플리케이션 종료
    """
    logger.info("애플리케이션이 정상적으로 종료되었습니다.")

app = FastAPI(lifespan=lifespan)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: 운영에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/query")
async def ask_question(request: AskRequest):
    """
    사용자의 질문을 받아 답변을 생성하는 API 엔드포인트
    """
    if not request.question:
        logger.warning("API 호출 시 질문이 누락되었습니다.")
        raise HTTPException(status_code=400, detail="질문이 없습니다.")

    logger.info(f"수신된 질문: {request.question}")
    try:
        answer = rag_service.ask(request.question)
        logger.info(f"생성된 답변: {answer}")
        return JSONResponse(content={"answer": answer})
    except RuntimeError as e:
        logger.error(f"RAG 파이프라인이 준비되지 않았습니다: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"답변 생성 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"답변 생성 중 오류 발생: {e}")

@app.get("/")
def read_root():
    return {"message": "Q&A Backend is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

