import pygame
import sys
import math
import random

# 초기 설정
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Physics Simulation Tool")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# 색상 정의
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 100)

# 공 클래스
class Ball:
    def __init__(self, x, y, radius=20, color=RED, mass=1.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass
        self.vx = 0
        self.vy = 0
        self.gravity = 0.5
        self.elasticity = 0.8
        self.drag = 0.99  # 공기 저항
        self.selected = False
        self.initial_pos = (x, y)

    def update(self):
        if not self.selected:
            self.vy += self.gravity
            self.vx *= self.drag
            self.vy *= self.drag
            self.x += self.vx
            self.y += self.vy

            # 벽 충돌
            if self.x - self.radius <= 0 or self.x + self.radius >= WIDTH:
                self.vx *= -self.elasticity
                self.x = max(self.radius, min(WIDTH - self.radius, self.x))
            if self.y - self.radius <= 0 or self.y + self.radius >= HEIGHT:
                self.vy *= -self.elasticity
                self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        # 속도 벡터 화살표
        pygame.draw.line(surface, YELLOW, (int(self.x), int(self.y)),
                         (int(self.x + self.vx * 5), int(self.y + self.vy * 5)), 2)

    def check_collision(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        distance = math.hypot(dx, dy)
        if distance < self.radius + other.radius:
            angle = math.atan2(dy, dx)
            total_mass = self.mass + other.mass
            new_vx1 = (self.vx * (self.mass - other.mass) + 2 * other.mass * other.vx) / total_mass
            new_vy1 = (self.vy * (self.mass - other.mass) + 2 * other.mass * other.vy) / total_mass
            new_vx2 = (other.vx * (other.mass - self.mass) + 2 * self.mass * self.vx) / total_mass
            new_vy2 = (other.vy * (other.mass - self.mass) + 2 * self.mass * self.vy) / total_mass
            self.vx, self.vy = new_vx1, new_vy1
            other.vx, other.vy = new_vx2, new_vy2
            # 겹침 해소
            overlap = 0.5 * (self.radius + other.radius - distance + 1)
            self.x -= math.cos(angle) * overlap
            self.y -= math.sin(angle) * overlap
            other.x += math.cos(angle) * overlap
            other.y += math.sin(angle) * overlap

# 버튼 클래스
class Button:
    def __init__(self, x, y, w, h, text, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback

    def draw(self, surface):
        pygame.draw.rect(surface, GRAY, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        label = font.render(self.text, True, WHITE)
        surface.blit(label, (self.rect.x + 10, self.rect.y + 10))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()

# 시뮬레이션 함수 및 상태
balls = []
paused = False

def pause_sim():
    global paused
    paused = True

def resume_sim():
    global paused
    paused = False

def reset_sim():
    global balls
    balls = []

# UI 버튼 생성
buttons = [
    Button(20, 20, 100, 40, "Pause", pause_sim),
    Button(140, 20, 100, 40, "Resume", resume_sim),
    Button(260, 20, 100, 40, "Reset", reset_sim)
]

# 메인 루프
dragging_ball = None
running = True
while running:
    screen.fill((20, 20, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        for btn in buttons:
            btn.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            for ball in balls:
                if math.hypot(event.pos[0] - ball.x, event.pos[1] - ball.y) < ball.radius:
                    dragging_ball = ball
                    ball.selected = True
                    ball.initial_pos = (ball.x, ball.y)
                    break
            else:
                new_ball = Ball(event.pos[0], event.pos[1], color=random.choice([RED, GREEN, BLUE]))
                balls.append(new_ball)
                dragging_ball = new_ball
                new_ball.selected = True

        elif event.type == pygame.MOUSEBUTTONUP and dragging_ball:
            dx = event.pos[0] - dragging_ball.initial_pos[0]
            dy = event.pos[1] - dragging_ball.initial_pos[1]
            dragging_ball.vx = dx * 0.2
            dragging_ball.vy = dy * 0.2
            dragging_ball.selected = False
            dragging_ball = None

        elif event.type == pygame.MOUSEMOTION and dragging_ball:
            dragging_ball.x, dragging_ball.y = event.pos

    if not paused:
        for ball in balls:
            ball.update()
        for i in range(len(balls)):
            for j in range(i + 1, len(balls)):
                balls[i].check_collision(balls[j])

    for ball in balls:
        ball.draw(screen)

    for btn in buttons:
        btn.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
