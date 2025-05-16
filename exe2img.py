import os
import numpy as np
from PIL import Image
from math import log
import pandas as pd
import re

# 경로 설정
base_path = "/home/user/malware/Malware/bytes"
bytes_dir = base_path  # 변환된 .bytes 파일 저장 디렉토리
img_dir = os.path.join(base_path, "img")  # 이미지 저장 디렉토리
csv_path = os.path.join(base_path, "data.csv")  # CSV 파일 경로

# 디렉토리 생성 (존재하지 않는 경우)
for directory in [bytes_dir, img_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# 메모리 주소가 제거된 바이트 파일에서 바이트 데이터 추출
def extract_bytes_from_text(text):
    """
    PE 헤더가 제거된 악성 PE 바이트 파일에서 메모리 주소를 제거하고
    실제 바이트 데이터만 추출합니다.
    """
    # 각 줄에서 메모리 주소 부분을 제거하고 바이트 데이터만 추출
    byte_lines = []
    for line in text.strip().split('\n'):
        # 메모리 주소 부분(앞 8자리 + 공백)을 제거
        if len(line) > 9 and re.match(r'[0-9A-Fa-f]{8}\s', line[:9]):
            # 메모리 주소 이후의 바이트 데이터만 추출
            bytes_part = line[9:].strip()
            byte_lines.append(bytes_part)
    
    # 모든 바이트 문자열을 하나로 합침
    all_bytes = ' '.join(byte_lines)
    
    # 공백으로 분리된 16진수 바이트 값을 추출
    byte_values = all_bytes.split()
    
    # 16진수 문자열을 정수로 변환 (??는 0으로 처리)
    int_values = []
    for byte_val in byte_values:
        if byte_val == '??':
            int_values.append(0)
        else:
            try:
                int_values.append(int(byte_val, 16))
            except ValueError:
                int_values.append(0)  # 변환할 수 없는 값은 0으로 처리
    
    # NumPy 배열로 변환
    return np.array(int_values, dtype=np.uint8)

# HEX → IMG 변환
def hex2img(array, output_img_path, img_size=256):
    # 배열을 1차원으로 변환 후 Numpy 배열로 변환(부호없는 8비트 정수)
    raw_data = array.flatten() 
    bytes_data = np.frombuffer(raw_data.tobytes(), dtype=np.uint8)
    
    # 목표 이미지 사이즈 256 * 256,  
    target_length = img_size * img_size
    processed = np.zeros(target_length, dtype=np.uint8) #  목표 크기와 같은 크기 새 배열 생성
    length = min(len(bytes_data), target_length) # 두 배열 중 작은 길이 선택
    processed[:length] = bytes_data[:length]
    
    # 이미지 생성 및 저장
    image = Image.fromarray(processed.reshape(img_size, img_size)).convert('L')
    image.save(output_img_path)
    return image

# .bytes 파일을 행렬로 읽기
def read_bytes_file(bytes_path):
    """
    .bytes 파일을 읽어서 2D 배열로 변환합니다.
    """
    array = []
    line_count = 0
    valid_line_count = 0
    
    try:
        with open(bytes_path, 'r') as f:
            for line in f:
                line_count += 1
                # 줄바꿈 제거하고 공백으로 분리
                parts = line.replace("\n", "").split(" ")
                
                # 첫 번째 부분은 메모리 주소이므로 제외
                if len(parts) > 1:
                    hex_values = parts[1:]
                    
                    # 16개의 값이 아니거나 빈 문자열이 있으면 건너뜀
                    if len(hex_values) != 16 or "" in hex_values:
                        continue
                    
                    # 16진수 값을 정수로 변환 (?? 값은 0으로 처리)
                    row = []
                    for val in hex_values:
                        if val == '??':
                            row.append(0)
                        else:
                            try:
                                row.append(int(val, 16))
                            except ValueError:
                                row.append(0)
                    
                    array.append(row)
                    valid_line_count += 1
        
        result_array = np.array(array, dtype=np.uint8)
        print(f"  - 파일 읽기 완료: 총 {line_count}줄, 유효한 데이터 {valid_line_count}줄")
        print(f"  - 배열 크기: {result_array.shape if result_array.size > 0 else '빈 배열'}")
        return result_array
    except Exception as e:
        print(f"  ✗ 파일 읽기 오류 {bytes_path}: {e}")
        return np.array([])

# 여러 파일 처리
def process_files():
    # CSV 초기화 또는 로드
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print(f"기존 CSV 파일을 로드했습니다. 총 {len(df)} 개의 레코드가 있습니다.")
    else:
        df = pd.DataFrame(columns=["img_code", "label"])
        print("새로운 CSV 파일을 생성합니다.")

    # 파일 총 개수 계산
    total_files = sum(1 for f in os.listdir(bytes_dir) if f.endswith(".bytes"))
    print(f"총 {total_files}개의 .bytes 파일을 처리합니다.")
    
    # 진행 상황 추적을 위한 카운터
    processed_count = 0
    success_count = 0
    skip_count = 0

    # bytes 디렉토리에서 .bytes 파일 탐색
    for filename in os.listdir(bytes_dir):
        if filename.endswith(".bytes"):
            processed_count += 1
            bytes_path = os.path.join(bytes_dir, filename)
            base_name = os.path.splitext(filename)[0]  # 확장자 제외 파일명
            img_path = os.path.join(img_dir, f"{base_name}.png")
            relative_img_path = f"./img/{base_name}.png"

            print(f"[{processed_count}/{total_files}] 처리 중: {filename}")
            
            # .bytes 파일을 이미지로 변환
            array = read_bytes_file(bytes_path)

            if array.size > 0:  # 데이터가 있을 경우에만 이미지 생성
                hex2img(array, img_path)
                success_count += 1
                print(f"  ✓ 이미지 변환 성공: {img_path}")

                # CSV에 기록
                label = 0  # benign/malware 구분 없이 임시로 0
                if not df[df["img_code"] == relative_img_path].empty:
                    # 이미 존재하는 항목 업데이트
                    df.loc[df["img_code"] == relative_img_path, "label"] = label
                    print(f"  ✓ CSV 레코드 업데이트: {relative_img_path}")
                else:
                    # 새 항목 추가
                    df.loc[len(df.index)] = [relative_img_path, label]
                    print(f"  ✓ CSV 새 레코드 추가: {relative_img_path}")
            else:
                skip_count += 1
                print(f"  ✗ 건너뜀 {filename}: 유효한 데이터가 없습니다.")

    # CSV 저장
    df.to_csv(csv_path, index=False)
    print(f"\n처리 완료:")
    print(f"  - 총 처리 파일: {processed_count}/{total_files}")
    print(f"  - 성공: {success_count}개")
    print(f"  - 건너뜀: {skip_count}개")
    print(f"  - CSV 저장 경로: {csv_path}")

# 파일에서 직접 바이트 추출 및 이미지 변환
def process_text_to_image(input_text_path, output_img_path, img_size=256):
    """
    메모리 주소가 포함된 바이트 텍스트 파일을 직접 이미지로 변환합니다.
    """
    try:
        # 텍스트 파일 읽기
        with open(input_text_path, 'r') as f:
            text_content = f.read()
        
        # 바이트 데이터 추출
        byte_array = extract_bytes_from_text(text_content)
        
        # 이미지로 변환
        if byte_array.size > 0:
            hex2img(byte_array, output_img_path, img_size)
            print(f"이미지가 '{output_img_path}'에 저장되었습니다.")
            return True
        else:
            print("추출된 바이트 데이터가 없습니다.")
            return False
    except Exception as e:
        print(f"이미지 변환 중 오류 발생: {e}")
        return False

# 실행
if __name__ == "__main__":
    # 디렉토리 내 모든 .bytes 파일 처리
    process_files()
    
    # 또는 단일 파일을 직접 처리할 경우
    # process_text_to_image("example.txt", "example.png")