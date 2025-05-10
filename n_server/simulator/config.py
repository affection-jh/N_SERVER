from zoneinfo import ZoneInfo
from collections import deque

# 시간대 설정
LOCAL_TZ = ZoneInfo("Asia/Seoul")

# 시간 관련 설정
UPDATE_INTERVAL = 0.8  # 데이터 업데이트 간격 (초)

# 회사 목록
COMPANIES = ["corp1", "corp2", "corp3", "corp4", "corp5", "corp6"]

# 최대 저장 데이터량 설정
SECONDS_IN_YEAR = 100 * 7 * 4 * 3

# 초기 주식 가격 설정
INITIAL_PRICES = {
    "corp1": 50.0,
    "corp2": 70.0,
    "corp3": 100.0,
    "corp4": 120.0,
    "corp5": 170.0,
    "corp6": 200.0,
}

# 샘플링 간격 (초 단위)
SAMPLE_INTERVALS = {
    "quarter": 50, 
    "month": 25,   
    "week": 10,    
    "day": 1         
}

# 캔들차트 기간 맵핑
PERIOD_MAP = {
    "day": 1,
    "week": 7,
    "month": 30,
    "quarter": 90
}

# 초기 데이터 구조 생성
def create_initial_data():
    # 주식 데이터 저장소
    stock_data = {company: deque(maxlen=SECONDS_IN_YEAR) for company in COMPANIES}
    
    # 캔들차트 데이터 저장소
    candle_data = {company: deque(maxlen=31) for company in COMPANIES}
    
    # 변동률 데이터 구조
    percentage_rates = {
        company: {
            "quarter": 0.0, 
            "month": 0.0,   
            "week": 0.0,    
            "day": 0.0
        } for company in COMPANIES
    }
    
    return stock_data, candle_data, percentage_rates 