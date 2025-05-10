# ws_server.py
from flask_socketio import SocketIO, emit
import time
import threading
import logging
from simulator.config import UPDATE_INTERVAL

# 간소화된 로깅 설정 (ERROR 레벨로 설정하여 중요 메시지만 출력)
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('websocket').setLevel(logging.INFO)
logger = logging.getLogger('websocket')

# 간소화된 socketio 인스턴스 생성 - ping_timeout과 ping_interval 값 조정
socketio = SocketIO(
    cors_allowed_origins="*", 
    logger=False, 
    engineio_logger=False,
    ping_timeout=60,  # 핑 타임아웃 확장
    ping_interval=25  # 핑 간격 확장
)
# 공유 데이터 저장 변수
shared_stock_data = None
COMPANIES = None

def init_websocket(stock_data, companies):
    """웹소켓 모듈 초기화"""
    global shared_stock_data, COMPANIES
    shared_stock_data = stock_data
    COMPANIES = companies
    logger.info("웹소켓 초기화 완료")

@socketio.on("connect")
def handle_connect(auth=None):
    """클라이언트 연결 이벤트 처리"""
    try:
        client_info = auth if auth else "정보 없음"
        logger.info(f"✓ 클라이언트 연결됨: {client_info}")
        emit("message", {"type": "welcome", "msg": "주가 실시간 스트리밍 시작"})
    except Exception as e:
        logger.error(f"연결 처리 중 오류: {str(e)}")

@socketio.on("disconnect")
def handle_disconnect(reason=None):
    """클라이언트 연결 해제 이벤트 처리"""
    try:
        # reason 매개변수는 Flask-SocketIO가 제공하는 연결 해제 이유
        logger.info(f"클라이언트 연결 해제: {reason if reason else '알 수 없음'}")
    except Exception as e:
        logger.error(f"연결 해제 처리 중 오류: {str(e)}")

@socketio.on_error()
def handle_error(e, *args, **kwargs):
    """Socket.IO 오류 처리 - 추가 인자로 인해 발생하는 오류 방지"""
    error_msg = str(e) if e else "알 수 없는 오류"
    logger.error(f"웹소켓 오류: {error_msg}")

def emit_stock_prices():
    """주기적으로 실시간 주가를 모든 클라이언트에 브로드캐스트"""
    print_counter = 0  # 로그 간소화를 위한 카운터
    while True:
        try:
            data = {}
            if shared_stock_data and COMPANIES:
                for comp in COMPANIES:
                    if comp in shared_stock_data and shared_stock_data[comp]:
                        data[comp] = shared_stock_data[comp][-1]["price"]
                if data:
                    # 20번에 한 번만 로그 출력 (약 20초마다)
                    print_counter += 1
                    if print_counter >= 20:
                        logger.info("주가 데이터 전송 중...")
                        print_counter = 0
                    socketio.emit("price_update", data)
        except Exception as e:
            logger.error(f"데이터 전송 오류: {str(e)}")
        
        time.sleep(UPDATE_INTERVAL)

def start_ws_emitter(app):
    """웹소켓 서버와 데이터 전송 쓰레드 시작"""
    socketio.init_app(
        app, 
        cors_allowed_origins="*", 
        async_mode='threading',
        logger=False, 
        engineio_logger=False,
        ping_timeout=60,
        ping_interval=25
    )
    # 데이터 전송 스레드 시작
    threading.Thread(target=emit_stock_prices, daemon=True).start()
    logger.info("🔌 웹소켓 서버 시작")
    return socketio
