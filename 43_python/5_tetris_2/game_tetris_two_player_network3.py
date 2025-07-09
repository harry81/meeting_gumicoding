import pygame
import random
import socket
import threading
import pickle
import sys
import time

# 게임 설정
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH * 2 + 200  # 두 플레이어 화면 + 중간 공간
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT + 100

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
COLORS = [
    (0, 255, 255),  # I - 청록색
    (0, 0, 255),    # J - 파란색
    (255, 165, 0),  # L - 주황색
    (255, 255, 0),  # O - 노란색
    (0, 255, 0),    # S - 초록색
    (128, 0, 128),  # T - 보라색
    (255, 0, 0)     # Z - 빨간색
]

# 테트리스 블록 모양
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]]   # Z
]

def get_local_ip():
    """로컬 IP 주소 가져오기"""
    try:
        # 외부와 연결을 시도하여 로컬 IP 확인
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

class Tetris:
    def __init__(self, x_offset):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.current_shape = 0
        self.x_offset = x_offset
        self.score = 0
        self.game_over = False
        self.game_started = False

    def spawn_piece(self):
        self.current_shape = random.randint(0, len(SHAPES) - 1)
        self.current_piece = SHAPES[self.current_shape]
        self.current_x = GRID_WIDTH // 2 - len(self.current_piece[0]) // 2
        self.current_y = 0

        if not self.is_valid_position():
            self.game_over = True

    def is_valid_position(self, piece=None, x=None, y=None):
        if piece is None:
            piece = self.current_piece
        if x is None:
            x = self.current_x
        if y is None:
            y = self.current_y

        for row in range(len(piece)):
            for col in range(len(piece[row])):
                if piece[row][col]:
                    new_x = x + col
                    new_y = y + row

                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return False

                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return False
        return True

    def rotate_piece(self):
        if not self.game_started:
            return
        rotated = [[self.current_piece[j][i] for j in range(len(self.current_piece))]
                   for i in range(len(self.current_piece[0]) - 1, -1, -1)]

        if self.is_valid_position(rotated):
            self.current_piece = rotated

    def move(self, dx, dy):
        if not self.game_started:
            return False
        if self.is_valid_position(x=self.current_x + dx, y=self.current_y + dy):
            self.current_x += dx
            self.current_y += dy
            return True
        return False

    def drop(self):
        if not self.game_started:
            return
        if not self.move(0, 1):
            self.lock_piece()

    def hard_drop(self):
        if not self.game_started:
            return
        while self.move(0, 1):
            pass
        self.lock_piece()

    def lock_piece(self):
        for row in range(len(self.current_piece)):
            for col in range(len(self.current_piece[row])):
                if self.current_piece[row][col]:
                    self.grid[self.current_y + row][self.current_x + col] = self.current_shape + 1

        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        lines_cleared = 0
        new_grid = []

        for row in self.grid:
            if 0 not in row:
                lines_cleared += 1
            else:
                new_grid.append(row)

        for _ in range(lines_cleared):
            new_grid.insert(0, [0 for _ in range(GRID_WIDTH)])

        self.grid = new_grid
        self.score += lines_cleared * 100

    def start_game(self):
        self.game_started = True
        self.spawn_piece()

    def draw(self, screen):
        # 게임 보드 그리기
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    color = COLORS[self.grid[y][x] - 1]
                    pygame.draw.rect(screen, color,
                                   (self.x_offset + x * CELL_SIZE, y * CELL_SIZE + 50,
                                    CELL_SIZE - 1, CELL_SIZE - 1))

        # 현재 블록 그리기
        if self.current_piece and not self.game_over and self.game_started:
            for row in range(len(self.current_piece)):
                for col in range(len(self.current_piece[row])):
                    if self.current_piece[row][col]:
                        color = COLORS[self.current_shape]
                        pygame.draw.rect(screen, color,
                                       (self.x_offset + (self.current_x + col) * CELL_SIZE,
                                        (self.current_y + row) * CELL_SIZE + 50,
                                        CELL_SIZE - 1, CELL_SIZE - 1))

        # 격자 그리기
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(screen, GRAY,
                           (self.x_offset + x * CELL_SIZE, 50),
                           (self.x_offset + x * CELL_SIZE, GRID_HEIGHT * CELL_SIZE + 50))
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(screen, GRAY,
                           (self.x_offset, y * CELL_SIZE + 50),
                           (self.x_offset + GRID_WIDTH * CELL_SIZE, y * CELL_SIZE + 50))

class NetworkGame:
    def __init__(self, is_host, host_ip='localhost', port=5555):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("2인용 Tetris - " + ("Host" if is_host else "Guest"))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.is_host = is_host
        self.host_ip = host_ip
        self.port = port
        self.local_ip = get_local_ip()

        # 플레이어 게임 인스턴스
        self.my_game = Tetris(50 if is_host else WINDOW_WIDTH // 2 + 50)
        self.opponent_game = Tetris(WINDOW_WIDTH // 2 + 50 if is_host else 50)

        self.running = True
        self.connected = False
        self.both_ready = False
        self.my_ready = False
        self.opponent_ready = False
        self.countdown = -1
        self.last_drop_time = 0

        # 네트워크 설정
        if is_host:
            self.setup_host()
        else:
            self.setup_guest()

    def setup_host(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(1)

        print(f"\n=== Host 서버 시작됨 ===")
        print(f"IP 주소: {self.local_ip}")
        print(f"포트: {self.port}")
        print(f"Guest는 '{self.local_ip}'로 접속하세요\n")

        # 연결 대기 스레드
        threading.Thread(target=self.accept_connection, daemon=True).start()

    def accept_connection(self):
        print("Guest 연결 대기 중...")
        self.conn, addr = self.server_socket.accept()
        print(f"Guest 연결됨: {addr}")
        self.connected = True

        # 데이터 수신 스레드 시작
        threading.Thread(target=self.receive_data, daemon=True).start()

    def setup_guest(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.host_ip, self.port))
            self.connected = True
            print(f"Host({self.host_ip})에 연결됨")
            self.conn = self.client_socket

            # 데이터 수신 스레드 시작
            threading.Thread(target=self.receive_data, daemon=True).start()
        except:
            print(f"Host({self.host_ip})에 연결할 수 없습니다")
            self.running = False

    def send_game_state(self):
        if self.connected:
            try:
                data = {
                    'grid': self.my_game.grid,
                    'current_piece': self.my_game.current_piece,
                    'current_x': self.my_game.current_x,
                    'current_y': self.my_game.current_y,
                    'current_shape': self.my_game.current_shape,
                    'score': self.my_game.score,
                    'game_over': self.my_game.game_over,
                    'ready': self.my_ready,
                    'game_started': self.my_game.game_started
                }
                self.conn.send(pickle.dumps(data))
            except:
                self.connected = False

    def receive_data(self):
        while self.running and self.connected:
            try:
                data = self.conn.recv(4096)
                if data:
                    game_state = pickle.loads(data)
                    self.opponent_game.grid = game_state['grid']
                    self.opponent_game.current_piece = game_state['current_piece']
                    self.opponent_game.current_x = game_state['current_x']
                    self.opponent_game.current_y = game_state['current_y']
                    self.opponent_game.current_shape = game_state['current_shape']
                    self.opponent_game.score = game_state['score']
                    self.opponent_game.game_over = game_state['game_over']
                    self.opponent_ready = game_state['ready']
                    self.opponent_game.game_started = game_state['game_started']

                    # 양쪽 다 준비되면 카운트다운 시작
                    if self.my_ready and self.opponent_ready and not self.both_ready:
                        self.both_ready = True
                        self.countdown = 3
            except:
                self.connected = False
                break

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if not self.my_game.game_started and self.connected:
                    if event.key == pygame.K_RETURN:  # Enter키로 준비
                        self.my_ready = not self.my_ready
                elif not self.my_game.game_over:
                    if event.key == pygame.K_LEFT:
                        self.my_game.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.my_game.move(1, 0)
                    elif event.key == pygame.K_DOWN:
                        self.my_game.drop()
                    elif event.key == pygame.K_UP:
                        self.my_game.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        self.my_game.hard_drop()

    def update(self):
        current_time = pygame.time.get_ticks()

        # 카운트다운 처리
        if self.both_ready and self.countdown > 0:
            if current_time % 1000 < 20:  # 1초마다
                self.countdown -= 1
                if self.countdown == 0:
                    # 게임 시작
                    self.my_game.start_game()
                    self.opponent_game.start_game()

        # 자동 낙하 (0.5초마다)
        if self.my_game.game_started and not self.my_game.game_over:
            if current_time - self.last_drop_time > 500:
                self.my_game.drop()
                self.last_drop_time = current_time

        # 게임 상태 전송
        self.send_game_state()

    def draw(self):
        self.screen.fill(BLACK)

        # 연결 전 상태
        if not self.connected:
            if self.is_host:
                info_text = [
                    "Host 서버 실행 중...",
                    f"IP 주소: {self.local_ip}",
                    f"포트: {self.port}",
                    "",
                    "Guest 접속 대기 중..."
                ]
                y = WINDOW_HEIGHT // 2 - 60
                for text in info_text:
                    rendered = self.font.render(text, True, WHITE)
                    self.screen.blit(rendered, (WINDOW_WIDTH // 2 - rendered.get_width() // 2, y))
                    y += 40
            else:
                status = self.font.render("Host에 연결 중...", True, WHITE)
                self.screen.blit(status, (WINDOW_WIDTH // 2 - status.get_width() // 2, WINDOW_HEIGHT // 2))

            pygame.display.flip()
            return

        # 플레이어 라벨
        if self.is_host:
            host_label = self.font.render("HOST (You)", True, WHITE)
            guest_label = self.font.render("GUEST", True, WHITE)
            self.screen.blit(host_label, (100, 10))
            self.screen.blit(guest_label, (WINDOW_WIDTH // 2 + 120, 10))
        else:
            host_label = self.font.render("HOST", True, WHITE)
            guest_label = self.font.render("GUEST (You)", True, WHITE)
            self.screen.blit(guest_label, (100, 10))
            self.screen.blit(host_label, (WINDOW_WIDTH // 2 + 120, 10))

        # 게임 시작 전 준비 상태 표시
        if not self.my_game.game_started:
            # 준비 상태 표시
            my_status = "준비 완료" if self.my_ready else "Enter키를 눌러 준비"
            opp_status = "준비 완료" if self.opponent_ready else "준비 대기 중..."

            my_color = GREEN if self.my_ready else WHITE
            opp_color = GREEN if self.opponent_ready else WHITE

            if self.is_host:
                my_text = self.small_font.render(my_status, True, my_color)
                opp_text = self.small_font.render(opp_status, True, opp_color)
                self.screen.blit(my_text, (80, WINDOW_HEIGHT // 2))
                self.screen.blit(opp_text, (WINDOW_WIDTH // 2 + 80, WINDOW_HEIGHT // 2))
            else:
                my_text = self.small_font.render(my_status, True, my_color)
                opp_text = self.small_font.render(opp_status, True, opp_color)
                self.screen.blit(opp_text, (80, WINDOW_HEIGHT // 2))
                self.screen.blit(my_text, (WINDOW_WIDTH // 2 + 80, WINDOW_HEIGHT // 2))

            # 카운트다운 표시
            if self.countdown > 0:
                countdown_text = self.font.render(str(self.countdown), True, RED)
                self.screen.blit(countdown_text, (WINDOW_WIDTH // 2 - 10, WINDOW_HEIGHT // 2 - 50))
            elif self.countdown == 0:
                start_text = self.font.render("START!", True, GREEN)
                self.screen.blit(start_text, (WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 50))

        # 게임 그리기
        self.my_game.draw(self.screen)
        self.opponent_game.draw(self.screen)

        # 점수 표시
        my_score = self.font.render(f"Score: {self.my_game.score}", True, WHITE)
        opp_score = self.font.render(f"Score: {self.opponent_game.score}", True, WHITE)

        if self.is_host:
            self.screen.blit(my_score, (50, WINDOW_HEIGHT - 40))
            self.screen.blit(opp_score, (WINDOW_WIDTH // 2 + 50, WINDOW_HEIGHT - 40))
        else:
            self.screen.blit(opp_score, (50, WINDOW_HEIGHT - 40))
            self.screen.blit(my_score, (WINDOW_WIDTH // 2 + 50, WINDOW_HEIGHT - 40))

        # 게임 오버 표시
        if self.my_game.game_over:
            game_over = self.font.render("GAME OVER", True, RED)
            x_pos = 50 if self.is_host else WINDOW_WIDTH // 2 + 50
            self.screen.blit(game_over, (x_pos + 50, WINDOW_HEIGHT // 2))

        if self.opponent_game.game_over:
            game_over = self.font.render("GAME OVER", True, RED)
            x_pos = WINDOW_WIDTH // 2 + 50 if self.is_host else 50
            self.screen.blit(game_over, (x_pos + 50, WINDOW_HEIGHT // 2))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        # 정리
        if hasattr(self, 'server_socket'):
            self.server_socket.close()
        if hasattr(self, 'conn'):
            self.conn.close()
        pygame.quit()

def main():
    print("\n=== 2인용 Tetris 게임 ===")
    print("1. Host로 시작")
    print("2. Guest로 시작")

    choice = input("\n선택 (1 또는 2): ")

    if choice == '1':
        game = NetworkGame(is_host=True)
    elif choice == '2':
        host_ip = input("Host IP 주소 입력 (기본값: localhost): ").strip() or 'localhost'
        game = NetworkGame(is_host=False, host_ip=host_ip)
    else:
        print("잘못된 선택입니다.")
        return

    game.run()

if __name__ == "__main__":
    main()
