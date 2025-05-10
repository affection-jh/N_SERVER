import time
import multiprocessing
import logging
from flask import Flask


# 로깅 설정 - 간소화
logging.basicConfig(level=logging.ERROR) 
logger = logging.getLogger('n_server')
logger.setLevel(logging.INFO) 
logging.getLogger('werkzeug').setLevel(logging.ERROR)

# 분리된 모듈 임포트
from simulator.config import COMPANIES, create_initial_data, PERIOD_MAP
from simulator.process_manager import start_processes

# 블루프린트 임포트
from routes.stock_routes import stock_bp, init_routes as init_stock_routes
from routes.variation_routes import variation_bp, init_routes as init_variation_routes

# 웹소켓 임포트
from websocket.web_socket_api import socketio, init_websocket, start_ws_emitter

# Flask 애플리케이션 생성
app = Flask(__name__)
app.config['SECRET_KEY'] = 'stock-simulator-secret!'
app.config['DEBUG'] = False  # 디버그 모드 비활성화
app.config['CORS_HEADERS'] = 'Content-Type'


# 블루프린트 등록
app.register_blueprint(stock_bp)
app.register_blueprint(variation_bp)

# 초기 데이터 구조 생성
stock_data, candle_data, _ = create_initial_data()

# 프로세스 간 공유될 데이터 변수들 - 전역 선언
shared_stock_data = None
shared_candle_data = None
shared_aggregated_data = None
shared_percentage_rates = None


def initialize_routes():
    """라우트 초기화 - 공유 데이터를 각 라우트 모듈에 전달"""
    # 주가 데이터 API 초기화
    init_stock_routes(
        shared_stock_data, 
        shared_candle_data, 
        shared_aggregated_data,
        shared_percentage_rates,
        COMPANIES,
        PERIOD_MAP
    )
    
    # 변동률 API 초기화
    init_variation_routes(
        shared_percentage_rates,
        COMPANIES
    )
    
    # 웹소켓 초기화
    init_websocket(shared_stock_data, COMPANIES)


if __name__ == "__main__":
    multiprocessing.freeze_support()  # Windows 대응
    
    # 공유 변수에 프로세스 시작 결과 할당
    shared_stock_data, shared_candle_data, shared_aggregated_data, shared_percentage_rates = start_processes()
    
    # 라우트 초기화
    initialize_routes()
    
    # 공유 변수 사용 (필요하면 유지, 사용하지 않는다면 삭제 가능)
    stock_data.clear()  # 기존 데이터 삭제
    for comp in COMPANIES:
        stock_data[comp] = shared_stock_data[comp]
    
    candle_data.clear()
    for comp in COMPANIES:
        candle_data[comp] = shared_candle_data[comp]

    # 웹소켓 서버 시작
    socket = start_ws_emitter(app)

    # 서버 시작 
    logger.info("🚀 스톡 시뮬레이터 서버 시작")
    logger.info("📡 웹소켓 서버: ws://0.0.0.0:5000/socket.io/")
    logger.info("🌐 REST API: http://0.0.0.0:5000/")
    socket.run(app, debug=False, host="0.0.0.0", port=5000, use_reloader=False, allow_unsafe_werkzeug=True, log_output=False)
