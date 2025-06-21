import os
import shutil
import random

# Kendi yoluna göre kaynak klasörler
base_dir = "C:/parking_dataset_yolo"
images_src = os.path.join(base_dir, "images")
labels_src = os.path.join(base_dir, "labels")

# YOLOv8 için hedef klasörler
yolo_base = os.path.join(base_dir, "yolo_dataset")
images_train = os.path.join(yolo_base, "images", "train")
images_val = os.path.join(yolo_base, "images", "val")
labels_train = os.path.join(yolo_base, "labels", "train")
labels_val = os.path.join(yolo_base, "labels", "val")

# Klasörleri oluştur
for folder in [images_train, images_val, labels_train, labels_val]:
    os.makedirs(folder, exist_ok=True)

# Tüm görselleri al (.jpg, .jpeg, .png)
image_files = [f for f in os.listdir(images_src) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
random.shuffle(image_files)

# %80 train / %20 val ayır
split_index = int(len(image_files) * 0.8)
train_files = image_files[:split_index]
val_files = image_files[split_index:]

def copy_pair(file_list, img_dst, lbl_dst):
    for img_file in file_list:
        base = os.path.splitext(img_file)[0]
        label_file = base + ".txt"

        img_path = os.path.join(images_src, img_file)
        lbl_path = os.path.join(labels_src, label_file)

        if os.path.exists(lbl_path):
            shutil.copy(img_path, os.path.join(img_dst, img_file))
            shutil.copy(lbl_path, os.path.join(lbl_dst, label_file))

# Kopyala
copy_pair(train_files, images_train, labels_train)
copy_pair(val_files, images_val, labels_val)

print(f"Toplam görsel: {len(image_files)}")
print(f"Eğitim: {len(train_files)} → {images_train}")
print(f"Doğrulama: {len(val_files)} → {images_val}")
