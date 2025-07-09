import pygame
import random

pygame.init()

# 게임 설정
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 30
COLUMNS = 10
ROWS = 20

# 색상
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255), (0, 0, 255), (255, 127, 0),
    (255, 255, 0), (0, 255, 0), (148, 0, 211), (255, 0, 0)
]

# 테트로미노
TETROMINOES = {
    'I': [[1, 1, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'Z': [[1, 1, 0], [0, 1, 1]],
}

# 키 입력 타이머 초기화
key_cooldown = 150  # 밀리초 단위
last_key_press_time = {
    "p1_left": 0, "p1_right": 0, "p1_down": 0, "p1_rotate": 0,
    "p2_left": 0, "p2_right": 0, "p2_down": 0, "p2_rotate": 0
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
                    if (new_x < 0 or new_x >= COLUMNS or
                        new_y >= ROWS or self.grid[new_y][new_x]):
                        return False
        return True

    def place_tetromino(self):
        for y, row in enumerate(self.tetromino.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[y + self.tetromino.y][x + self.tetromino.x] = self.tetromino.color
        self.clear_lines()
        self.tetromino = self.next_tetromino
        self.next_tetromino = Tetromino(3, 0)
        if not self.valid_position(self.tetromino.shape, 0, 0):
            self.game_over = True

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
            garbage = [random.choice([0, 255]) for _ in range(COLUMNS)]
            self.grid.append([GRAY if cell == 255 else 0 for cell in garbage])

def draw_grid(screen, player, x_offset):
    for y, row in enumerate(player.grid):
        for x, cell in enumerate(row):
            color = cell if cell else WHITE
            pygame.draw.rect(screen, color, pygame.Rect(
                x_offset + x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)
            pygame.draw.rect(screen, BLACK, pygame.Rect(
                x_offset + x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

    # Draw current tetromino
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
    clock = pygame.time.Clock()

    p1 = Player(0)
    p2 = Player(SCREEN_WIDTH // 2)

    fall_time = 0
    fall_speed = 0.5

    running = True
    while running:
        screen.fill(BLACK)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            for player in [p1, p2]:
                if not player.game_over:
                    if player.valid_position(player.tetromino.shape, 0, 1):
                        player.tetromino.y += 1
                    else:
                        player.place_tetromino()
                        # 공격 시스템
                        lines = player.clear_lines()
                        if lines > 0:
                            if player == p1:
                                p2.add_garbage(lines)
                            else:
                                p1.add_garbage(lines)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()


        # Player 1 controls
        if not p1.game_over:
            if keys[pygame.K_a]:
                if p1.valid_position(p1.tetromino.shape, -1, 0):
                    p1.tetromino.x -= 1
            if keys[pygame.K_d]:
                if p1.valid_position(p1.tetromino.shape, 1, 0):
                    p1.tetromino.x += 1
            if keys[pygame.K_s]:
                if p1.valid_position(p1.tetromino.shape, 0, 1):
                    p1.tetromino.y += 1
            if keys[pygame.K_w]:
                p1.tetromino.rotate()
                if not p1.valid_position(p1.tetromino.shape, 0, 0):
                    p1.tetromino.rotate()  # rotate back

        # Player 2 controls
        if not p2.game_over:
            if keys[pygame.K_LEFT]:
                if p2.valid_position(p2.tetromino.shape, -1, 0):
                    p2.tetromino.x -= 1
            if keys[pygame.K_RIGHT]:
                if p2.valid_position(p2.tetromino.shape, 1, 0):
                    p2.tetromino.x += 1
            if keys[pygame.K_DOWN]:
                if p2.valid_position(p2.tetromino.shape, 0, 1):
                    p2.tetromino.y += 1
            if keys[pygame.K_UP]:
                p2.tetromino.rotate()
                if not p2.valid_position(p2.tetromino.shape, 0, 0):
                    p2.tetromino.rotate()

        draw_grid(screen, p1, 50)
        draw_grid(screen, p2, SCREEN_WIDTH // 2 + 50)

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
