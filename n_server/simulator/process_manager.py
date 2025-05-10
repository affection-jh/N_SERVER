import multiprocessing
import time

from simulator.config import COMPANIES, INITIAL_PRICES, SAMPLE_INTERVALS
from simulator.data_genetator import generate_data, update_aggregated_data

def start_processes():
    """멀티프로세싱을 사용하여 데이터 공유 최적화"""
    manager = multiprocessing.Manager()

    # 공유 데이터 생성
    shared_stock_data = manager.dict({comp: manager.list() for comp in COMPANIES})
    shared_candle_data = manager.dict({comp: manager.list() for comp in COMPANIES})
    shared_aggregated_data = manager.dict({comp: manager.dict({"quarter": [], "month": [], "week": [], "day": []}) for comp in COMPANIES})
    
    # 변동률 데이터를 공유 변수로 생성
    shared_percentage_rates = manager.dict({
        comp: manager.dict({
            "quarter": 0.0,
            "month": 0.0,
            "week": 0.0,
            "day": 0.0
        }) for comp in COMPANIES
    })

    # 초기 데이터 삽입
    for comp in COMPANIES:
        shared_stock_data[comp].append({
            "time": time.time(),
            "price": INITIAL_PRICES[comp]
        })

    # 백그라운드 프로세스 실행
    multiprocessing.Process(
        target=generate_data, 
        args=(shared_stock_data, COMPANIES, INITIAL_PRICES), 
        daemon=True
    ).start()
    
    multiprocessing.Process(
        target=update_aggregated_data, 
        args=(shared_stock_data, shared_aggregated_data, shared_candle_data, shared_percentage_rates, SAMPLE_INTERVALS), 
        daemon=True
    ).start()

    return shared_stock_data, shared_candle_data, shared_aggregated_data, shared_percentage_rates 