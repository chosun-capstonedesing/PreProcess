import os
import numpy as np
from PIL import Image

def xlsx_to_binary_image(file_path, output_path, image_size=(256, 256)):
    with open(file_path, 'rb') as f:
        byte_data = f.read()

    byte_array = np.frombuffer(byte_data, dtype=np.uint8)
    total_len = len(byte_array)
    square_size = int(np.ceil(np.sqrt(total_len)))
    padded = np.pad(byte_array, (0, square_size**2 - total_len), mode='constant')
    img_array = padded.reshape((square_size, square_size))

    img = Image.fromarray(img_array).resize(image_size)
    img.save(output_path)
    print(f"[+] 변환 완료: {output_path}")

def convert_all_xlsx_to_images(input_folder, output_folder, image_size=(256, 256)):
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.xlsx'):
            file_path = os.path.join(input_folder, filename)
            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(output_folder, f"{base_name}.png")
            try:
                xlsx_to_binary_image(file_path, output_path, image_size=image_size)
            except Exception as e:
                print(f"[-] 오류 발생: {filename} → {e}")

# === 실행 ===
xlsx_input_folder = "/home/wonjun/xls/xlsx_dataset/Malware"               # 🔁 여기에 xlsx 파일 경로 입력
output_image_folder = "/home/wonjun/xls/xlsx_dataset/Malware_img"       # 🔁 이미지 저장 경로

convert_all_xlsx_to_images(xlsx_input_folder, output_image_folder)
