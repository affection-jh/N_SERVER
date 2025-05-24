from flask import Blueprint, jsonify
from simulator.config import COMPANIES, UPDATE_PERIODS
from collections import deque

# 블루프린트 정의
stock_bp = Blueprint('stock', __name__)

# 데이터 저장소
stock_data = {}
candle_data = {}
aggregated_data = {}

def deque_to_list(data):
    if isinstance(data, deque):
        return list(data)
    elif isinstance(data, dict):
        return {k: deque_to_list(v) for k, v in data.items()}
    return data

def init_routes(data):
    global stock_data, candle_data, aggregated_data
    stock_data = data[0]
    candle_data = data[1]
    aggregated_data = data[2]

@stock_bp.route('/<company>/<period>', methods=['GET'])
def get_stock_history(company, period):
    try:
        company_data = aggregated_data[company].get(period, [])
        print(len(company_data))
        history_data = []
        if company_data:
            for data_point in company_data:
                history_data.append([
                    data_point['time'],  # x축: 시간
                    float(data_point['price'])  # y축: 가격
                ])

        return jsonify(history_data)

    except Exception as e:
        print(f"🚨 주가 이력 조회 중 오류 발생: {e}")
        return jsonify({"error": "서버 내부 오류 발생"}), 500
    


@stock_bp.route('/current_prices', methods=['GET'])
def get_current_prices():
    try:
        prices = {
            comp: stock_data[comp][-1]['price'] 
            for comp in COMPANIES 
            if stock_data[comp] and len(stock_data[comp]) > 0
        }
        return jsonify(prices)
    except Exception as e:
        print(f"🚨 오류 발생: {e}")
        return jsonify({"error": "서버 내부 오류 발생"}), 500
    


@stock_bp.route('/candle/<company>/<period>', methods=['GET'])
def get_candle_data(company, period):   
    try:
     
        candles = deque_to_list(candle_data[company][period])
        return jsonify({
            "candles": candles
        })
    except Exception as e:
        print(f"캔들 데이터 조회 중 오류 발생: {e}")
        return jsonify({"error": "서버 내부 오류 발생"}), 500


@stock_bp.route('/initial_prices', methods=['GET'])
def get_initial_prices():
    try:
        result = {}
        for comp in COMPANIES:
            if comp in aggregated_data:
                result[comp] = {
                    period: data[0]['price'] if data else None
                    for period, data in aggregated_data[comp].items()
                }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "서버 내부 오류 발생"}), 500
        
    

