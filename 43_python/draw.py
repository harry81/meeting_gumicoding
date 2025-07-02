import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("간단한 드로잉 보드")
drawing = False
last_pos = None
color = (255, 255, 255)  # 흰색

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            drawing = True
            last_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            drawing = False
        elif event.type == pygame.MOUSEMOTION and drawing:
            pygame.draw.line(screen, color, last_pos, event.pos, 5)
            last_pos = event.pos
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # R 키로 빨간색
                color = (255, 0, 0)
            elif event.key == pygame.K_b:  # B 키로 파란색
                color = (0, 0, 255)

    pygame.display.flip()

pygame.quit()
