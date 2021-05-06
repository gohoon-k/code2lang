# 각종 설정들이 저장된 파일.

import datetime
import os

from typing import List

# 루트 프로젝트 디렉터리
PROJECT_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)

# 지원 언어 목록. 추가할 경우 데이터들도 추가해야함
SUPPORTED_LANGUAGES: List[str] = ["cpp", "html", "java", "javascript", "kotlin", "python"]

# 대소문자 구별 안함 플래그 문자열
CASE_IGNORE_FLAG: str = " -> IGNORE_CASE"

# 전체 키워드 파일 경로
ALL_KEYWORDS_PATH: str = f"{PROJECT_ROOT}/datasets/all_keywords_regex.txt"
ALL_KEYWORDS_DISPLAY_NAME_PATH: str = f"{PROJECT_ROOT}/datasets/all_keywords_display_name.txt"

# 스크래핑에서 쓰이는 경로
SC_SCRAP_OUTPUT_PATH: str = f"{PROJECT_ROOT}/scraping/source_codes/workspace"
TAG_SCRAP_OUTPUT_PATH: str = f"{PROJECT_ROOT}/scraping/tags"

# 분석기에서 쓰이는 각종 경로
ANALYZE_TARGET_PATH: str = SC_SCRAP_OUTPUT_PATH
ANALYZE_OUTPUT_PATH: str = f"{PROJECT_ROOT}/scraping/source_codes/statistics"
ANALYZE_REDUNDANT_PATH: str = f"{PROJECT_ROOT}/scraping/source_codes/redundant"

# 시각화 데이터 입력 경로와 출력 경로를 설정한다
VISUALIZATION_INPUT_PATH: str = f"{PROJECT_ROOT}/scraping/source_codes/statistics/statistics.dat"
VISUALIZATION_OUTPUT_PATH: str = f"{PROJECT_ROOT}/visualized_data"

# 데이터 집합을 만들기 위한 상수
VALIDATE_RATIO: float = 0.1
DATASET_CREATION_TARGET: str = "final"
DATASET_CREATION_ROOT: str = f"{SC_SCRAP_OUTPUT_PATH}/{DATASET_CREATION_TARGET}"

# 훈련/검증 데이터 경로
TRAIN_DATASET_PATH: str = f"{PROJECT_ROOT}/datasets/train_dataset"
VALIDATION_DATASET_PATH: str = f"{PROJECT_ROOT}/datasets/validation_dataset"
TRAIN_DATASET_PREVIEW_PATH: str = f"{PROJECT_ROOT}/datasets/train_dataset_preview.csv"
VALIDATION_DATASET_PREVIEW_PATH: str = f"{PROJECT_ROOT}/datasets/validation_dataset_preview.csv"

# 모델 경로 및 이름
MODEL_PATH: str = f"{PROJECT_ROOT}/models"
MODEL_NAME: str = "code2lang_m"

# 예측시 사용할 모델의 경로
USE_LATEST_MODEL: bool = False
# PREDICT_MODEL: str = "20201231-225212"  # 0.007
# PREDICT_MODEL: str = "20210101-133222"  # 0.005
# PREDICT_MODEL: str = "20210101-135901"  # 0.005
# PREDICT_MODEL: str = "20210114-214129"  # 0.0044
# PREDICT_MODEL: str = "20210209-103443"  # 0.0012
# PREDICT_MODEL: str = "20210209-161501"  # 0.00089
PREDICT_MODEL: str = "20210210-102201"  # 0.00074

# 데이터 전처리 모드. 0이면 단어의 존재 여부만 반영하고 1이면 단어의 빈도까지 반영한다.
MODE: int = 0

# 모델을 저장하기 위한 현재 시간을 포매팅한 문자열
CURRENT_DATE_TIME: str = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
