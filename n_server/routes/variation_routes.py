from flask import Blueprint, jsonify

# 블루프린트 정의
variation_bp = Blueprint('variation', __name__)

# 공유 데이터 저장 변수
shared_init_prices = None
COMPANIES = None

# 초기화 함수
def init_routes(init_prices, companies):
    global shared_init_prices, COMPANIES
    shared_init_prices = init_prices
    COMPANIES = companies


@variation_bp.route('/init_price/<company>', methods=['GET'])
def get_init_price(company):
    """특정 회사의 기간별 종가 조회 API"""
    if company not in shared_init_prices:
        return jsonify({"error": "존재하지 않는 회사입니다."}), 404
        
    return jsonify(dict(shared_init_prices[company]))


@variation_bp.route('/init_prices', methods=['GET'])
def get_all_init_prices():
    """모든 회사의 기간별 종가 조회 API"""
    result = {}
    for comp in COMPANIES:
        if comp in shared_init_prices:
            result[comp] = dict(shared_init_prices[comp])
    return jsonify(result) 