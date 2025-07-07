import os
from dotenv import load_dotenv

# --env-file .config/.env 옵션 넣어서 실행하기 귀찮으면 넣고...
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.config', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
else:
    # 대체 경로
    load_dotenv()

# 환경 변수에서 설정 값 가져오기
GOOGLE_DRIVE_FOLDER_IDS = os.getenv("GOOGLE_DRIVE_FOLDER_IDS")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash-latest")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.7))
