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
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game variables
FPS = 60
GRAVITY = 0.6
JUMP_VEL = -10
DINO_Y = HEIGHT - 60
CACTUS_SPEED = 5

# Dino class
class Dino:
    def __init__(self):
        self.x = 50
        self.y = DINO_Y
        self.vel_y = 0
        self.jumping = False

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
        pygame.draw.rect(screen, BLACK, (self.x, self.y, 40, 40))  # Simple dino rectangle

# Cactus class
class Cactus:
    def __init__(self):
        self.x = WIDTH
        self.y = HEIGHT - 40
        self.width = 20
        self.height = 40

    def update(self):
        self.x -= CACTUS_SPEED

    def draw(self):
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height))

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
            dino_rect = pygame.Rect(dino.x, dino.y, 40, 40)
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
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
