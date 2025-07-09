import pygame
import random

pygame.init()

# 화면 설정
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 30
COLUMNS = 10
ROWS = 20

# 색상 정의
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255), (0, 0, 255), (255, 127, 0),
    (255, 255, 0), (0, 255, 0), (148, 0, 211), (255, 0, 0)
]

# 테트로미노 정의
TETROMINOES = {
    'I': [[1, 1, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'Z': [[1, 1, 0], [0, 1, 1]],
}

class Tetromino:
    def __init__(self, x, y):
        self.shape = random.choice(list(TETROMINOES.values()))
        self.color = random.choice(COLORS)
        self.x = x
        self.y = y

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

class Player:
    def __init__(self, offset_x):
        self.offset_x = offset_x
        self.grid = [[0]*COLUMNS for _ in range(ROWS)]
        self.tetromino = Tetromino(3, 0)
        self.next_tetromino = Tetromino(3, 0)
        self.game_over = False

    def valid_position(self, shape, offset_x, offset_y):
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = x + self.tetromino.x + offset_x
                    new_y = y + self.tetromino.y + offset_y
                    if new_x < 0 or new_x >= COLUMNS or new_y >= ROWS:
                        return False
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return False
        return True

    def place_tetromino(self):
        for y, row in enumerate(self.tetromino.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[y + self.tetromino.y][x + self.tetromino.x] = self.tetromino.color
        lines = self.clear_lines()
        self.tetromino = self.next_tetromino
        self.next_tetromino = Tetromino(3, 0)
        if not self.valid_position(self.tetromino.shape, 0, 0):
            self.game_over = True
        return lines

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(cell == 0 for cell in row)]
        lines_cleared = ROWS - len(new_grid)
        for _ in range(lines_cleared):
            new_grid.insert(0, [0]*COLUMNS)
        self.grid = new_grid
        return lines_cleared

    def add_garbage(self, lines=1):
        for _ in range(lines):
            self.grid.pop(0)
            garbage = [0] * COLUMNS
            hole = random.randint(0, COLUMNS - 1)
            for i in range(COLUMNS):
                if i != hole:
                    garbage[i] = GRAY
            self.grid.append(garbage)

def draw_grid(screen, player, x_offset):
    for y, row in enumerate(player.grid):
        for x, cell in enumerate(row):
            color = cell if cell else WHITE
            pygame.draw.rect(screen, color, pygame.Rect(
                x_offset + x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)
            pygame.draw.rect(screen, BLACK, pygame.Rect(
                x_offset + x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

    for y, row in enumerate(player.tetromino.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, player.tetromino.color, pygame.Rect(
                    x_offset + (player.tetromino.x + x) * GRID_SIZE,
                    (player.tetromino.y + y) * GRID_SIZE,
                    GRID_SIZE, GRID_SIZE
                ), 0)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("2인용 테트리스")
    clock = pygame.time.Clock()

    p1 = Player(50)
    p2 = Player(SCREEN_WIDTH // 2 + 50)

    fall_time = 0
    fall_speed = 0.5

    key_cooldown = 150  # ms
    last_key_press_time = {
        "p1_left": 0, "p1_right": 0, "p1_down": 0, "p1_rotate": 0,
        "p2_left": 0, "p2_right": 0, "p2_down": 0, "p2_rotate": 0
    }

    running = True
    while running:
        screen.fill(BLACK)
        delta_time = clock.tick(60)
        fall_time += delta_time
        current_time = pygame.time.get_ticks()

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            for player in [p1, p2]:
                if not player.game_over:
                    if player.valid_position(player.tetromino.shape, 0, 1):
                        player.tetromino.y += 1
                    else:
                        lines = player.place_tetromino()
                        if lines > 0:
                            if player == p1:
                                p2.add_garbage(lines)
                            else:
                                p1.add_garbage(lines)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # Player 1
        if not p1.game_over:
            if keys[pygame.K_a] and current_time - last_key_press_time["p1_left"] > key_cooldown:
                if p1.valid_position(p1.tetromino.shape, -1, 0):
                    p1.tetromino.x -= 1
                last_key_press_time["p1_left"] = current_time
            if keys[pygame.K_d] and current_time - last_key_press_time["p1_right"] > key_cooldown:
                if p1.valid_position(p1.tetromino.shape, 1, 0):
                    p1.tetromino.x += 1
                last_key_press_time["p1_right"] = current_time
            if keys[pygame.K_s] and current_time - last_key_press_time["p1_down"] > key_cooldown:
                if p1.valid_position(p1.tetromino.shape, 0, 1):
                    p1.tetromino.y += 1
                last_key_press_time["p1_down"] = current_time
            if keys[pygame.K_w] and current_time - last_key_press_time["p1_rotate"] > key_cooldown:
                p1.tetromino.rotate()
                if not p1.valid_position(p1.tetromino.shape, 0, 0):
                    p1.tetromino.rotate()
                last_key_press_time["p1_rotate"] = current_time

        # Player 2
        if not p2.game_over:
            if keys[pygame.K_LEFT] and current_time - last_key_press_time["p2_left"] > key_cooldown:
                if p2.valid_position(p2.tetromino.shape, -1, 0):
                    p2.tetromino.x -= 1
                last_key_press_time["p2_left"] = current_time
            if keys[pygame.K_RIGHT] and current_time - last_key_press_time["p2_right"] > key_cooldown:
                if p2.valid_position(p2.tetromino.shape, 1, 0):
                    p2.tetromino.x += 1
                last_key_press_time["p2_right"] = current_time
            if keys[pygame.K_DOWN] and current_time - last_key_press_time["p2_down"] > key_cooldown:
                if p2.valid_position(p2.tetromino.shape, 0, 1):
                    p2.tetromino.y += 1
                last_key_press_time["p2_down"] = current_time
            if keys[pygame.K_UP] and current_time - last_key_press_time["p2_rotate"] > key_cooldown:
                p2.tetromino.rotate()
                if not p2.valid_position(p2.tetromino.shape, 0, 0):
                    p2.tetromino.rotate()
                last_key_press_time["p2_rotate"] = current_time

        draw_grid(screen, p1, p1.offset_x)
        draw_grid(screen, p2, p2.offset_x)

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
