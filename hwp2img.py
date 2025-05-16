import os
import numpy as np
from PIL import Image
import imgaug.augmenters as iaa

def load_image(img_path):
    return np.array(Image.open(img_path))

def save_image(img_array, output_path):
    img = Image.fromarray(img_array)
    img.save(output_path)

def augment_85_images(img_path, output_dir, num_aug=85):
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(img_path))[0]
    image = load_image(img_path)

    seq = iaa.Sequential([
        iaa.SomeOf((1, 3), [  # 무작위로 1~3개 조합
            iaa.Affine(rotate=(-45, 45)),
            iaa.Affine(scale=(0.8, 1.2)),
            iaa.Flipud(0.5),
            iaa.Fliplr(0.5),
            iaa.AdditiveGaussianNoise(scale=(5, 20)),
            iaa.GaussianBlur(sigma=(0.0, 1.5)),
            iaa.LinearContrast((0.75, 1.5)),
            iaa.Multiply((0.8, 1.2)),
            iaa.Add((-10, 10), per_channel=0.5),
            iaa.ElasticTransformation(alpha=50, sigma=5),
            iaa.PiecewiseAffine(scale=(0.01, 0.05)),
            iaa.PerspectiveTransform(scale=(0.01, 0.1))
        ])
    ])

    images_aug = seq(images=[image for _ in range(num_aug)])

    for i, aug_img in enumerate(images_aug):
        save_path = os.path.join(output_dir, f"{base_name}_aug{i+1:03}.png")
        save_image(aug_img, save_path)

def augment_all_images_in_folder(input_folder, output_root_folder):
    os.makedirs(output_root_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            img_path = os.path.join(input_folder, filename)
            base_name = os.path.splitext(filename)[0]
            output_subfolder = os.path.join(output_root_folder, base_name)
            print(f"[+] 증강 중: {filename} → {output_subfolder}")
            augment_85_images(img_path, output_subfolder)

# 실제 경로 설정
input_folder = "/home/wonjun/hwp/Benign_img"
output_folder = "/home/wonjun/hwp/Benign_aug"

augment_all_images_in_folder(input_folder, output_folder)
