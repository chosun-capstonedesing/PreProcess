import os
import numpy as np
from PIL import Image
from tqdm import tqdm

# 한글 바이트 파일을 256x256 이미지로 변환하는 함수
def hwp_to_image(hwp_file_path, output_image_path, width=256, height=256, normalize=True):
    """
    한글 바이트 파일을 256x256 그레이스케일 이미지로 변환합니다.
    
    Args:
        hwp_file_path (str): 한글 파일 경로
        output_image_path (str): 출력 이미지 경로
        width (int): 이미지의 너비
        height (int): 이미지의 높이
        normalize (bool): 바이트 값을 0-255 범위로 정규화할지 여부
    """
    # 한글 파일을 바이너리 모드로 읽기
    with open(hwp_file_path, 'rb') as f:
        byte_content = f.read()
    
    # 바이트 배열을 numpy 배열로 변환
    byte_array = np.frombuffer(byte_content, dtype=np.uint8)
    
    # 정규화 (선택 사항)
    if normalize:
        byte_array = byte_array.astype(np.float32)
        if byte_array.max() > 0:  # 0으로 나누기 방지
            byte_array = (byte_array / byte_array.max() * 255).astype(np.uint8)
    
    # 고정된 크기로 배열 준비 (256x256)
    required_size = width * height
    
    if len(byte_array) >= required_size:
        # 필요한 만큼만 사용
        padded_array = byte_array[:required_size]
    else:
        # 반복하여 필요한 크기 만들기
        repeat_count = (required_size // len(byte_array)) + 1
        padded_array = np.tile(byte_array, repeat_count)[:required_size]
    
    # 2D 배열로 재구성 (256x256)
    image_array = padded_array.reshape((height, width))
    
    # PIL 이미지로 변환 및 저장
    image = Image.fromarray(image_array, mode='L')  # 'L'은 그레이스케일 모드
    image.save(output_image_path)
    
    return image

# 메인 함수: 한글 파일을 이미지로 변환
def process_hwp_files(input_dir, output_dir, width=256, height=256):
    """
    디렉토리 내의 모든 한글 파일을 처리하여 256x256 이미지로 변환합니다.
    
    Args:
        input_dir (str): 입력 한글 파일 디렉토리
        output_dir (str): 출력 이미지 디렉토리
        width (int): 이미지 너비 (256으로 고정)
        height (int): 이미지 높이 (256으로 고정)
    """
    # 입력 디렉토리 구조 확인 (정상/악성 폴더 구조 가정)
    class_dirs = [d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]
    
    if not class_dirs:
        print(f"경고: {input_dir}에 서브디렉토리가 없습니다.")
        # 단일 디렉토리 처리 (클래스 분류가 없는 경우)
        class_dirs = ['']
    
    for class_dir in class_dirs:
        # 클래스별 입력 디렉토리 경로
        if class_dir:
            class_input_dir = os.path.join(input_dir, class_dir)
            # 클래스별 출력 디렉토리 생성
            class_output_dir = os.path.join(output_dir, class_dir)
        else:
            class_input_dir = input_dir
            class_output_dir = output_dir
        
        os.makedirs(class_output_dir, exist_ok=True)
        
        # 한글 파일 목록 (hwp, hwpx 확장자)
        hwp_files = [f for f in os.listdir(class_input_dir) 
                    if os.path.isfile(os.path.join(class_input_dir, f)) and 
                    (f.lower().endswith('.hwp') or f.lower().endswith('.hwpx') or 
                     f.lower().endswith('.bin') or f.lower().endswith('.dat'))]
        
        if not hwp_files:
            print(f"경고: {class_input_dir}에 처리할 파일이 없습니다.")
            continue
        
        print(f"{class_dir if class_dir else '기본'} 클래스의 {len(hwp_files)}개 파일 처리 중...")
        
        # 각 한글 파일 처리
        for hwp_file in tqdm(hwp_files):
            hwp_file_path = os.path.join(class_input_dir, hwp_file)
            base_filename = os.path.splitext(hwp_file)[0]
            
            # 이미지 저장 경로
            image_output_path = os.path.join(class_output_dir, f"{base_filename}.png")
            
            try:
                # 한글 파일을 256x256 이미지로 변환
                hwp_to_image(hwp_file_path, image_output_path, width, height)
                print(f"변환 완료: {hwp_file} → {image_output_path}")
                    
            except Exception as e:
                print(f"파일 {hwp_file} 처리 중 오류 발생: {e}")
                continue
    
    print("모든 파일 처리 완료!")
    return True

# 사용 예시
if __name__ == "__main__":
    # 경로 설정
    input_dir = "/path/to/hwp_files"  # 한글 파일이 있는 경로 (정상/악성 폴더 구조)
    output_dir = "/path/to/output_images"  # 이미지를 저장할 경로
    
    # 한글 파일을 256x256 이미지로 변환
    process_hwp_files(
        input_dir, 
        output_dir, 
        width=256, 
        height=256
    )
    
    print("프로그램 실행 완료!")