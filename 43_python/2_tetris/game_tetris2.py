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
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 6)  # Extra space for preview
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
DARK_GRAY = (50, 50, 50)

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
BASE_FALL_SPEED = 0.5  # Seconds per fall
FALL_TICK = 0
LEVEL = 1
score = 0
game_over = False

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

    def draw(self, offset_x=0, offset_y=0):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell:
                    x, y = (self.x + j) * BLOCK_SIZE + offset_x, (self.y + i) * BLOCK_SIZE + offset_y
                    # Draw shadow for 3D effect
                    pygame.draw.rect(screen, DARK_GRAY, (x + 2, y + 2, BLOCK_SIZE - 1, BLOCK_SIZE - 1))
                    # Draw main block
                    pygame.draw.rect(screen, self.color, (x, y, BLOCK_SIZE - 1, BLOCK_SIZE - 1))
                    # Add texture pattern
                    pygame.draw.line(screen, WHITE, (x + 2, y + 2), (x + BLOCK_SIZE - 3, y + BLOCK_SIZE - 3), 1)
                    pygame.draw.line(screen, WHITE, (x + BLOCK_SIZE - 3, y + 2), (x + 2, y + BLOCK_SIZE - 3), 1)

# Game grid
grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
current_piece = Tetromino()
next_piece = Tetromino()

async def main():
    global current_piece, next_piece, score, FALL_TICK, game_over, LEVEL
    clock = pygame.time.Clock()
    clear_animation = False
    clear_timer = 0
    clear_lines_list = []

    while True:
        if game_over:
            screen.fill(BLACK)
            font = pygame.font.Font(None, 48)
            game_over_text = font.render(f"Game Over! Score: {score}", True, WHITE)
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    # Restart game
                    grid[:] = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
                    score = 0
                    LEVEL = 1
                    game_over = False
                    current_piece = Tetromino()
                    next_piece = Tetromino()
            await asyncio.sleep(1.0 / FPS)
            continue

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
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
                        for _ in range(3):
                            current_piece.rotate()

        # Update piece position
        if not clear_animation:
            FALL_TICK += clock.get_time() / 1000
            fall_speed = BASE_FALL_SPEED / (1 + LEVEL * 0.1)  # Increase speed with level
            if FALL_TICK >= fall_speed:
                current_piece.move(0, 1)
                if check_collision(current_piece, grid):
                    current_piece.move(0, -1)
                    place_piece(current_piece, grid)
                    clear_lines_list = clear_lines()
                    if clear_lines_list:
                        clear_animation = True
                        clear_timer = 0
                    else:
                        current_piece = next_piece
                        next_piece = Tetromino()
                        if check_collision(current_piece, grid):
                            game_over = True
                FALL_TICK = 0

        # Handle line clear animation
        if clear_animation:
            clear_timer += clock.get_time() / 1000
            if clear_timer >= 0.2:  # Flash for 0.2 seconds
                clear_animation = False

        # Draw
        screen.fill(BLACK)
        draw_grid(grid, clear_animation, clear_lines_list)
        if not clear_animation:
            current_piece.draw()

        # Draw next piece preview
        font = pygame.font.Font(None, 36)
        next_text = font.render("Next:", True, WHITE)
        screen.blit(next_text, (GRID_WIDTH * BLOCK_SIZE + 10, 10))
        next_piece.draw(offset_x=GRID_WIDTH * BLOCK_SIZE + 10, offset_y=50)

        # Display score and level
        score_text = font.render(f"Score: {score}", True, WHITE)
        level_text = font.render(f"Level: {LEVEL}", True, WHITE)
        screen.blit(score_text, (GRID_WIDTH * BLOCK_SIZE + 10, SCREEN_HEIGHT - 60))
        screen.blit(level_text, (GRID_WIDTH * BLOCK_SIZE + 10, SCREEN_HEIGHT - 30))

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
    global grid, score, LEVEL
    new_grid = [row for row in grid if any(cell is None for cell in row)]
    lines_cleared = GRID_HEIGHT - len(new_grid)
    if lines_cleared > 0:
        score += lines_cleared * 100 * LEVEL
        LEVEL = 1 + score // 1000  # Increase level every 1000 points
        grid = [[None for _ in range(GRID_WIDTH)] for _ in range(lines_cleared)] + new_grid
        return [i for i, row in enumerate(grid) if all(cell is not None for cell in row)]
    return []

def draw_grid(grid, clear_animation, clear_lines_list):
    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            x, y = j * BLOCK_SIZE, i * BLOCK_SIZE
            if clear_animation and i in clear_lines_list:
                # Flash effect for clearing lines
                color = WHITE if (pygame.time.get_ticks() // 100) % 2 == 0 else GRAY
                pygame.draw.rect(screen, color, (x, y, BLOCK_SIZE - 1, BLOCK_SIZE - 1))
            elif cell:
                # Draw block with shadow and texture
                pygame.draw.rect(screen, DARK_GRAY, (x + 2, y + 2, BLOCK_SIZE - 1, BLOCK_SIZE - 1))
                pygame.draw.rect(screen, cell, (x, y, BLOCK_SIZE - 1, BLOCK_SIZE - 1))
                pygame.draw.line(screen, WHITE, (x + 2, y + 2), (x + BLOCK_SIZE - 3, y + BLOCK_SIZE - 3), 1)
                pygame.draw.line(screen, WHITE, (x + BLOCK_SIZE - 3, y + 2), (x + 2, y + BLOCK_SIZE - 3), 1)
            else:
                pygame.draw.rect(screen, GRAY, (x, y, BLOCK_SIZE - 1, BLOCK_SIZE - 1), 1)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
