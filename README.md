# Akıllı Otopark Takip Sistemi

Bu proje, otoparklardaki park alanlarının dolu/boş durumunu gerçek zamanlı olarak tespit eden bir sistemdir. YOLOv8 tabanlı derin öğrenme modeliyle, park alanlarının koordinatları önceden tanımlanır ve her bir slotun dolu mu boş mu olduğu doğrudan sınıflandırılır. Kullanıcı dostu bir arayüz ile (PyQt5) video veya canlı görüntü üzerinden analiz yapılabilir.

---

## Özellikler

- Gerçek zamanlı park yeri doluluk tespiti
- PyQt5 tabanlı masaüstü arayüz
- YOLOv8 tabanlı derin öğrenme modeli
- Çoklu kamera ve konfigürasyon desteği
- Doluluk oranı ve istatistiksel analiz

---

## Kullanılan Teknolojiler

- Python 3.8+
- YOLOv8 (ultralytics)
- PyTorch
- OpenCV
- PyQt5
- Numpy, Pandas, Matplotlib, Seaborn, scikit-learn
- CUDA (isteğe bağlı, GPU hızlandırma için)

---

## Klasör Yapısı

```
OtoparkTakipSistemi/
├── main_gui.py
├── model_training_v1.ipynb
├── model_training_v2.ipynb
├── models/
│   ├── v1_model/
│   └── v2_model/
├── yolo_results/
│   ├── yolo_parking_v1/
│   └── yolo_parking_v2/
├── config/
├── dataset/
├── videos/
├── img/
├── utils/
└── requirements.txt
```

---

## Kurulum

### Gereksinimler

- Python 3.8 veya üzeri
- Git LFS (Large File Storage)

### Adımlar

1. Repository'yi klonlayın:
   ```bash
   git clone https://github.com/adilomrplt/OtoparkTakipSistemi.git
   cd OtoparkTakipSistemi
   ```

2. Git LFS'i etkinleştirin:
   ```bash
   git lfs install
   ```

3. Python sanal ortamı oluşturun ve aktif edin:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

4. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

---

## Kullanım

Ana arayüzü başlatmak için:
```bash
python main_gui.py
```

Model eğitimi için Jupyter notebook dosyalarını kullanabilirsiniz:
- model_training_v1.ipynb
- model_training_v2.ipynb

---

## Önemli Notlar

- `dataset` altındaki `images` ve `labels` klasörleri .gitignore ile hariç tutulmuştur (büyük boyut nedeniyle)(çalışmak isterseniz bana ulaşabilirsiniz).
- Model ağırlıkları ve eğitim sonuçları için `models/` ve `yolo_results/weights/` klasörlerine bakınız.
- Park slotlarının koordinatları `config/slotlar_camX.json` dosyalarında tanımlanır.
- Büyük dosyalar (model ağırlıkları, videolar) Git LFS ile yönetilmektedir.

---


###  Ekran Görüntüleri

![1](img/1.png)
![2](img/2.png)
![3](img/3.png)

## Lisans

Bu proje MIT lisansı ile lisanslanmıştır. Detaylar için LICENSE dosyasına bakınız.

---

## İletişim

Her türlü soru, öneri veya iş birliği için:
- E-posta: adilomerpolat@gmail.com
- GitHub: [adilomrplt/OtoparkTakipSistemi](https://github.com/adilomrplt/OtoparkTakipSistemi.git)

