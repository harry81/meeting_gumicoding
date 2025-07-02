import librosa
import numpy as np
import argparse
import random
import os

def create_beatmap(mp3_path, output_path, density=0.7, chord_chance=0.15):
    """
    MP3 파일에서 비트를 분석하여 리듬 게임용 beatmap.txt 파일을 생성합니다.

    :param mp3_path: 분석할 MP3 파일 경로
    :param output_path: 생성될 beatmap.txt 파일 경로
    :param density: 노트 생성 밀도 (0.1 ~ 1.0). 값이 클수록 노트가 많아집니다.
    :param chord_chance: 동시치기(코드)가 발생할 확률 (0.0 ~ 1.0)
    """
    if not os.path.exists(mp3_path):
        print(f"오류: 파일 '{mp3_path}'를 찾을 수 없습니다.")
        return

    print(f"'{mp3_path}' 파일을 분석 중입니다. 잠시만 기다려주세요...")

    try:
        # 1. 오디오 파일 로드
        y, sr = librosa.load(mp3_path)

        # 2. 온셋(소리 시작점) 감지
        #    - librosa.onset.onset_detect는 온셋 이벤트의 프레임 인덱스를 반환합니다.
        #    - backtrack=True를 사용하여 실제 피크에 더 가깝게 위치를 조정합니다.
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr, units='frames', backtrack=True)

        # 프레임을 시간(초)으로 변환
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)

        print(f"총 {len(onset_times)}개의 잠재적 노트 지점을 감지했습니다.")

        # 3. 노트 생성 및 레인 할당
        notes = []
        last_lane = -1

        for t in onset_times:
            # 밀도(density) 설정에 따라 노트를 생성할지 결정
            if random.random() > density:
                continue

            # 시간을 밀리초(ms)로 변환
            time_ms = int(t * 1000)

            # 4. 레인 할당 로직
            # 이전 레인과 겹치지 않도록 간단한 로직 추가
            available_lanes = [0, 1, 2, 3]
            if last_lane != -1 and len(available_lanes) > 1:
                # available_lanes.remove(last_lane) # 바로 옆에 같은 노트가 나오는 것을 방지하려면 주석 해제
                pass

            lane = random.choice(available_lanes)
            notes.append((time_ms, lane))
            last_lane = lane

            # 5. 동시치기(코드) 생성 로직
            if random.random() < chord_chance:
                chord_lanes = [0, 1, 2, 3]
                chord_lanes.remove(lane) # 이미 할당된 레인은 제외
                chord_lane = random.choice(chord_lanes)
                notes.append((time_ms, chord_lane))

        # 시간순으로 정렬
        notes.sort()

        # 6. 파일로 저장
        with open(output_path, 'w') as f:
            f.write(f"# Beatmap generated from '{os.path.basename(mp3_path)}'\n")
            f.write(f"# Total notes: {len(notes)}\n")
            for time_ms, lane in notes:
                f.write(f"{time_ms},{lane}\n")

        print(f"성공! '{output_path}' 파일에 {len(notes)}개의 노트가 포함된 비트맵을 생성했습니다.")
        print(f"팁: 생성된 비트맵이 너무 어렵거나 쉬우면 --density 와 --chord-chance 옵션을 조절해보세요.")

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        print("librosa 또는 ffmpeg 설치에 문제가 없는지 확인해주세요.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="MP3 파일에서 리듬 게임용 beatmap.txt를 자동으로 생성합니다.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("mp3_file", help="분석할 MP3 파일의 경로")

    parser.add_argument(
        "-o", "--output",
        default="beatmap.txt",
        help="출력할 비트맵 파일 이름 (기본값: beatmap.txt)"
    )

    parser.add_argument(
        "-d", "--density",
        type=float,
        default=0.7,
        help="노트 생성 밀도 (0.1 ~ 1.0, 기본값: 0.7)\n"
             "값이 높을수록 더 많은 노트가 생성됩니다."
    )

    parser.add_argument(
        "-c", "--chord-chance",
        type=float,
        default=0.15,
        help="동시치기(코드)가 발생할 확률 (0.0 ~ 1.0, 기본값: 0.15)\n"
             "값이 높을수록 코드가 더 자주 나옵니다."
    )

    args = parser.parse_args()

    create_beatmap(args.mp3_file, args.output, args.density, args.chord_chance)
