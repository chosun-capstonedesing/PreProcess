import os
import numpy as np
from PIL import Image

def docx_to_binary_image(docx_path, output_path, image_size=(256, 256)):
    with open(docx_path, 'rb') as f:
        byte_data = f.read()

    byte_array = np.frombuffer(byte_data, dtype=np.uint8)
    total_len = len(byte_array)
    square_size = int(np.ceil(np.sqrt(total_len)))
    padded = np.pad(byte_array, (0, square_size**2 - total_len), mode='constant')
    img_array = padded.reshape((square_size, square_size))

    img = Image.fromarray(img_array).resize(image_size)
    img.save(output_path)
    print(f"[+] 변환 완료: {output_path}")

def convert_all_docx_in_folder(input_folder, output_folder, image_size=(256, 256)):
    os.makedirs(output_folder, exist_ok=True)
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".docx"):
            input_path = os.path.join(input_folder, filename)
            output_name = f"{os.path.splitext(filename)[0]}.png"
            output_path = os.path.join(output_folder, output_name)
            try:
                docx_to_binary_image(input_path, output_path, image_size=image_size)
            except Exception as e:
                print(f"[-] 변환 실패: {filename} → {e}")
    print("[✅] 모든 docx 이미지 변환 완료")

# === 실행 ===
input_docx_folder = r"/home/wonjun/docx/docx/Malware"  # ⚠ 사용자이름 부분 수정
output_image_folder = r"/home/wonjun/docx/docx/Malware_img"

convert_all_docx_in_folder(input_docx_folder, output_image_folder)
