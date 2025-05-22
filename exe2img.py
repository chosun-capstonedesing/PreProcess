import os
import numpy as np
from PIL import Image
import pandas as pd
import struct

# 경로 설정
base_path = "E:/Virus/VirusShare_00479/exe"
exe_dir = base_path
img_dir = os.path.join(base_path, "img")
csv_path = os.path.join(base_path, "data.csv")

# 디렉토리 생성
for directory in [exe_dir, img_dir]:
    os.makedirs(directory, exist_ok=True)

# HEX → IMG 변환 함수
def hex2img(array, output_img_path, img_size=256):
    raw_data = array.flatten()
    bytes_data = np.frombuffer(raw_data.tobytes(), dtype=np.uint8)
    target_length = img_size * img_size
    processed = np.zeros(target_length, dtype=np.uint8)
    length = min(len(bytes_data), target_length)
    processed[:length] = bytes_data[:length]
    image = Image.fromarray(processed.reshape(img_size, img_size)).convert('L')
    image.save(output_img_path)
    return image

# PE 헤더 제거 함수
def read_exe_file_strip_pe(exe_path):
    try:
        with open(exe_path, 'rb') as f:
            data = f.read()

        if data[:2] != b'MZ':
            print(f"  ✗ MZ 헤더 없음: {exe_path}")
            return np.array([])

        e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
        pe_offset = e_lfanew
        if data[pe_offset:pe_offset+4] != b'PE\0\0':
            print(f"  ✗ PE 헤더 없음: {exe_path}")
            return np.array([])

        # SizeOfHeaders 값 추출 (PE 헤더에서 0x54 위치)
        size_of_headers = struct.unpack_from("<I", data, pe_offset + 0x54)[0]

        # 헤더 이후의 데이터만 사용
        stripped_data = data[size_of_headers:]
        return np.frombuffer(stripped_data, dtype=np.uint8)

    except Exception as e:
        print(f"  ✗ PE 제거 실패 {exe_path}: {e}")
        return np.array([])

# 전체 파일 처리
def process_exe_files():
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print(f"기존 CSV 파일 로드됨. 총 {len(df)}개 레코드.")
    else:
        df = pd.DataFrame(columns=["img_code", "label"])
        print("새 CSV 파일 생성됨.")

    exe_files = [f for f in os.listdir(exe_dir) if f.endswith(".exe")]
    total_files = len(exe_files)
    print(f"총 {total_files}개의 .exe 파일을 처리합니다.")

    processed_count = success_count = skip_count = 0

    for filename in exe_files:
        processed_count += 1
        exe_path = os.path.join(exe_dir, filename)
        base_name = os.path.splitext(filename)[0]
        img_path = os.path.join(img_dir, f"{base_name}.png")
        relative_img_path = f"./img/{base_name}.png"

        print(f"[{processed_count}/{total_files}] 처리 중: {filename}")

        array = read_exe_file_strip_pe(exe_path)

        if array.size > 0:
            hex2img(array, img_path)
            success_count += 1
            print(f"  ✓ 이미지 저장 완료: {img_path}")

            label = 0  # 필요 시 실제 라벨 반영
            if not df[df["img_code"] == relative_img_path].empty:
                df.loc[df["img_code"] == relative_img_path, "label"] = label
            else:
                df.loc[len(df.index)] = [relative_img_path, label]
        else:
            skip_count += 1
            print(f"  ✗ 변환 실패: {filename}")

    df.to_csv(csv_path, index=False)
    print("\n처리 완료:")
    print(f"  - 총 파일 수: {processed_count}")
    print(f"  - 성공: {success_count}")
    print(f"  - 건너뜀: {skip_count}")
    print(f"  - CSV 저장 경로: {csv_path}")

# 실행
if __name__ == "__main__":
    process_exe_files()
