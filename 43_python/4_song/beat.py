import pygame
import sys
import os

# --- 초기화 ---
pygame.init()
pygame.mixer.init()

# --- 상수 정의 ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 120  # 더 부드러운 노트 움직임을 위해 FPS를 높게 설정

# 색상
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
LANE_COLORS = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100)]
JUDGEMENT_LINE_COLOR = (200, 200, 200)

# 게임 설정
LANE_COUNT = 4
LANE_WIDTH = 100
LANE_SEPARATOR_WIDTH = 10
TOTAL_LANE_WIDTH = (LANE_COUNT * LANE_WIDTH) + ((LANE_COUNT - 1) * LANE_SEPARATOR_WIDTH)
LANE_START_X = (SCREEN_WIDTH - TOTAL_LANE_WIDTH) // 2

JUDGEMENT_LINE_Y = 500
NOTE_HEIGHT = 20
NOTE_SPEED = 5  # 1프레임당 이동하는 픽셀 수

# 판정 범위 (판정선과의 거리 기준, 픽셀 단위)
PERFECT_RANGE = 20
GREAT_RANGE = 40
GOOD_RANGE = 60

# 키 매핑 (D, F, J, K)
KEY_MAPPING = {
    pygame.K_d: 0,
    pygame.K_f: 1,
    pygame.K_j: 2,
    pygame.K_k: 3
}

# --- 화면 및 시계 설정 ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame 리듬 게임")
clock = pygame.time.Clock()

# --- 애셋 로드 ---
try:
    # 폰트 로드 (D2Coding 폰트 또는 다른 ttf 폰트 파일)
    font_path = "D2Coding.ttf"
    if not os.path.exists(font_path):
        font_path = pygame.font.get_default_font() # 파일이 없으면 기본 폰트 사용

    font_small = pygame.font.Font(font_path, 24)
    font_medium = pygame.font.Font(font_path, 48)
    font_large = pygame.font.Font(font_path, 72)

except FileNotFoundError as e:
    print(f"오류: 애셋 파일({e.filename})을 찾을 수 없습니다. 게임을 종료합니다.")
    sys.exit()


# --- 비트맵 로드 함수 ---


# --- 비트맵 로드 함수 ---
def load_beatmap(filename):
    beatmap = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    time = int(parts[0])
                    lane = int(parts[1])
                    beatmap.append({'time': time, 'lane': lane, 'spawned': False})
    except FileNotFoundError:
        print(f"오류: 비트맵 파일 '{filename}'을 찾을 수 없습니다.")
        return []
    # 시간을 기준으로 정렬
    return sorted(beatmap, key=lambda x: x['time'])

# --- 노트 클래스 ---
class Note(pygame.sprite.Sprite):
    def __init__(self, lane):
        super().__init__()
        self.lane = lane

        note_width = LANE_WIDTH - 10
        self.image = pygame.Surface([note_width, NOTE_HEIGHT])
        self.image.fill(LANE_COLORS[lane])

        x_pos = LANE_START_X + lane * (LANE_WIDTH + LANE_SEPARATOR_WIDTH) + 5
        self.rect = self.image.get_rect(center=(x_pos + note_width // 2, 0))
        self.speed = NOTE_SPEED

    def update(self):
        self.rect.y += self.speed
        # 화면 밖으로 나가면 자동 삭제
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# --- 텍스트 렌더링 함수 ---
def draw_text(text, font, color, surface, x, y, center=True):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)

# --- 게임 상태 ---
class GameState:
    START = 0
    PLAYING = 1
    RESULT = 2

# --- 메인 게임 루프 ---
def game_loop(song_file, beatmap_file):
    game_state = GameState.START

    # 게임 변수
    score = 0
    combo = 0
    max_combo = 0
    judgements = {"Perfect": 0, "Great": 0, "Good": 0, "Miss": 0}

    # 판정 텍스트 관련
    judgement_text = ""
    judgement_timer = 0

    # 비트맵 및 노트 관리
    beatmap = load_beatmap(beatmap_file)
    if not beatmap:
        return # 비트맵 로드 실패 시 종료

    all_sprites = pygame.sprite.Group()
    notes_in_lanes = [[] for _ in range(LANE_COUNT)]

    # 노트가 판정선까지 도달하는 데 걸리는 시간 (ms)
    time_to_reach_judgement_line = (JUDGEMENT_LINE_Y / NOTE_SPEED) * (1000 / FPS)

    music_started = False
    start_time = 0



    # --- 게임 루프 ---
    running = True
    while running:
        # --- 이벤트 처리 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == GameState.START:
                if event.type == pygame.KEYDOWN:
                    game_state = GameState.PLAYING
                    music_started = True
                    pygame.mixer.music.load(song_file)
                    pygame.mixer.music.play()
                    start_time = pygame.time.get_ticks()

            elif game_state == GameState.PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key in KEY_MAPPING:
                        lane_idx = KEY_MAPPING[event.key]
                        hit = False
                        # 해당 레인의 가장 가까운 노트를 찾음
                        if notes_in_lanes[lane_idx]:
                            note = notes_in_lanes[lane_idx][0]
                            distance = abs(note.rect.centery - JUDGEMENT_LINE_Y)

                            if distance <= PERFECT_RANGE:
                                judgement_text = "Perfect"
                                score += 300
                                combo += 1
                                judgements["Perfect"] += 1
                                hit = True
                            elif distance <= GREAT_RANGE:
                                judgement_text = "Great"
                                score += 200
                                combo += 1
                                judgements["Great"] += 1
                                hit = True
                            elif distance <= GOOD_RANGE:
                                judgement_text = "Good"
                                score += 100
                                combo += 1
                                judgements["Good"] += 1
                                hit = True

                            if hit:
                                judgement_timer = FPS // 2 # 0.5초간 표시
                                note.kill()
                                notes_in_lanes[lane_idx].pop(0)

            elif game_state == GameState.RESULT:
                if event.type == pygame.KEYDOWN:
                    game_loop() # 게임 재시작
                    return


        # --- 게임 로직 업데이트 ---
        if game_state == GameState.PLAYING:
            current_time = pygame.time.get_ticks() - start_time

            # 노트 생성
            for note_data in beatmap:
                if not note_data['spawned'] and current_time >= note_data['time'] - time_to_reach_judgement_line:
                    note = Note(note_data['lane'])
                    all_sprites.add(note)
                    notes_in_lanes[note_data['lane']].append(note)
                    note_data['spawned'] = True

            # 노트 이동
            all_sprites.update()

            # Miss 판정
            for i in range(LANE_COUNT):
                # 리스트를 복사해서 순회 (삭제 중 에러 방지)
                for note in list(notes_in_lanes[i]):
                    if note.rect.top > JUDGEMENT_LINE_Y + GOOD_RANGE:
                        judgement_text = "Miss"
                        judgement_timer = FPS // 2
                        judgements["Miss"] += 1
                        combo = 0
                        note.kill()
                        notes_in_lanes[i].remove(note)

            # 콤보 업데이트
            if combo > max_combo:
                max_combo = combo

            # 판정 텍스트 타이머 감소
            if judgement_timer > 0:
                judgement_timer -= 1

            # 게임 종료 조건 (음악이 끝나고 모든 노트가 사라졌을 때)
            if not pygame.mixer.music.get_busy() and len(all_sprites) == 0:
                 game_state = GameState.RESULT


        # --- 화면 그리기 ---
        screen.fill(BLACK)

        if game_state == GameState.START:
            draw_text("Pygame 리듬 게임", font_large, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
            draw_text("사용할 키: D, F, J, K", font_medium, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            draw_text("아무 키나 눌러 시작하세요", font_small, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3)

        elif game_state == GameState.PLAYING or game_state == GameState.RESULT:
            # 레인 그리기
            for i in range(LANE_COUNT):
                x = LANE_START_X + i * (LANE_WIDTH + LANE_SEPARATOR_WIDTH)
                pygame.draw.rect(screen, GRAY, (x, 0, LANE_WIDTH, SCREEN_HEIGHT))

            # 판정선 그리기
            pygame.draw.line(screen, JUDGEMENT_LINE_COLOR, (LANE_START_X, JUDGEMENT_LINE_Y),
                             (LANE_START_X + TOTAL_LANE_WIDTH, JUDGEMENT_LINE_Y), 5)

            # 노트 그리기
            all_sprites.draw(screen)

            # UI 텍스트 그리기
            draw_text(f"점수: {score}", font_small, WHITE, screen, 80, 30)

            if combo > 1:
                draw_text(f"{combo} 콤보!", font_medium, WHITE, screen, SCREEN_WIDTH // 2, 150)

            if judgement_timer > 0:
                draw_text(judgement_text, font_medium, LANE_COLORS[3], screen, SCREEN_WIDTH // 2, 250)

        if game_state == GameState.RESULT:
            # 반투명 배경
            result_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            result_bg.fill((0, 0, 0, 180))
            screen.blit(result_bg, (0, 0))

            draw_text("결과", font_large, WHITE, screen, SCREEN_WIDTH // 2, 80)
            draw_text(f"총점: {score}", font_medium, WHITE, screen, SCREEN_WIDTH // 2, 180)
            draw_text(f"최대 콤보: {max_combo}", font_medium, WHITE, screen, SCREEN_WIDTH // 2, 240)

            y_offset = 320
            for j, count in judgements.items():
                draw_text(f"{j}: {count}", font_small, WHITE, screen, SCREEN_WIDTH // 2, y_offset)
                y_offset += 40

            draw_text("아무 키나 눌러 다시 시작", font_small, WHITE, screen, SCREEN_WIDTH // 2, 550)


        # --- 화면 업데이트 ---
        pygame.display.flip()
        clock.tick(FPS)

    # --- 종료 ---
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("사용법: python beat.py <음악_파일.mp3> <비트맵_파일.txt>")
        sys.exit(1)
    
    song_file = os.path.abspath(sys.argv[1])
    beatmap_file = os.path.abspath(sys.argv[2])
    game_loop(song_file, beatmap_file)
