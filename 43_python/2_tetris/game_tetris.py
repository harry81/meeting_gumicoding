import pygame
import random
import asyncio
import platform

# Initialize Pygame
pygame.init()

# Screen settings
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * GRID_WIDTH
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

# Colors
COLORS = [
    (0, 255, 255),  # Cyan (I)
    (0, 0, 255),    # Blue (J)
    (255, 165, 0),  # Orange (L)
    (255, 255, 0),  # Yellow (O)
    (0, 255, 0),    # Green (S)
    (255, 0, 0),    # Red (Z)
    (128, 0, 128)   # Purple (T)
]
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[0, 1, 0], [1, 1, 1]]   # T
]

# Game variables
FPS = 60
FALL_SPEED = 0.5  # Seconds per fall
FALL_TICK = 0

# Tetromino class
class Tetromino:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = COLORS[SHAPES.index(self.shape)]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def rotate(self):
        self.shape = list(zip(*self.shape[::-1]))

    def draw(self):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, self.color,
                                   ( (self.x + j) * BLOCK_SIZE, (self.y + i) * BLOCK_SIZE,
                                     BLOCK_SIZE - 1, BLOCK_SIZE - 1))

# Game grid
grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
current_piece = Tetromino()
score = 0
game_over = False

async def main():
    global current_piece, score, FALL_TICK, game_over
    clock = pygame.time.Clock()

    while not game_over:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.move(-1, 0)
                    if check_collision(current_piece, grid):
                        current_piece.move(1, 0)
                if event.key == pygame.K_RIGHT:
                    current_piece.move(1, 0)
                    if check_collision(current_piece, grid):
                        current_piece.move(-1, 0)
                if event.key == pygame.K_DOWN:
                    current_piece.move(0, 1)
                    if check_collision(current_piece, grid):
                        current_piece.move(0, -1)
                if event.key == pygame.K_UP:
                    current_piece.rotate()
                    if check_collision(current_piece, grid):
                        for _ in range(3):  # Rotate back
                            current_piece.rotate()

        # Update piece position
        FALL_TICK += clock.get_time() / 1000
        if FALL_TICK >= FALL_SPEED:
            current_piece.move(0, 1)
            if check_collision(current_piece, grid):
                current_piece.move(0, -1)
                place_piece(current_piece, grid)
                clear_lines()
                current_piece = Tetromino()
                if check_collision(current_piece, grid):
                    game_over = True
            FALL_TICK = 0

        # Draw
        screen.fill(BLACK)
        draw_grid(grid)
        current_piece.draw()

        # Display score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

def check_collision(piece, grid):
    for i, row in enumerate(piece.shape):
        for j, cell in enumerate(row):
            if cell:
                x, y = piece.x + j, piece.y + i
                if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT or (y >= 0 and grid[y][x]):
                    return True
    return False

def place_piece(piece, grid):
    for i, row in enumerate(piece.shape):
        for j, cell in enumerate(row):
            if cell and piece.y + i >= 0:
                grid[piece.y + i][piece.x + j] = piece.color

def clear_lines():
    global grid, score
    new_grid = [row for row in grid if any(cell is None for cell in row)]
    lines_cleared = GRID_HEIGHT - len(new_grid)
    score += lines_cleared * 100
    grid = [[None for _ in range(GRID_WIDTH)] for _ in range(lines_cleared)] + new_grid

def draw_grid(grid):
    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, cell,
                               (j * BLOCK_SIZE, i * BLOCK_SIZE,
                                BLOCK_SIZE - 1, BLOCK_SIZE - 1))
            else:
                pygame.draw.rect(screen, GRAY,
                               (j * BLOCK_SIZE, i * BLOCK_SIZE,
                                BLOCK_SIZE - 1, BLOCK_SIZE - 1), 1)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
