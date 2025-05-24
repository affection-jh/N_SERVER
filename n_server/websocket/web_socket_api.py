# ws_server.py
from flask_socketio import SocketIO, emit
import time
import threading
from simulator.config import UPDATE_INTERVAL

class WebSocketManager:
    def __init__(self):
        self.stock_data = None
        self.companies = None
        self.socketio = None
        self._emit_thread = None

    def init_websocket(self, stock_data, companies):
        self.stock_data = stock_data
        self.companies = companies

    def _start_emit_thread(self):
        if self._emit_thread is None or not self._emit_thread.is_alive():
            print("데이터 송출 스레드 시작")
            self._emit_thread = threading.Thread(target=self.emit_stock_prices, daemon=True)
            self._emit_thread.start()

    def handle_connect(self):
        try:
            print("새로운 클라이언트가 연결되었습니다.")
            self.socketio.emit("message", {
                "type": "welcome",
                "msg": "주가 실시간 스트리밍 시작"
            })
        except Exception as e:
            print(f"웹소켓 연결 오류: {e}")

    def emit_stock_prices(self):
        print("실시간 데이터 송출 시작")
        while True:
            try:
                if not self.stock_data or not self.companies:
                    time.sleep(UPDATE_INTERVAL)
                    continue

                price_data = {
                    comp: self.stock_data[comp][-1]["price"]
                    for comp in self.companies
                    if comp in self.stock_data and self.stock_data[comp]
                }

                # 데이터 방출
                if price_data and self.socketio:
                    self.socketio.emit("price_update", price_data)

            except Exception as e:
                print(f"실시간 데이터 송출 중 오류 발생: {e}")
            
            time.sleep(UPDATE_INTERVAL)

    def start(self, app):
        # SocketIO 인스턴스 생성
        self.socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode='threading',
            logger=True,
            engineio_logger=True,
            ping_timeout=60,
            ping_interval=25,
            host='0.0.0.0',  # 모든 네트워크 인터페이스에서 접속 허용
            allow_upgrades=True,  # WebSocket 업그레이드 허용
            transports=['websocket', 'polling']  # 클라이언트와 동일한 전송 방식 지원
        )
        
        # 이벤트 핸들러 등록
        self.socketio.on_event('connect', self.handle_connect)
        
        # 데이터 송출 스레드 시작
        self._start_emit_thread()
            
        return self.socketio

def create_websocket_manager():
    return WebSocketManager()
