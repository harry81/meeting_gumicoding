import pygame
import sys

# 기본 설정
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("물리 시뮬레이션 도구")
clock = pygame.time.Clock()

# 물체 정의
class Ball:
    def __init__(self, x, y, radius, color, mass):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass
        self.vx = 0  # x축 속도
        self.vy = 0  # y축 속도
        self.gravity = 0.5  # 중력 가속도 (픽셀/프레임²)
        self.elasticity = 0.7  # 탄성 계수 (1: 완전 반사)

    def update(self):
        self.vy += self.gravity  # 중력 적용
        self.x += self.vx
        self.y += self.vy

        # 바닥 충돌 감지
        if self.y + self.radius >= HEIGHT:
            self.y = HEIGHT - self.radius
            self.vy *= -self.elasticity  # 반사

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

# 공 생성
ball = Ball(x=400, y=100, radius=20, color=(255, 100, 100), mass=1)

# 메인 루프
running = True
while running:
    screen.fill((30, 30, 30))  # 배경색

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ball.update()
    ball.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
