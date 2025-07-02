import pygame
import random
import asyncio
import platform

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH = 800
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chrome Dino Game")

# Colors
COLORS = [
    (0, 0, 0),      # Black
    (34, 139, 34),  # Forest Green
    (139, 69, 19),  # Brown
    (128, 0, 128),  # Purple
    (0, 128, 128)   # Teal
]
WHITE = (255, 255, 255)

# Game variables
FPS = 60
GRAVITY = 0.6
JUMP_VEL = -10
DINO_Y = HEIGHT - 60
CACTUS_SPEED = 5

# Dino class with improved shape
class Dino:
    def __init__(self):
        self.x = 50
        self.y = DINO_Y
        self.vel_y = 0
        self.jumping = False
        self.color = random.choice(COLORS)  # Random color for dino

    def jump(self):
        if not self.jumping:
            self.vel_y = JUMP_VEL
            self.jumping = True

    def update(self):
        if self.jumping:
            self.y += self.vel_y
            self.vel_y += GRAVITY
            if self.y >= DINO_Y:
                self.y = DINO_Y
                self.jumping = False
                self.vel_y = 0

    def draw(self):
        # Draw dino with T-Rex-like shape
        # Head
        pygame.draw.rect(screen, self.color, (self.x + 30, self.y - 20, 20, 20))
        # Body
        pygame.draw.rect(screen, self.color, (self.x + 10, self.y, 30, 20))
        # Legs
        pygame.draw.rect(screen, self.color, (self.x + 10, self.y + 20, 10, 20))
        pygame.draw.rect(screen, self.color, (self.x + 20, self.y + 20, 10, 20))
        # Tail
        pygame.draw.rect(screen, self.color, (self.x, self.y + 10, 10, 10))
        # Eye
        pygame.draw.circle(screen, WHITE, (self.x + 40, self.y - 15), 3)

# Cactus class with random color
class Cactus:
    def __init__(self):
        self.x = WIDTH
        self.y = HEIGHT - 40
        self.width = 20
        self.height = 40
        self.color = random.choice(COLORS)  # Random color for cactus

    def update(self):
        self.x -= CACTUS_SPEED

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

# Game setup
dino = Dino()
cacti = []
score = 0
clock = pygame.time.Clock()

# Spawn cactus periodically
spawn_timer = 0
SPAWN_INTERVAL = 1000  # Milliseconds

async def main():
    global score, spawn_timer
    running = True

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    dino.jump()

        # Update
        dino.update()

        # Spawn cactus
        spawn_timer += clock.get_time()
        if spawn_timer > SPAWN_INTERVAL:
            cacti.append(Cactus())
            spawn_timer = 0

        # Update cacti
        for cactus in cacti[:]:
            cactus.update()
            if cactus.x < -cactus.width:
                cacti.remove(cactus)
                score += 1

            # Collision detection
            dino_rect = pygame.Rect(dino.x, dino.y - 20, 50, 60)  # Adjusted for new dino shape
            cactus_rect = pygame.Rect(cactus.x, cactus.y, cactus.width, cactus.height)
            if dino_rect.colliderect(cactus_rect):
                running = False

        # Draw
        screen.fill(WHITE)
        dino.draw()
        for cactus in cacti:
            cactus.draw()

        # Display score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, COLORS[0])  # Black for score
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
