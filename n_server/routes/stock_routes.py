from flask import Blueprint, jsonify

# 블루프린트 정의
stock_bp = Blueprint('stock', __name__)

# 공유 데이터 저장 변수
shared_stock_data = None
shared_aggregated_data = None
shared_candle_data = None
shared_percentage_rates = None

# 설정 값
COMPANIES = None
PERIOD_MAP = None

# 초기화 함수
def init_routes(stock_data, candle_data, aggregated_data, percentage_rates, companies, period_map):
    global shared_stock_data, shared_candle_data, shared_aggregated_data, shared_percentage_rates, COMPANIES, PERIOD_MAP
    shared_stock_data = stock_data
    shared_candle_data = candle_data
    shared_aggregated_data = aggregated_data
    shared_percentage_rates = percentage_rates
    COMPANIES = companies
    PERIOD_MAP = period_map


@stock_bp.route('/current_prices', methods=['GET'])
def get_current_prices():
    try:
        prices = {comp: shared_stock_data[comp][-1]['price'] 
                 for comp in COMPANIES 
                 if shared_stock_data[comp] and len(shared_stock_data[comp]) > 0}
        return jsonify(prices)
    except Exception as e:
        print(f"🚨 오류 발생: {e}")
        return jsonify({"error": "서버 내부 오류 발생"}), 500


@stock_bp.route('/stock/<company>/<period>', methods=['GET'])
def get_stock_data(company, period):
    if company not in shared_aggregated_data or period not in shared_aggregated_data[company]:
        return jsonify({"error": "존재하지 않는 회사 또는 잘못된 기간"}), 400
    return jsonify(list(shared_aggregated_data[company][period]))


@stock_bp.route('/candle/<company>/<period>', methods=['GET'])
def get_candle_data(company, period):
    """캔들 데이터 조회 API"""
    if shared_candle_data is None:
        return jsonify({"error": "캔들 데이터가 아직 초기화되지 않았습니다."}), 500

    if company not in shared_candle_data:
        return jsonify({"error": "존재하지 않는 회사입니다."}), 404

    if period not in PERIOD_MAP:
        return jsonify({"error": "기간 오류"}), 400

    candles = list(shared_candle_data[company])[-PERIOD_MAP[period]:]
    return jsonify({"candles": candles}) 