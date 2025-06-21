import os
import shutil
import random

# Dizinleri ayarla
base_dir = r"C:\Users\omerp\Masaüstü\verihazirla\dataset"
images_dir = os.path.join(base_dir, "images")
labels_dir = os.path.join(base_dir, "labels")

# Hedef klasörler (varsa temizle, yoksa oluştur)
for split in ["train", "val"]:
    os.makedirs(os.path.join(base_dir, "images", split), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "labels", split), exist_ok=True)

# Görsel dosya isimlerini al
image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
random.shuffle(image_files)  # Karıştır

# Oranları belirle
val_ratio = 0.2
val_count = int(len(image_files) * val_ratio)

val_files = image_files[:val_count]
train_files = image_files[val_count:]

def copy_files(file_list, split):
    for img_name in file_list:
        img_src = os.path.join(images_dir, img_name)
        label_name = os.path.splitext(img_name)[0] + ".txt"
        label_src = os.path.join(labels_dir, label_name)

        img_dst = os.path.join(base_dir, "images", split, img_name)
        label_dst = os.path.join(base_dir, "labels", split, label_name)

        # Dosyalar varsa kopyala (etiket olmayan görseli atla)
        if os.path.exists(label_src):
            shutil.copyfile(img_src, img_dst)
            shutil.copyfile(label_src, label_dst)

copy_files(train_files, "train")
copy_files(val_files, "val")

print("Dataset YOLO formatına uygun şekilde hazırlandı!")
