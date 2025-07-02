import pygame
import numpy as np
import time

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1)

WIDTH, HEIGHT = 800, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Piano (No WAV)")

font = pygame.font.SysFont(None, 32)

# 키보드 키 -> 음 이름 -> 주파수(Hz)
key_to_freq = {
    pygame.K_a: ("C", 261.63),
    pygame.K_s: ("D", 293.66),
    pygame.K_d: ("E", 329.63),
    pygame.K_f: ("F", 349.23),
    pygame.K_g: ("G", 392.00),
    pygame.K_h: ("A", 440.00),
    pygame.K_j: ("B", 493.88),
    pygame.K_k: ("C2", 523.25),
}

generated_sounds = {}

recording = False
recorded_notes = []
record_start_time = 0

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
RED = (255, 100, 100)

def generate_sound(frequency, duration=0.5, volume=0.5, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = np.sin(2 * np.pi * frequency * t)
    audio = (wave * volume * (2**15 - 1)).astype(np.int16)

    # mixer가 스테레오로 설정되어 있을 수 있으니, 2D 배열로 변환
    if pygame.mixer.get_init()[2] == 2:  # stereo
        audio = np.column_stack((audio, audio))  # duplicate mono to stereo

    return pygame.sndarray.make_sound(audio)

def play_note(key_code):
    if key_code not in generated_sounds:
        _, freq = key_to_freq[key_code]
        generated_sounds[key_code] = generate_sound(freq)
    generated_sounds[key_code].play()

def draw_piano():
    screen.fill(GRAY)
    keys = list(key_to_freq.keys())
    key_width = WIDTH // len(keys)

    for i, k in enumerate(keys):
        rect = pygame.Rect(i * key_width, 100, key_width - 2, 150)
        pygame.draw.rect(screen, WHITE, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)
        label = font.render(pygame.key.name(k), True, BLACK)
        screen.blit(label, (rect.x + 10, rect.y + 10))

    status = "Recording..." if recording else "Press R to Record | P to Play"
    msg = font.render(status, True, RED if recording else BLACK)
    screen.blit(msg, (20, 20))

def play_recorded():
    if not recorded_notes:
        print("녹음된 음이 없습니다.")
        return
    for i, (key, timestamp) in enumerate(recorded_notes):
        if i > 0:
            delay = timestamp - recorded_notes[i-1][1]
            time.sleep(delay)
        play_note(key)

# 메인 루프
running = True
while running:
    draw_piano()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                if not recording:
                    recorded_notes = []
                    record_start_time = time.time()
                    recording = True
                    print("🎙️ 녹음 시작")
                else:
                    recording = False
                    print("🛑 녹음 종료")
            elif event.key == pygame.K_p:
                print("▶️ 재생 시작")
                play_recorded()
            elif event.key in key_to_freq:
                play_note(event.key)
                if recording:
                    timestamp = time.time() - record_start_time
                    recorded_notes.append((event.key, timestamp))

pygame.quit()
