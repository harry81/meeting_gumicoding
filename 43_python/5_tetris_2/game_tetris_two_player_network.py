import pygame
import random
import socket
import pickle
import threading
import struct
from queue import Queue, Empty

# --- 1. 기본 설정 및 상수 ---
pygame.font.init()

# 화면 크기
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
PLAY_WIDTH = 300  # 10 blocks
PLAY_HEIGHT = 600 # 20 blocks
BLOCK_SIZE = 30

# 게임 보드 위치
TOP_LEFT_X_P1 = 50
TOP_LEFT_Y = SCREEN_HEIGHT - PLAY_HEIGHT - 50
TOP_LEFT_X_P2 = SCREEN_WIDTH - PLAY_WIDTH - 50

# 테트로미노 모양
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

# 모양과 색상
SHAPES = [S, Z, I, O, J, L, T]
SHAPE_COLORS = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]

# --- 2. 블록 및 게임 로직 클래스 ---

class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0

class TetrisGame:
    def __init__(self):
        self.grid = self.create_grid()
        self.current_piece = self.get_shape()
        self.next_piece = self.get_shape()
        self.fall_time = 0
        self.fall_speed = 0.27
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.garbage_to_add = 0

    def create_grid(self, locked_positions={}):
        grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                if (x, y) in locked_positions:
                    c = locked_positions[(x, y)]
                    grid[y][x] = c
        return grid

    def get_shape(self):
        return Piece(5, 0, random.choice(SHAPES))

    def convert_shape_format(self, piece):
        positions = []
        shape_format = piece.shape[piece.rotation % len(piece.shape)]
        for i, line in enumerate(shape_format):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    positions.append((piece.x + j, piece.y + i))
        for i, pos in enumerate(positions):
            positions[i] = (pos[0] - 2, pos[1] - 4)
        return positions

    def valid_space(self, piece):
        accepted_pos = [[(j, i) for j in range(10) if self.grid[i][j] == (0, 0, 0)] for i in range(20)]
        accepted_pos = [j for sub in accepted_pos for j in sub]
        formatted = self.convert_shape_format(piece)
        for pos in formatted:
            if pos not in accepted_pos:
                if pos[1] > -1:
                    return False
        return True

    def check_lost(self, positions):
        for pos in positions:
            _, y = pos
            if y < 1:
                self.game_over = True
                return True
        return False

    def update_grid(self, locked_positions):
        self.grid = self.create_grid(locked_positions)

    def clear_lines(self, locked_positions):
        inc = 0
        full_rows = []
        for i in range(len(self.grid) - 1, -1, -1):
            row = self.grid[i]
            if (0, 0, 0) not in row:
                inc += 1
                full_rows.append(i)
                for j in range(len(row)):
                    del locked_positions[(j, i)]

        if inc > 0:
            for key in sorted(list(locked_positions), key=lambda x: x[1])[::-1]:
                x, y = key
                lines_to_drop = sum(1 for r in full_rows if y < r)
                if lines_to_drop > 0:
                    new_key = (x, y + lines_to_drop)
                    locked_positions[new_key] = locked_positions.pop(key)

        self.score += inc * 10
        self.lines_cleared += inc
        return inc

    def add_garbage_lines(self, num_lines, locked_positions):
        new_locked = {}
        for (x, y), color in locked_positions.items():
            if y - num_lines >= 0:
                new_locked[(x, y - num_lines)] = color
            else:
                self.game_over = True

        locked_positions.clear()
        locked_positions.update(new_locked)

        hole = random.randint(0, 9)
        for i in range(num_lines):
            for j in range(10):
                if j != hole:
                    locked_positions[(j, 19 - i)] = (128, 128, 128)

# --- 3. 네트워크 클래스 (개선됨) ---
class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = ""
        self.port = 5555
        self.addr = (self.host, self.port)
        self.conn = None
        self.player_id = 0
        self.receive_thread = None
        self.running = False
        self.data_queue = Queue()

    def start_server(self):
        try:
            self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.client.bind(self.addr)
            self.client.listen(1)
            print(f"[SERVER] Waiting for connection on {self.get_local_ip()}:{self.port}")
            self.conn, addr = self.client.accept()
            print("[SERVER] Connected to:", addr)
            self.player_id = 1
            self.running = True
            self.receive_thread = threading.Thread(target=self._receive_loop)
            self.receive_thread.daemon = True
            self.receive_thread.start()
        except socket.error as e:
            print(f"[ERROR] Server could not start: {e}")

    def connect_to_server(self, host_ip):
        self.host = host_ip
        self.addr = (self.host, self.port)
        try:
            self.client.connect(self.addr)
            self.conn = self.client
            self.player_id = 2
            self.running = True
            self.receive_thread = threading.Thread(target=self._receive_loop)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            return True
        except socket.error as e:
            print(f"[ERROR] Could not connect to {host_ip}: {e}")
            return False

    def send(self, data):
        if not self.running:
            return
        try:
            pickled_data = pickle.dumps(data)
            message = struct.pack('!I', len(pickled_data)) + pickled_data
            self.conn.sendall(message)
        except socket.error as e:
            print(f"Send Error: {e}")
            self.running = False

    def _receive_loop(self):
        while self.running:
            try:
                raw_msglen = self._recv_all(4)
                if not raw_msglen:
                    break
                msglen = struct.unpack('!I', raw_msglen)[0]
                data = self._recv_all(msglen)
                if not data:
                    break
                unpickled_data = pickle.loads(data)
                self.data_queue.put(unpickled_data)
            except (socket.error, pickle.UnpicklingError, EOFError, struct.error):
                break
        self.running = False
        self.data_queue.put("CONNECTION_LOST")

    def _recv_all(self, n):
        data = bytearray()
        while len(data) < n:
            try:
                packet = self.conn.recv(n - len(data))
                if not packet:
                    return None
                data.extend(packet)
            except socket.error:
                return None
        return data

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        try:
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            try:
                IP = socket.gethostbyname(socket.gethostname())
            except Exception:
                IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def close(self):
        self.running = False
        if self.conn:
            try:
                self.conn.shutdown(socket.SHUT_RDWR)
                self.conn.close()
            except socket.error:
                pass
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1)

# --- 4. 그리기 함수 ---

def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(label, (SCREEN_WIDTH/2 - label.get_width()/2, SCREEN_HEIGHT/2 - label.get_height()/2))

def draw_grid(surface, grid, offset_x=0):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, (128, 128, 128), (offset_x + j*BLOCK_SIZE, TOP_LEFT_Y + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_window(surface, grid_p1, grid_p2, score_p1=0, score_p2=0):
    surface.fill((0, 0, 0))
    font = pygame.font.SysFont('comicsans', 30)

    # Player 1
    label_p1 = font.render('YOU (Player 1)', 1, (255, 255, 255))
    surface.blit(label_p1, (TOP_LEFT_X_P1 + PLAY_WIDTH/2 - label_p1.get_width()/2, TOP_LEFT_Y - 40))
    for i in range(len(grid_p1)):
        for j in range(len(grid_p1[i])):
            pygame.draw.rect(surface, grid_p1[i][j], (TOP_LEFT_X_P1 + j*BLOCK_SIZE, TOP_LEFT_Y + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    pygame.draw.rect(surface, (255, 0, 0), (TOP_LEFT_X_P1, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 4)
    draw_grid(surface, grid_p1, TOP_LEFT_X_P1)

    # Player 2
    label_p2 = font.render('OPPONENT (Player 2)', 1, (255, 255, 255))
    surface.blit(label_p2, (TOP_LEFT_X_P2 + PLAY_WIDTH/2 - label_p2.get_width()/2, TOP_LEFT_Y - 40))
    for i in range(len(grid_p2)):
        for j in range(len(grid_p2[i])):
            pygame.draw.rect(surface, grid_p2[i][j], (TOP_LEFT_X_P2 + j*BLOCK_SIZE, TOP_LEFT_Y + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    pygame.draw.rect(surface, (0, 0, 255), (TOP_LEFT_X_P2, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 4)
    draw_grid(surface, grid_p2, TOP_LEFT_X_P2)

    # Score display
    score_label_p1 = font.render(f'Score: {score_p1}', 1, (255,255,255))
    surface.blit(score_label_p1, (TOP_LEFT_X_P1, TOP_LEFT_Y + PLAY_HEIGHT + 10))
    score_label_p2 = font.render(f'Score: {score_p2}', 1, (255,255,255))
    surface.blit(score_label_p2, (TOP_LEFT_X_P2, TOP_LEFT_Y + PLAY_HEIGHT + 10))

def draw_next_shape(piece, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (255,255,255))
    sx = SCREEN_WIDTH/2 - 100
    sy = SCREEN_HEIGHT/2 - 50
    shape_format = piece.shape[piece.rotation % len(piece.shape)]
    for i, line in enumerate(shape_format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, piece.color, (sx + j*BLOCK_SIZE, sy + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    surface.blit(label, (sx + 10, sy - 30))

def draw_input_box(screen, text, prompt, active):
    font = pygame.font.SysFont('comicsans', 32)
    box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 40)
    color = pygame.Color('dodgerblue2') if active else pygame.Color('lightskyblue3')
    prompt_label = font.render(prompt, 1, (255, 255, 255))
    screen.blit(prompt_label, (box_rect.x, box_rect.y - 40))
    pygame.draw.rect(screen, color, box_rect, 2)
    text_surface = font.render(text, True, (255, 255, 255))
    screen.blit(text_surface, (box_rect.x + 5, box_rect.y + 5))
    box_rect.w = max(300, text_surface.get_width() + 10)

def main(win):
    locked_positions = {}
    game = TetrisGame()
    network = Network()
    opponent_state = {'grid': game.create_grid(), 'score': 0, 'game_over': False}

    menu_running = True
    role = None
    input_box_text = ''
    input_active = False

    while menu_running:
        win.fill((0, 0, 0))
        draw_text_middle(win, 'Press H for Host, G for Guest', 60, (255, 255, 255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_running = False
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    role = 'host'
                    menu_running = False
                if event.key == pygame.K_g:
                    role = 'guest'
                    input_active = True
                    menu_running = False

    if not role: return

    if role == 'host':
        server_thread = threading.Thread(target=network.start_server)
        server_thread.daemon = True
        server_thread.start()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    network.close()
                    pygame.quit()
                    return
            win.fill((0,0,0))
            local_ip = network.get_local_ip()
            draw_text_middle(win, f'Waiting for Guest...Your IP is: {local_ip}', 40, (255, 255, 255))
            pygame.display.update()
            if network.conn:
                waiting = False
            if not server_thread.is_alive() and not network.conn:
                draw_text_middle(win, 'Server failed to start.', 40, (255, 0, 0))
                pygame.display.update()
                pygame.time.delay(2000)
                return
            pygame.time.delay(100)

    elif role == 'guest':
        input_prompt = "Enter Host IP Address:"
        while not network.conn:
            win.fill((0,0,0))
            draw_input_box(win, input_box_text, input_prompt, input_active)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if not network.connect_to_server(input_box_text):
                            input_prompt = "Connection Failed. Try Again:"
                            input_box_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        input_box_text = input_box_text[:-1]
                    else:
                        input_box_text += event.unicode

    if not network.conn:
        print("Could not establish connection.")
        return

    clock = pygame.time.Clock()
    run = True
    while run:
        game.fall_time += clock.get_rawtime()
        clock.tick()

        if game.fall_time / 1000 > game.fall_speed:
            game.fall_time = 0
            game.current_piece.y += 1
            if not (game.valid_space(game.current_piece)) and game.current_piece.y > 0:
                game.current_piece.y -= 1
                piece_pos = game.convert_shape_format(game.current_piece)
                for pos in piece_pos:
                    locked_positions[pos] = game.current_piece.color
                game.current_piece = game.next_piece
                game.next_piece = game.get_shape()
                lines_cleared = game.clear_lines(locked_positions)
                garbage_to_send = 0
                if lines_cleared == 2: garbage_to_send = 1
                elif lines_cleared == 3: garbage_to_send = 2
                elif lines_cleared == 4: garbage_to_send = 4
                if game.check_lost(locked_positions):
                    game.game_over = True
                network.send({
                    'grid': game.create_grid(locked_positions),
                    'score': game.score,
                    'game_over': game.game_over,
                    'garbage': garbage_to_send
                })

        if game.garbage_to_add > 0:
            game.add_garbage_lines(game.garbage_to_add, locked_positions)
            game.garbage_to_add = 0
            game.update_grid(locked_positions)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and not game.game_over:
                if event.key == pygame.K_LEFT:
                    game.current_piece.x -= 1
                    if not game.valid_space(game.current_piece): game.current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    game.current_piece.x += 1
                    if not game.valid_space(game.current_piece): game.current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    game.current_piece.y += 1
                    if not game.valid_space(game.current_piece): game.current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    game.current_piece.rotation = (game.current_piece.rotation + 1) % len(game.current_piece.shape)
                    if not game.valid_space(game.current_piece):
                        game.current_piece.rotation = (game.current_piece.rotation - 1) % len(game.current_piece.shape)
                elif event.key == pygame.K_SPACE:
                    while game.valid_space(game.current_piece):
                        game.current_piece.y += 1
                    game.current_piece.y -= 1
                    game.fall_time = game.fall_speed * 1000 + 1

        try:
            while not network.data_queue.empty():
                opponent_data = network.data_queue.get_nowait()
                if opponent_data == "CONNECTION_LOST":
                    run = False
                    draw_text_middle(win, "Opponent Disconnected", 60, (255, 0, 0))
                    pygame.display.update()
                    pygame.time.delay(2000)
                    break
                opponent_state.update(opponent_data)
                if opponent_data.get('garbage', 0) > 0:
                    game.garbage_to_add += opponent_data['garbage']
        except Empty:
            pass

        if not network.running and run:
            run = False
            draw_text_middle(win, "Connection Lost", 60, (255, 0, 0))
            pygame.display.update()
            pygame.time.delay(2000)

        game.update_grid(locked_positions)
        temp_grid_p1 = [row[:] for row in game.grid]
        shape_pos = game.convert_shape_format(game.current_piece)
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                temp_grid_p1[y][x] = game.current_piece.color

        p1_grid, p2_grid = (temp_grid_p1, opponent_state['grid']) if network.player_id == 1 else (opponent_state['grid'], temp_grid_p1)
        p1_score, p2_score = (game.score, opponent_state['score']) if network.player_id == 1 else (opponent_state['score'], game.score)

        # The drawing should be consistent. Player 1 is always on the left.
        if network.player_id == 1:
            draw_window(win, temp_grid_p1, opponent_state['grid'], game.score, opponent_state['score'])
        else:
            # Guest needs to draw its own grid on the left, and host's grid on the right
            draw_window(win, temp_grid_p1, opponent_state['grid'], game.score, opponent_state['score'])


        draw_next_shape(game.next_piece, win)

        if game.game_over or opponent_state['game_over']:
            win_msg = "YOU WIN!" if opponent_state['game_over'] else "YOU LOSE!"
            win_color = (0, 255, 0) if opponent_state['game_over'] else (255, 0, 0)
            draw_text_middle(win, win_msg, 80, win_color)
            if not game.game_over: # If opponent lost, send one last confirmation
                 network.send({'grid': game.grid, 'score': game.score, 'game_over': True, 'garbage': 0})
            game.game_over = True # Stop local player input

        pygame.display.update()

        if game.game_over:
            pygame.time.delay(3000)
            run = False

    network.close()

if __name__ == "__main__":
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('2P Tetris')
    main(win)
    pygame.quit()
