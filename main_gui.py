import sys
import json
import cv2
from math import ceil
from ultralytics import YOLO
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QFrame, QSizePolicy, QSlider, QMessageBox, QButtonGroup
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer, QTime

# DİNAMİK OTOMATİK YAPILANDIRMA
KAMERA_YAPILANDIRMA = {
    "Otopark 1": {
        "model": "./yolo_results/yolo_parking_v1/weights/best.pt",
        "slotlar": "./config/slotlar_cam1.json",
        "video": "./videos/cam1.mp4"
    },
    "Otopark 2": {
        "model": "./yolo_results/yolo_parking_v2/weights/best.pt",
        "slotlar": "./config/slotlar_cam2.json",
        "video": "./videos/cam2.mp4"
    },
    "Otopark 3": {
        "model": "./yolo_results/yolo_parking_v2/weights/best.pt",
        "slotlar": "./config/slotlar_cam3.json",
        "video": "./videos/cam3.mp4"
    },
    # Yeni otopark eklemek için buraya ekle!
}

class OtoparkUygulamasi(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Akıllı Otopark Analiz Sistemi")
        self.setGeometry(50, 50, 1850, 950)
        self.setStyleSheet("""
            QWidget { background-color: #f5f7fa; font-family: 'Segoe UI'; }
            QPushButton {
                background-color: #3a4a6b; color: white; border: none;
                padding: 8px 18px; border-radius: 4px; font-size: 14px; min-width: 110px;
            }
            QPushButton:checked {
                background-color: #223056;
                color: #ffe082;
                font-weight: bold;
                border: 2px solid #ffe082;
            }
            QPushButton:hover { background-color: #4a5a7b; }
            QPushButton:disabled { background-color: #cccccc; }
            QLabel { font-size: 14px; color: #333333; }
            QSlider::handle:horizontal {
                background: #3a4a6b; width: 14px; height: 14px; border-radius: 7px;
            }
        """)

        self.kamera_yapilandirma = KAMERA_YAPILANDIRMA
        self.otopark_adlari = list(self.kamera_yapilandirma.keys())
        self.otopark_adi = self.otopark_adlari[0]

        self.model = None
        self.slotlar = []
        self.kamera = None
        self.zamanlayici = QTimer()
        self.zamanlayici.timeout.connect(self.kareyi_guncelle)
        self.slot_etiketleri = []
        self.duraklatildi = False

        self.arayuz_olustur()
        self.otopark_degisti(self.otopark_adi)

    def arayuz_olustur(self):
        ana_düzen = QHBoxLayout(self)
        ana_düzen.setContentsMargins(10, 10, 10, 10)
        ana_düzen.setSpacing(15)

        # ---------- SOL PANEL ----------
        sol_panel = QVBoxLayout()
        sol_panel.setSpacing(10)

        # Otopark seçim butonları (yan yana)
        self.otopark_buton_grup = QButtonGroup(self)
        self.otopark_butonlar = []
        otopark_secim_panel = QHBoxLayout()
        otopark_secim_panel.setSpacing(12)
        for i, adi in enumerate(self.otopark_adlari):
            btn = QPushButton(adi)
            btn.setCheckable(True)
            if i == 0:
                btn.setChecked(True)
            self.otopark_buton_grup.addButton(btn, i)
            self.otopark_butonlar.append(btn)
            otopark_secim_panel.addWidget(btn)
        self.otopark_buton_grup.buttonClicked[int].connect(self.otopark_buton_secildi)
        sol_panel.addLayout(otopark_secim_panel)

        # Video paneli (daima 1280x720)
        self.video_etiketi = QLabel("Video yükleniyor...")
        self.video_etiketi.setAlignment(Qt.AlignCenter)
        self.video_etiketi.setFixedSize(1280, 720)
        self.video_etiketi.setStyleSheet("""
            background-color: #2c3e50;
            color: #ecf0f1;
            font-size: 18px;
            border-radius: 4px;
        """)
        sol_panel.addWidget(self.video_etiketi)

        # Kontrol butonları
        kontrol_düzeni = QHBoxLayout()
        self.buton_baslat = QPushButton("Başlat")
        self.buton_baslat.setEnabled(False)
        self.buton_baslat.clicked.connect(self.videoyu_baslat)
        self.buton_durdur = QPushButton("Durdur")
        self.buton_durdur.setEnabled(False)
        self.buton_durdur.clicked.connect(self.videoyu_durdur)
        self.buton_geri = QPushButton("◀◀ 10sn")
        self.buton_geri.setEnabled(False)
        self.buton_geri.clicked.connect(self.geri_10sn)
        self.buton_ileri = QPushButton("10sn ▶▶")
        self.buton_ileri.setEnabled(False)
        self.buton_ileri.clicked.connect(self.ileri_10sn)
        kontrol_düzeni.addWidget(self.buton_baslat)
        kontrol_düzeni.addWidget(self.buton_durdur)
        kontrol_düzeni.addWidget(self.buton_geri)
        kontrol_düzeni.addWidget(self.buton_ileri)
        sol_panel.addLayout(kontrol_düzeni)

        # Zaman kaydırıcı
        self.zaman_kaydirici = QSlider(Qt.Horizontal)
        self.zaman_kaydirici.setRange(0, 0)
        self.zaman_kaydirici.setEnabled(False)
        self.zaman_kaydirici.sliderMoved.connect(self.zaman_kaydirildi)
        sol_panel.addWidget(self.zaman_kaydirici)

        # Zaman göstergeleri
        zaman_düzeni = QHBoxLayout()
        self.suanki_zaman = QLabel("00:00:00")
        self.suanki_zaman.setStyleSheet("font-weight: bold; font-size: 14px;")
        zaman_ayrac = QLabel("/")
        zaman_ayrac.setStyleSheet("font-weight: bold;")
        self.toplam_sure = QLabel("00:00:00")
        self.toplam_sure.setStyleSheet("font-weight: bold; font-size: 14px;")
        zaman_düzeni.addStretch()
        zaman_düzeni.addWidget(self.suanki_zaman)
        zaman_düzeni.addWidget(zaman_ayrac)
        zaman_düzeni.addWidget(self.toplam_sure)
        zaman_düzeni.addStretch()
        sol_panel.addLayout(zaman_düzeni)

        ana_düzen.addLayout(sol_panel, 4)

        # ----------- SAĞ PANEL -----------
        sag_panel = QFrame()
        sag_panel.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 6px;
            border: 1px solid #d1d5db;
        """)
        sag_panel.setFixedWidth(470)
        sag_duzen = QVBoxLayout(sag_panel)
        sag_duzen.setContentsMargins(10, 10, 10, 10)
        sag_duzen.setSpacing(10)

        # Analiz kutusu
        istatistik_kutu = QFrame()
        istatistik_kutu.setStyleSheet("""
            background-color: #f8fafc;
            border-radius: 6px;
            border: 1px solid #d1d5db;
            padding: 10px;
        """)
        istatistik_duzen = QVBoxLayout(istatistik_kutu)
        istatistik_baslik = QLabel("ANALİZ SONUÇLARI")
        istatistik_baslik.setAlignment(Qt.AlignCenter)
        istatistik_baslik.setStyleSheet("font-weight: bold; font-size: 18px; color: #3a4a6b;")
        istatistik_duzen.addWidget(istatistik_baslik)
        self.etiket_durum = QLabel("Dolu: 0 | Boş: 0 | Toplam: 0")
        self.etiket_durum.setAlignment(Qt.AlignCenter)
        self.etiket_durum.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        istatistik_duzen.addWidget(self.etiket_durum)
        self.yuzde_etiketi = QLabel("Doluluk: %0")
        self.yuzde_etiketi.setAlignment(Qt.AlignCenter)
        self.yuzde_etiketi.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #3a4a6b;
        """)
        istatistik_duzen.addWidget(self.yuzde_etiketi)
        sag_duzen.addWidget(istatistik_kutu)
        istatistik_kutu.setLayout(istatistik_duzen)

        baslik = QLabel("PARK ALANLARI DURUMU")
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #3a4a6b;
            padding-bottom: 10px;
            border-bottom: 2px solid #3a4a6b;
        """)
        sag_duzen.addWidget(baslik)

        # Dinamik grid alanı (scroll yok!)
        self.grid_widget = QWidget()
        self.grid = QGridLayout(self.grid_widget)
        self.grid.setSpacing(8)
        self.grid.setContentsMargins(8, 8, 8, 8)
        sag_duzen.addWidget(self.grid_widget)
        sag_duzen.addStretch()
        ana_düzen.addWidget(sag_panel, 2)

    def otopark_buton_secildi(self, idx):
        for i, btn in enumerate(self.otopark_butonlar):
            btn.setChecked(i == idx)
        otopark_adi = self.otopark_adlari[idx]
        self.otopark_degisti(otopark_adi)

    def otopark_degisti(self, otopark_adi):
        try:
            self.otopark_adi = otopark_adi
            ayar = self.kamera_yapilandirma[otopark_adi]
            self.model = YOLO(ayar["model"])
            with open(ayar["slotlar"], "r", encoding="utf-8") as f:
                self.slotlar = json.load(f)
            # Video paneli daima büyük!
            self.video_etiketi.setFixedSize(1280, 720)
            self.video_ac(ayar["video"])
            self.grid_guncelle()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Otopark yükleme hatası: {str(e)}")

    def grid_guncelle(self):
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        self.slot_etiketleri = []
        toplam_slot = len(self.slotlar)
        # Büyük otoparklarda da sığacak şekilde optimize grid!
        if toplam_slot <= 24:
            sutun_sayisi = 6
            kutu_boy = 54
            font_size = 18
        elif toplam_slot <= 50:
            sutun_sayisi = 8
            kutu_boy = 45
            font_size = 15
        elif toplam_slot <= 80:
            sutun_sayisi = 10
            kutu_boy = 38
            font_size = 13
        elif toplam_slot <= 120:
            sutun_sayisi = 10
            kutu_boy = 31
            font_size = 12
        else:
            sutun_sayisi = 12
            kutu_boy = 28
            font_size = 10
        self.grid.setSpacing(8)
        for i in range(toplam_slot):
            etiket = QLabel(f"{i+1}")
            etiket.setFixedSize(kutu_boy, kutu_boy)
            etiket.setAlignment(Qt.AlignCenter)
            etiket.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            etiket.setStyleSheet(f"""
                QLabel {{
                    background-color: #e0e6ed;
                    color: #3a4a6b;
                    border-radius: 4px;
                    border: 1px solid #c0ccda;
                    font-size: {font_size}px;
                    font-weight: bold;
                }}
            """)
            satir = i // sutun_sayisi
            sutun = i % sutun_sayisi
            self.grid.addWidget(etiket, satir, sutun)
            self.slot_etiketleri.append(etiket)

    def video_ac(self, dosya_yolu):
        try:
            if self.kamera:
                self.kamera.release()
            self.kamera = cv2.VideoCapture(dosya_yolu)
            if not self.kamera.isOpened():
                raise Exception("Video açılamadı")

            fps = self.kamera.get(cv2.CAP_PROP_FPS)
            toplam_kare = int(self.kamera.get(cv2.CAP_PROP_FRAME_COUNT))
            sure = toplam_kare / fps

            zaman = QTime(0, 0).addSecs(int(sure))
            self.toplam_sure.setText(zaman.toString("HH:mm:ss"))

            self.zaman_kaydirici.setRange(0, toplam_kare)
            self.zaman_kaydirici.setEnabled(True)
            self.buton_baslat.setEnabled(True)
            self.buton_durdur.setEnabled(False)
            self.buton_ileri.setEnabled(True)
            self.buton_geri.setEnabled(True)
            self.video_etiketi.setText("Video yüklendi.")
            self.duraklatildi = False

            self.videoyu_baslat()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Video yükleme hatası: {str(e)}")
            if self.kamera:
                self.kamera.release()

    def videoyu_baslat(self):
        if self.kamera:
            self.zamanlayici.start(30)
            self.buton_baslat.setEnabled(False)
            self.buton_durdur.setEnabled(True)
            self.duraklatildi = False
            self.video_etiketi.setText("Video oynatılıyor...")

    def videoyu_durdur(self):
        if self.kamera:
            self.zamanlayici.stop()
            self.buton_baslat.setEnabled(True)
            self.buton_durdur.setEnabled(False)
            self.duraklatildi = True
            self.kareyi_guncelle()

    def geri_10sn(self):
        if self.kamera:
            mevcut_kare = self.kamera.get(cv2.CAP_PROP_POS_FRAMES)
            fps = self.kamera.get(cv2.CAP_PROP_FPS)
            yeni_konum = max(0, mevcut_kare - (10 * fps))
            self.kamera.set(cv2.CAP_PROP_POS_FRAMES, yeni_konum)
            self.zaman_kaydirici.setValue(int(yeni_konum))
            if self.duraklatildi:
                self.kareyi_guncelle()

    def ileri_10sn(self):
        if self.kamera:
            mevcut_kare = self.kamera.get(cv2.CAP_PROP_POS_FRAMES)
            fps = self.kamera.get(cv2.CAP_PROP_FPS)
            yeni_konum = mevcut_kare + (10 * fps)
            self.kamera.set(cv2.CAP_PROP_POS_FRAMES, yeni_konum)
            self.zaman_kaydirici.setValue(int(yeni_konum))
            if self.duraklatildi:
                self.kareyi_guncelle()

    def zaman_kaydirildi(self, konum):
        if self.kamera:
            self.kamera.set(cv2.CAP_PROP_POS_FRAMES, konum)
            if self.duraklatildi:
                self.kareyi_guncelle()

    def kareyi_guncelle(self):
        try:
            ret, kare = self.kamera.read()
            if not ret or kare is None:
                self.zamanlayici.stop()
                self.buton_baslat.setEnabled(False)
                self.buton_durdur.setEnabled(False)
                self.video_etiketi.setText("Video sona erdi")
                return

            vw = self.video_etiketi.width()
            vh = self.video_etiketi.height()
            kare = cv2.resize(kare, (vw, vh))
            tahmin = self.model.predict(kare, conf=0.3, iou=0.3)[0]
            kutular = tahmin.boxes.data.tolist()

            tespit_edilenler = []
            for k in kutular:
                x1, y1, x2, y2, guven, sinif = k
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                tespit_edilenler.append((cx, cy, int(sinif)))

            slot_durumu = ["empty"] * len(self.slotlar)
            dolu_sayisi = 0

            for i, slot in enumerate(self.slotlar):
                x = int(slot["x"] * vw)
                y = int(slot["y"] * vh)
                w = int(slot["w"] * vw)
                h = int(slot["h"] * vh)

                for cx, cy, sinif in tespit_edilenler:
                    if abs(cx - x) < w // 2 and abs(cy - y) < h // 2:
                        if sinif == 1:
                            slot_durumu[i] = "occupied"
                            dolu_sayisi += 1
                        break

                renk = (0, 255, 0) if slot_durumu[i] == "empty" else (0, 0, 255)
                cv2.rectangle(kare, (x - w//2, y - h//2), (x + w//2, y + h//2), renk, 2)
                cv2.putText(kare, str(i+1), (x - 10, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

            # Sağ paneldeki kutular
            for i, durum in enumerate(slot_durumu):
                if i < len(self.slot_etiketleri):
                    if durum == "occupied":
                        self.slot_etiketleri[i].setStyleSheet("""
                            QLabel {
                                background-color: #e74c3c;
                                color: white;
                                border-radius: 4px;
                                border: 2px solid #c0392b;
                                font-size: 15px;
                                font-weight: bold;
                            }
                        """)
                    else:
                        self.slot_etiketleri[i].setStyleSheet("""
                            QLabel {
                                background-color: #2ecc71;
                                color: white;
                                border-radius: 4px;
                                border: 2px solid #27ae60;
                                font-size: 15px;
                                font-weight: bold;
                            }
                        """)

            toplam_slot = len(self.slotlar)
            bos_sayisi = toplam_slot - dolu_sayisi
            oran = int((dolu_sayisi / toplam_slot) * 100) if toplam_slot > 0 else 0
            self.etiket_durum.setText(f"Dolu: {dolu_sayisi} | Boş: {bos_sayisi} | Toplam: {toplam_slot}")
            self.yuzde_etiketi.setText(f"Doluluk: %{oran}")

            mevcut_kare = int(self.kamera.get(cv2.CAP_PROP_POS_FRAMES))
            fps = self.kamera.get(cv2.CAP_PROP_FPS)
            zaman = QTime(0, 0).addSecs(int(mevcut_kare / fps))
            self.suanki_zaman.setText(zaman.toString("HH:mm:ss"))
            self.zaman_kaydirici.setValue(mevcut_kare)

            rgb = cv2.cvtColor(kare, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            satir_basi = ch * w
            qimg = QImage(rgb.data, w, h, satir_basi, QImage.Format_RGB888)
            self.video_etiketi.setPixmap(QPixmap.fromImage(qimg))

        except Exception as hata:
            print(f"Hata oluştu: {str(hata)}")
            self.zamanlayici.stop()

    def closeEvent(self, olay):
        self.zamanlayici.stop()
        if self.kamera:
            self.kamera.release()
        olay.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        pencere = OtoparkUygulamasi()
        pencere.show()
        sys.exit(app.exec_())
    except Exception as hata:
        print(f"Uygulama hatası: {str(hata)}")
        sys.exit(1)
