import time
import numpy as np
from simulator.stock_simulator import brownian_motion
from simulator.config import UPDATE_INTERVAL

def generate_data(shared_stock_data, companies, initial_prices):
    """실시간 주가 생성"""
    while True:
        time.sleep(UPDATE_INTERVAL)
        for comp in companies:
            # 데이터가 없으면 초기 가격으로 시작
            if len(shared_stock_data[comp]) == 0:
                print(f"⚠️ {comp}의 초기 데이터가 없어 초기화합니다.")
                shared_stock_data[comp].append({"time": time.time(), "price": initial_prices[comp]})
                continue

            initial_value = shared_stock_data[comp][-1]["price"]
            # 회사 이름을 전달하여 각 회사마다 독립적인 base_mean 유지
            new_price = brownian_motion(initial_value, company_name=comp)
            shared_stock_data[comp].append({"time": time.time(), "price": round(new_price, 2)})
        
    
        print("✅ 주가 생성 완료")
            


def sample_data(data_list, interval):
    if not data_list:
        return []

    sampled_data = []
    last_time = data_list[-1]["time"]
    current_time = last_time - interval * 40  # 최근 40개의 샘플링된 데이터만 유지

    while current_time <= last_time:
        segment = [point["price"] for point in data_list if current_time <= point["time"] < current_time + interval]
        if segment:
            sampled_data.append({"time": current_time, "price": round(np.mean(segment), 2)})
        current_time += interval

    from collections import deque
    return deque(sampled_data, maxlen=50)


def calculate_percentage_rates(data_list):
    """주어진 데이터 리스트에서 첫 가격과 마지막 가격 사이의 변동률(%)을 계산"""
    if not data_list or len(data_list) < 2:
        return 0.0

    # 데이터가 딕셔너리 형태인지 확인
    if isinstance(data_list[0], dict) and "price" in data_list[0]:
        last_price = data_list[-1]["price"]
        first_price = data_list[0]["price"]
    else:
        # 데이터가 숫자 목록인 경우
        last_price = data_list[-1]
        first_price = data_list[0]
    
    if first_price == 0 or first_price is None:  # 0으로 나누기 방지
        return 0.0
    
    # 변동률 계산 (백분율로 변환)
    #change_rate = ((last_price - first_price) / first_price) * 100
    
    # 너무 작은 변화는 반올림하여 0으로
    #if abs(change_rate) < 0.01:
    #    return 0.0
        
    return round(first_price, 2)


def generate_candle_data(shared_stock_data, shared_candle_data):
    """캔들 데이터 생성"""
    current_time = int(time.time())
    for comp in shared_stock_data.keys():
        if len(shared_stock_data[comp]) < 30:
            continue

        daily_prices = [point["price"] for point in list(shared_stock_data[comp])[-30:]]

        if not daily_prices:
            continue

        candle_entry = {
            "time": current_time,
            "open": daily_prices[0],
            "high": max(daily_prices),
            "low": min(daily_prices),
            "price": daily_prices[-1]  # 종가
        }
        shared_candle_data[comp].append(candle_entry)

    print("📊 하루치 캔들 데이터 업데이트 완료")


def update_aggregated_data(shared_stock_data, shared_aggregated_data, shared_candle_data, shared_percentage_rates, sample_intervals):
    companies = list(shared_stock_data.keys())
    while True:
        time.sleep(30)  # 더 자주 업데이트
        for comp in companies:
            data_list = list(shared_stock_data[comp])
            if not data_list or len(data_list) < 2:  # 최소 2개 이상의 데이터 필요
                continue

            # 각 기간별 데이터 샘플링
            quarter_data = sample_data(data_list, sample_intervals["quarter"])
            month_data = sample_data(data_list, sample_intervals["month"])
            week_data = sample_data(data_list, sample_intervals["week"])
            day_data = sample_data(data_list, sample_intervals["day"])
            
            # 각 기간별 변동률 계산 및 공유 변수에 저장
            if quarter_data and len(list(quarter_data)) >= 2:
                shared_percentage_rates[comp]["quarter"] = calculate_percentage_rates(list(quarter_data))
            if month_data and len(list(month_data)) >= 2:
                shared_percentage_rates[comp]["month"] = calculate_percentage_rates(list(month_data))
            if week_data and len(list(week_data)) >= 2:
                shared_percentage_rates[comp]["week"] = calculate_percentage_rates(list(week_data))
            if day_data and len(list(day_data)) >= 2:
                shared_percentage_rates[comp]["day"] = calculate_percentage_rates(list(day_data))
            
            # 집계 데이터 저장
            shared_aggregated_data[comp] = {
                "quarter": quarter_data,
                "month": month_data,
                "week": week_data,
                "day": day_data
            }
            
        generate_candle_data(shared_stock_data, shared_candle_data)
        
        # 변동률 출력
        for comp in companies:
            print(f"{comp} 변동률: {dict(shared_percentage_rates[comp])}")
            
        print("📊 샘플링 데이터 업데이트 완료!")