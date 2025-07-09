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
CELL_SIZE = 25  # 3명이 들어가도록 크기 조정
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH * 3 + 250  # 3명 화면 + 여백
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT + 120

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
                                   (self.x_offset + x * CELL_SIZE, y * CELL_SIZE + 60,
                                    CELL_SIZE - 1, CELL_SIZE - 1))

        # 현재 블록 그리기
        if self.current_piece and not self.game_over and self.game_started:
            for row in range(len(self.current_piece)):
                for col in range(len(self.current_piece[row])):
                    if self.current_piece[row][col]:
                        color = COLORS[self.current_shape]
                        pygame.draw.rect(screen, color,
                                       (self.x_offset + (self.current_x + col) * CELL_SIZE,
                                        (self.current_y + row) * CELL_SIZE + 60,
                                        CELL_SIZE - 1, CELL_SIZE - 1))

        # 격자 그리기
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(screen, GRAY,
                           (self.x_offset + x * CELL_SIZE, 60),
                           (self.x_offset + x * CELL_SIZE, GRID_HEIGHT * CELL_SIZE + 60))
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(screen, GRAY,
                           (self.x_offset, y * CELL_SIZE + 60),
                           (self.x_offset + GRID_WIDTH * CELL_SIZE, y * CELL_SIZE + 60))

class NetworkGame:
    def __init__(self, player_type, host_ip='localhost', port=5555):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 20)

        self.player_type = player_type  # 'host', 'guest1', 'guest2'
        self.player_id = {'host': 0, 'guest1': 1, 'guest2': 2}[player_type]
        pygame.display.set_caption(f"3인용 Tetris - {player_type.upper()}")

        self.host_ip = host_ip
        self.port = port
        self.local_ip = get_local_ip()

        # 3명의 게임 인스턴스
        x_positions = [30, 30 + GRID_WIDTH * CELL_SIZE + 60, 30 + (GRID_WIDTH * CELL_SIZE + 60) * 2]
        self.games = [Tetris(x_pos) for x_pos in x_positions]
        self.my_game = self.games[self.player_id]

        self.running = True
        self.connected = False
        self.all_connected = False
        self.ready_states = [False, False, False]
        self.all_ready = False
        self.countdown = -1
        self.last_drop_time = 0

        # 연결 상태
        self.connections = [None, None, None]
        self.connections[self.player_id] = 'self'

        # 네트워크 설정
        if player_type == 'host':
            self.setup_host()
        else:
            self.setup_guest()

    def setup_host(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(2)  # 2명의 guest 대기

        print(f"\n=== Host 서버 시작됨 ===")
        print(f"IP 주소: {self.local_ip}")
        print(f"포트: {self.port}")
        print(f"Guest들은 '{self.local_ip}'로 접속하세요\n")

        self.guest_connections = []
        threading.Thread(target=self.accept_connections, daemon=True).start()

    def accept_connections(self):
        print("Guest들의 연결을 대기 중...")
        while len(self.guest_connections) < 2:
            conn, addr = self.server_socket.accept()
            guest_id = len(self.guest_connections) + 1
            self.guest_connections.append((conn, guest_id))
            self.connections[guest_id] = conn
            print(f"Guest{guest_id} 연결됨: {addr}")

            # 게스트에게 ID 전송
            conn.send(pickle.dumps({'type': 'assign_id', 'id': guest_id}))

            # 데이터 수신 스레드 시작
            threading.Thread(target=self.receive_data_host, args=(conn, guest_id), daemon=True).start()

            if len(self.guest_connections) == 2:
                self.all_connected = True
                self.connected = True
                print("모든 플레이어가 연결되었습니다!")

    def setup_guest(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.host_ip, self.port))
            print(f"Host({self.host_ip})에 연결됨")

            # ID 할당 받기
            data = pickle.loads(self.client_socket.recv(4096))
            if data['type'] == 'assign_id':
                self.player_id = data['id']
                self.my_game = self.games[self.player_id]
                print(f"플레이어 ID: Guest{self.player_id}")

            self.connected = True
            threading.Thread(target=self.receive_data_guest, daemon=True).start()
        except Exception as e:
            print(f"Host({self.host_ip})에 연결할 수 없습니다: {e}")
            self.running = False

    def broadcast_game_state(self):
        if not self.connected:
            return

        data = {
            'type': 'game_state',
            'player_id': self.player_id,
            'game_data': {
                'grid': self.my_game.grid,
                'current_piece': self.my_game.current_piece,
                'current_x': self.my_game.current_x,
                'current_y': self.my_game.current_y,
                'current_shape': self.my_game.current_shape,
                'score': self.my_game.score,
                'game_over': self.my_game.game_over,
                'game_started': self.my_game.game_started
            },
            'ready': self.ready_states[self.player_id],
            'all_connected': self.all_connected
        }

        try:
            if self.player_type == 'host':
                # 모든 게스트에게 전송
                for conn, _ in self.guest_connections:
                    conn.send(pickle.dumps(data))
            else:
                # 호스트에게 전송
                self.client_socket.send(pickle.dumps(data))
        except:
            self.connected = False

    def receive_data_host(self, conn, guest_id):
        while self.running and self.connected:
            try:
                data = pickle.loads(conn.recv(4096))
                if data['type'] == 'game_state':
                    self.update_player_state(data)

                    # 다른 플레이어들에게 전파
                    for other_conn, other_id in self.guest_connections:
                        if other_id != guest_id:
                            other_conn.send(pickle.dumps(data))
            except:
                print(f"Guest{guest_id} 연결 끊김")
                break

    def receive_data_guest(self):
        while self.running and self.connected:
            try:
                data = pickle.loads(self.client_socket.recv(4096))
                if data['type'] == 'game_state':
                    self.update_player_state(data)
                    self.all_connected = data.get('all_connected', False)
            except:
                self.connected = False
                break

    def update_player_state(self, data):
        player_id = data['player_id']
        if player_id != self.player_id:
            game_data = data['game_data']
            self.games[player_id].grid = game_data['grid']
            self.games[player_id].current_piece = game_data['current_piece']
            self.games[player_id].current_x = game_data['current_x']
            self.games[player_id].current_y = game_data['current_y']
            self.games[player_id].current_shape = game_data['current_shape']
            self.games[player_id].score = game_data['score']
            self.games[player_id].game_over = game_data['game_over']
            self.games[player_id].game_started = game_data['game_started']
            self.ready_states[player_id] = data['ready']

        # 모두 준비되었는지 확인
        if self.all_connected and all(self.ready_states) and not self.all_ready:
            self.all_ready = True
            self.countdown = 3

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if not self.my_game.game_started and self.all_connected:
                    if event.key == pygame.K_RETURN:
                        self.ready_states[self.player_id] = not self.ready_states[self.player_id]
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
        if self.all_ready and self.countdown > 0:
            if current_time % 1000 < 20:
                self.countdown -= 1
                if self.countdown == 0:
                    for game in self.games:
                        game.start_game()

        # 자동 낙하
        if self.my_game.game_started and not self.my_game.game_over:
            if current_time - self.last_drop_time > 500:
                self.my_game.drop()
                self.last_drop_time = current_time

        # 게임 상태 전송
        self.broadcast_game_state()

    def draw(self):
        self.screen.fill(BLACK)

        # 연결 대기 화면
        if not self.all_connected:
            if self.player_type == 'host':
                info_text = [
                    "Host 서버 실행 중...",
                    f"IP 주소: {self.local_ip}",
                    f"포트: {self.port}",
                    "",
                    f"연결된 플레이어: {len(self.guest_connections) + 1}/3",
                    "모든 플레이어를 기다리는 중..."
                ]
                y = WINDOW_HEIGHT // 2 - 80
                for text in info_text:
                    rendered = self.font.render(text, True, WHITE)
                    self.screen.blit(rendered, (WINDOW_WIDTH // 2 - rendered.get_width() // 2, y))
                    y += 35
            else:
                status = self.font.render("다른 플레이어를 기다리는 중...", True, WHITE)
                self.screen.blit(status, (WINDOW_WIDTH // 2 - status.get_width() // 2, WINDOW_HEIGHT // 2))

            pygame.display.flip()
            return

        # 플레이어 라벨
        labels = ["HOST", "GUEST 1", "GUEST 2"]
        for i in range(3):
            label = labels[i]
            if i == self.player_id:
                label += " (You)"
            text = self.small_font.render(label, True, WHITE)
            x_pos = 30 + i * (GRID_WIDTH * CELL_SIZE + 60) + (GRID_WIDTH * CELL_SIZE // 2) - text.get_width() // 2
            self.screen.blit(text, (x_pos, 10))

        # 준비 상태 표시
        if not self.my_game.game_started:
            for i in range(3):
                status = "준비 완료" if self.ready_states[i] else "준비 대기 중..."
                color = GREEN if self.ready_states[i] else WHITE
                if i == self.player_id and not self.ready_states[i]:
                    status = "Enter키를 눌러 준비"

                text = self.small_font.render(status, True, color)
                x_pos = 30 + i * (GRID_WIDTH * CELL_SIZE + 60) + (GRID_WIDTH * CELL_SIZE // 2) - text.get_width() // 2
                self.screen.blit(text, (x_pos, WINDOW_HEIGHT // 2))

            # 카운트다운
            if self.countdown > 0:
                countdown_text = self.font.render(str(self.countdown), True, RED)
                self.screen.blit(countdown_text, (WINDOW_WIDTH // 2 - 10, WINDOW_HEIGHT // 2 - 50))
            elif self.countdown == 0:
                start_text = self.font.render("START!", True, GREEN)
                self.screen.blit(start_text, (WINDOW_WIDTH // 2 - 35, WINDOW_HEIGHT // 2 - 50))

        # 게임 그리기
        for game in self.games:
            game.draw(self.screen)

        # 점수 표시
        for i in range(3):
            score_text = self.small_font.render(f"Score: {self.games[i].score}", True, WHITE)
            x_pos = 30 + i * (GRID_WIDTH * CELL_SIZE + 60)
            self.screen.blit(score_text, (x_pos, WINDOW_HEIGHT - 30))

            # 게임 오버 표시
            if self.games[i].game_over:
                game_over = self.small_font.render("GAME OVER", True, RED)
                x_pos = 30 + i * (GRID_WIDTH * CELL_SIZE + 60) + (GRID_WIDTH * CELL_SIZE // 2) - game_over.get_width() // 2
                self.screen.blit(game_over, (x_pos, WINDOW_HEIGHT // 2 + 50))

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
        if hasattr(self, 'client_socket'):
            self.client_socket.close()
        pygame.quit()

def main():
    print("\n=== 3인용 Tetris 게임 ===")
    print("1. Host로 시작")
    print("2. Guest로 시작")

    choice = input("\n선택 (1 또는 2): ")

    if choice == '1':
        game = NetworkGame('host')
    elif choice == '2':
        host_ip = input("Host IP 주소 입력 (기본값: localhost): ").strip() or 'localhost'
        game = NetworkGame('guest1', host_ip=host_ip)  # guest1 또는 guest2로 자동 할당됨
    else:
        print("잘못된 선택입니다.")
        return

    game.run()

if __name__ == "__main__":
    main()
