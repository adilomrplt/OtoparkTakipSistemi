# YOLOv8 ile Otopark Doluluk Tespiti

Bu projede, otopark alanlarının **boş** veya **dolu** olup olmadığını otomatik tespit eden bir sistem geliştirilmiştir. Eğitim işlemi YOLOv8 kullanılarak yapılmıştır.

## 📁 Klasör Yapısı

- `weights/`: Eğitilmiş en iyi model dosyası (`best.pt`)
- `metrics/`: Eğitim sonrası oluşan performans grafikleri ve karşılaştırmalar
- `inference_batches/`: Eğitim ve doğrulama sürecinde modelin tahmin örnekleri
- `logs/`: Eğitim sırasında oluşan CSV, YAML ve diğer log dosyaları

## ⚙️ Eğitim Ayarları

- Model: `yolov8n.pt`
- Epoch: 50
- Görsel Boyutu: 640x640
- Batch Size: 16
- mAP50: **%99.5**
- Kullanılan GPU: RTX 3050 Ti

## 🎯 Genel Not

Model oldukça başarılı bir şekilde otopark doluluk durumunu ayırt edebilmektedir. Eğitim sürecinde verilerin dengesi korunmuş ve analizler yapılmıştır.
