import logging.config
import os

def setup_logging():
    """
    logging.conf 파일을 읽어 로깅 설정을 구성합니다.
    """
    # 로그 디렉토리 생성
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    logging.config.fileConfig('.config/logging.conf', disable_existing_loggers=False)

