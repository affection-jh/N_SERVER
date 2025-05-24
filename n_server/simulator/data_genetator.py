import time
from simulator.config import COMPANIES, UPDATE_INTERVAL, MAX_STORAGE_TIME, ONE_DAY_SECONDS, UPDATE_PERIODS, CANDLE_PER_DAY, PERIOD_RANGE
from simulator.stock_simulator import brownian_motion 
from collections import deque

def generate_data(market_data):   
    while True:
        time.sleep(UPDATE_INTERVAL)
        for comp in COMPANIES:

            initial_value = market_data.stock_data[comp][-1]["price"]
            new_price = brownian_motion(initial_value, company_name=comp)
            market_data.stock_data[comp].append({
                "time": time.time(),
                "price": round(new_price, 2)
            })
            
            if len(market_data.stock_data[comp]) > MAX_STORAGE_TIME:
                market_data.stock_data[comp] = market_data.stock_data[comp][-MAX_STORAGE_TIME:]
                
        print("✅ 주가 생성 완료")

def sample_data(price_history, interval, period):
    if len(price_history) < 2:
        return []

    sampled_data = []
    last_time = price_history[-1]["time"]
    
    # 각 기간별 데이터 범위 설정
    period_ranges = PERIOD_RANGE
    
    # 해당 기간의 데이터 범위 가져오기
    target_range = period_ranges[period]
    start_time = last_time - target_range
    
    # 범위 내의 데이터만 필터링
    period_data = [p for p in price_history if p["time"] >= start_time]
    if not period_data:
        return []
    
    # 시간 간격으로 데이터 샘플링
    current_time = start_time
    while current_time <= last_time:
        # 현재 시간 범위의 데이터 추출
        interval_data = [p for p in period_data if current_time <= p["time"] < current_time + interval]
        
        if interval_data:
            # 구간의 평균 가격 계산
            avg_price = sum(p["price"] for p in interval_data) / len(interval_data)
            sampled_data.append({
                "time": current_time,
                "price": round(avg_price, 2)
            })
        
        current_time += interval

    return sampled_data


def aggregate_prices_to_candles(price_points, group_size):
    if len(price_points) < group_size:
        return []
        
    # deque를 리스트로 변환하여 슬라이싱 가능하게 함
    price_list = list(price_points)
    candles = []
    
    for i in range(0, len(price_list), group_size):
        if i + group_size > len(price_list):
            break
            
        # 그룹 데이터 추출
        chunk = price_list[i:i+group_size]
        if len(chunk) < group_size:
            break
            
        # 한 번의 순회로 모든 값을 계산
        first_price = chunk[0]["price"]
        last_price = chunk[-1]["price"]
        high = low = first_price
        
        for point in chunk[1:]:  # 첫 번째는 이미 처리했으므로 제외
            price = point["price"]
            if price > high:
                high = price
            if price < low:
                low = price
                
        candles.append({
            "time": chunk[-1]["time"],
            "open": first_price,
            "high": high,
            "low": low,
            "close": last_price,
        })
    return candles

def create_candle_from_data(data_list, lookback):
    if len(data_list) < lookback:
        return None
        
    target_data = data_list[-lookback:]
    high = low = target_data[0]["high"]
    
    for candle in target_data[1:]:
        if candle["high"] > high:
            high = candle["high"]
        if candle["low"] < low:
            low = candle["low"]
            
    return {
        "time": target_data[-1]["time"],
        "open": target_data[0]["open"],
        "high": high,
        "low": low,
        "close": target_data[-1]["close"]
    }

def generate_candle_data(stock_data, candle_data):
    min_data_points = ONE_DAY_SECONDS // CANDLE_PER_DAY
    
    for comp in stock_data.keys():
        stock_list = stock_data[comp]
        if len(stock_list) < min_data_points:
            print(f"⚠️ {comp}의 데이터 포인트가 부족합니다. (현재: {len(stock_list)}, 필요: {min_data_points})")
            continue

        # 일봉 생성 (하루 5개 캔들)
        day_candles = aggregate_prices_to_candles(
            stock_list,  
            min_data_points
        )
        
        if 'day' not in candle_data[comp]:
            candle_data[comp]['day'] = deque(maxlen=5)
        for candle in day_candles[-5:]:
            candle_data[comp]['day'].append(candle)

        # 상위 기간 캔들 생성을 위한 데이터
        day_candles_list = list(candle_data[comp]['day'])

        # 주봉 생성 (5개 데이터 = 1개 캔들, 7개 저장)
        if len(day_candles_list) >= 5:
            week_candle = create_candle_from_data(day_candles_list, 5)
            if week_candle:
                if 'week' not in candle_data[comp]:
                    candle_data[comp]['week'] = deque(maxlen=7)
                if len(candle_data[comp]['week']) == 0 or week_candle["time"] > candle_data[comp]['week'][-1]["time"]:
                    candle_data[comp]['week'].append(week_candle)

        # 월봉 생성 (5개 데이터 = 1개 캔들, 30개 저장)
        if len(day_candles_list) >= 5:
            month_candle = create_candle_from_data(day_candles_list, 5)
            if month_candle:
                if 'month' not in candle_data[comp]:
                    candle_data[comp]['month'] = deque(maxlen=30)
                if len(candle_data[comp]['month']) == 0 or month_candle["time"] > candle_data[comp]['month'][-1]["time"]:
                    candle_data[comp]['month'].append(month_candle)

        # 분기 캔들 생성 (15개 데이터 = 1개 캔들, 30개 저장)
        if len(day_candles_list) >= 15:
            quarter_candle = create_candle_from_data(day_candles_list, 15)
            if quarter_candle:
                if 'quarter' not in candle_data[comp]:
                    candle_data[comp]['quarter'] = deque(maxlen=30)
                if len(candle_data[comp]['quarter']) == 0 or quarter_candle["time"] > candle_data[comp]['quarter'][-1]["time"]:
                    candle_data[comp]['quarter'].append(quarter_candle)

    print("📊 캔들 데이터 업데이트 완료")



def update_market_data(market_data):
    while True:
        time.sleep(ONE_DAY_SECONDS/CANDLE_PER_DAY)
        
        for comp in COMPANIES:
            if len(market_data.stock_data[comp]) < 2:
                continue
                
            price_history = market_data.stock_data[comp]
            
            for period, interval in UPDATE_PERIODS.items():
                sampled_data = sample_data(price_history, interval, period)  # period 파라미터 추가
                if sampled_data and len(sampled_data) >= 2:
                    # 기존 데이터 클리어 후 새로운 데이터 추가
                    market_data.aggregated_data[comp][period].clear()
                    for data_point in sampled_data:
                        market_data.aggregated_data[comp][period].append(data_point)

            generate_candle_data(market_data.stock_data, market_data.candle_data)
            
        print("📊 일일 데이터 업데이트 완료")