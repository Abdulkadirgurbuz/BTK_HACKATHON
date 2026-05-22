import sqlite3

def tablolari_olustur():
    baglanti = sqlite3.connect("envanter.db")
    imlec = baglanti.cursor()

    # ================= 1. TABLOLARIN OLUŞTURULMASI =================
    imlec.execute("""CREATE TABLE IF NOT EXISTS donanim (id INTEGER PRIMARY KEY AUTOINCREMENT, varlik_grubu TEXT, varlik_kodu TEXT, donanim_adi TEXT, donanim_tipi TEXT, seri_no TEXT, marka TEXT, model TEXT, stok_durumu TEXT, departman TEXT, varlik_sahibi TEXT)""")
    imlec.execute("""CREATE TABLE IF NOT EXISTS yazilim (id INTEGER PRIMARY KEY AUTOINCREMENT, varlik_grubu TEXT, varlik_kodu TEXT, yazilim_adi TEXT, uretici TEXT, versiyon TEXT, satici TEXT, fiyat TEXT, satin_alma_tarihi TEXT, lisans_baslangic TEXT, lisans_bitis TEXT, lisans_tipi TEXT, departman TEXT, varlik_sahibi TEXT)""")
    imlec.execute("""CREATE TABLE IF NOT EXISTS personel (id INTEGER PRIMARY KEY AUTOINCREMENT, varlik_grubu TEXT, varlik_kodu TEXT, sicil_no TEXT, ad TEXT, soyad TEXT, ise_giris TEXT, isten_cikis TEXT, departman TEXT, durumu TEXT)""")
    imlec.execute("""CREATE TABLE IF NOT EXISTS sistem (id INTEGER PRIMARY KEY AUTOINCREMENT, varlik_grubu TEXT, varlik_kodu TEXT, sistem_adi TEXT, departman TEXT, sorumlu TEXT)""")
    imlec.execute("""CREATE TABLE IF NOT EXISTS fiziksel_mekan (id INTEGER PRIMARY KEY AUTOINCREMENT, varlik_grubu TEXT, varlik_kodu TEXT, departman TEXT, sorumlu TEXT)""")
    imlec.execute("""CREATE TABLE IF NOT EXISTS varlik_gruplari (kod TEXT PRIMARY KEY, ad TEXT)""")
    imlec.execute("""CREATE TABLE IF NOT EXISTS departmanlar (ad TEXT PRIMARY KEY)""")

    gruplar_listesi = [
        "1 - AĞ VE SİSTEMLER", "1.1 - NETWORK CİHAZLARI", "1.2 - SUNUCU VE YEDEKLEME ÜNİTELERİ",
        "2 - UYGULAMALAR", "2.1 - KRİTİK VERİ İŞLEYEN UYGULAMALAR", "2.2 - KRİTİK VERİ İŞLEMEYEN UYGULAMALAR", "2.3 - GELİŞTİRİLEN UYGULAMALAR",
        "3 - TAŞINABİLİR CİHAZ VE ORTAMLAR", "3.1 - AKILLI TELEFON VE TABLETLER", "3.2 - DİZÜSTÜ VE MASAÜSTÜ BİLGİSAYARLAR",
        "4 - NESNELERİN İNTERNETİ (IOT) CİHAZLARI", "4.1 - GÜVENLİK KAMERALARI", "4.2 - ACCESS POINTLER", "4.3 - TURNIKE, PDKS",
        "5 - PERSONEL", "5.1 - ÜST YÖNETİCİLER", "5.2 - BİRİM SORUMLULARI", "5.3 - KRİTİK KULLANICILAR", "5.4 - SON KULLANICILAR",
        "6 - FİZİKSEL MEKANLAR", "6.1 - ANA MERKEZ SUNUCU ODASI", "6.2 - FKM ODASI", "6.3 - NETWORK DAĞITIM NOKTALARI", "6.4 - CCTV ODASI", "6.5 - PERSONEL ODALARI"
    ]
    imlec.execute("SELECT COUNT(*) FROM varlik_gruplari")
    if imlec.fetchone()[0] == 0:
        veri_gruplar = [(g.split(' - ')[0], g.split(' - ')[1]) for g in gruplar_listesi]
        imlec.executemany("INSERT INTO varlik_gruplari (kod, ad) VALUES (?, ?)", veri_gruplar)

    aktif_gruplar = [g for g in gruplar_listesi if "6.2" not in g]

    # ================= 2. TEK DOĞRU KAYNAK (MASTER DATA) =================
    # Artık sistemdeki tüm varlıklar bu listeye göre dağıtılacak. Ahmet Yılmaz HER YERDE Bilgi İşlem'de olacak!
    KURUMSAL_KADRO = [
        ("Ahmet", "Yılmaz", "Bilgi İşlem"), ("Ayşe", "Kaya", "Ağ Yönetimi"),
        ("Mehmet", "Demir", "Sistem Yönetimi"), ("Fatma", "Çelik", "Yazılım Geliştirme"),
        ("Mustafa", "Şahin", "Veritabanı"), ("Zeynep", "Yıldız", "Web Teknolojileri"),
        ("Ali", "Yıldırım", "Ar-Ge"), ("Elif", "Öztürk", "Satın Alma"),
        ("Kemal", "Aydın", "Saha Operasyon"), ("Esra", "Özdemir", "Muhasebe"),
        ("Burak", "Arslan", "İnovasyon"), ("Derya", "Doğan", "Siber Güvenlik"),
        ("Hasan", "Kılıç", "Ağ Yönetimi"), ("Ceren", "Aslan", "İnsan Kaynakları"),
        ("Hüseyin", "Çetin", "Genel Merkez"), ("Yasemin", "Kara", "Yönetim Kurulu"),
        ("Volkan", "Koç", "İdari İşler"), ("Gizem", "Kurt", "Tasarım"),
        ("Gökhan", "Özkan", "Müşteri Hizmetleri"), ("Tuğba", "Şimşek", "Güvenlik"),
        ("Sinan", "Polat", "BT Altyapı"), ("Merve", "Öz", "Lojistik"),
        ("Murat", "Erdoğan", "Tesis Güvenlik"), ("Emine", "Yavuz", "Halkla İlişkiler")
    ]

    imlec.execute("SELECT COUNT(*) FROM departmanlar")
    if imlec.fetchone()[0] == 0:
        essiz_departmanlar = list(set([kisi[2] for kisi in KURUMSAL_KADRO]))
        veri_dept = [(d,) for d in essiz_departmanlar]
        imlec.executemany("INSERT OR IGNORE INTO departmanlar (ad) VALUES (?)", veri_dept)

    # ================= 3. PERSONEL TABLOSU =================
    imlec.execute("SELECT COUNT(*) FROM personel")
    if imlec.fetchone()[0] == 0:
        personel_verileri = []
        farkli_tarihler = ["10.01.2018", "15.03.2019", "22.05.2020", "01.09.2021", "14.11.2017", "05.02.2022", "19.07.2016", "30.08.2020", "11.12.2019", "08.04.2021", "25.10.2018", "03.06.2022", "17.01.2015", "29.09.2020", "12.02.2019", "07.07.2021", "21.03.2017", "14.05.2022", "09.11.2018", "26.08.2020", "02.04.2016", "18.10.2021", "31.01.2019", "15.07.2022"]
        cikan_personeller = [4, 11, 16, 22]
        cikis_tarihleri = {4: "20.12.2022", 11: "15.08.2023", 16: "01.11.2023", 22: "10.01.2024"}

        for i, (ad, soyad, dept) in enumerate(KURUMSAL_KADRO):
            grup = aktif_gruplar[i]
            if i in cikan_personeller:
                cikis = cikis_tarihleri[i]
                durum = "İşten Ayrıldı"
            else:
                cikis = "-"
                durum = "Aktif"
            personel_verileri.append((grup, f"PR-{i+1:03d}", f"{1001+i}", ad, soyad, farkli_tarihler[i], cikis, dept, durum))
        imlec.executemany("INSERT INTO personel (varlik_grubu, varlik_kodu, sicil_no, ad, soyad, ise_giris, isten_cikis, departman, durumu) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", personel_verileri)

    # ================= 4. DONANIM TABLOSU (Sayısal Stok Eklendi) =================
    imlec.execute("SELECT COUNT(*) FROM donanim")
    if imlec.fetchone()[0] == 0:
        gercek_donanimlar = [
            ("Omurga Router", "Yönlendirici", "RTR-998811", "Digiphone", "DP-R8000", "5"),
            ("Kenar Switch 48 Port", "Switch", "SW-445522", "Digiphone", "DP-S48G", "12"),
            ("Veritabanı Sunucusu", "Rack Sunucu", "SRV-773322", "Asus", "RS720-E10", "2"),
            ("ERP Uygulama Sunucusu", "Tower Sunucu", "APP-112233", "Casper", "Excalibur S-Tower", "4"),
            ("Kritik Veri Depolama", "NAS Cihazı", "STG-554433", "Acer", "Altos Storage", "3"),
            ("İç Ağ Web Sunucusu", "Mini PC Server", "WEB-889900", "Asus", "ExpertCenter D7", "8"),
            ("Yazılım Test Sunucusu", "Rack Sunucu", "TST-223344", "Casper", "Nirvana SRV-1U", "6"),
            ("Şifreli Taşınabilir Disk", "Harici Disk", "HDD-446688", "Reeder", "R-Drive 2TB", "25"),
            ("Saha Personel Telefonu", "Akıllı Telefon", "MOB-557799", "General Mobile", "GM 24 Pro", "40"),
            ("Muhasebe Dizüstü Bilgisayar", "Dizüstü PC", "LT-990011", "Acer", "TravelMate P2", "15"),
            ("Akıllı Bina Kontrolcüsü", "IoT Gateway", "IOT-332211", "Sunny", "SN-IoT Hub", "10"),
            ("Ana Giriş Güvenlik Kamerası", "IP Kamera", "CAM-776655", "Fujifilm", "X-Guard 4K", "35"),
            ("Misafir Ağı Erişim Noktası", "Access Point", "AP-884422", "Onvo", "OV-Net Wi-Fi 6", "20"),
            ("Personel Parmak İzi Okuyucu", "PDKS Cihazı", "TR-119933", "Seta", "Bio-Pass 500", "7"),
            ("Çağrı Merkezi Bilgisayarı", "Masaüstü PC", "PC-335577", "Casper", "Nirvana Desktop", "50"),
            ("Genel Müdür Bilgisayarı", "Ultrabook", "LT-882244", "Asus", "ZenBook 14 OLED", "2"),
            ("İnsan Kaynakları Sorumlu PC", "All-in-One PC", "AIO-663311", "Acer", "Veriton Z", "5"),
            ("Grafik Tasarım İş İstasyonu", "Workstation", "WS-448800", "Casper", "Excalibur Pro W", "3"),
            ("Depo Görevli Bilgisayarı", "İnce İstemci", "TC-227755", "SEG", "SEG ThinClient", "22"),
            ("Sistem Odası Isı Sensörü", "Ortam İzleme", "SN-993366", "Powertec", "PT-EnvSense", "10"),
            ("Hassas Kontrollü Klima", "İklimlendirme", "AC-115588", "SEG", "Cool-Master Pro", "4"),
            ("Kat Dağıtım Kabini", "Ağ Kabini", "RK-771144", "Kiwi", "K-Rack 24U", "8"),
            ("Merkezi Kayıt Cihazı", "NVR Cihazı", "NVR-550022", "OM System", "Guard-Vision 64CH", "3"),
            ("Toplantı Odası Ekranı", "Etkileşimli Ekran", "DIS-336699", "Sunny", "SN-Board 65", "6")
        ]

        donanim_verileri = []
        for i, grup in enumerate(aktif_gruplar):
            d_adi, d_tipi, d_seri, d_marka, d_model, stok = gercek_donanimlar[i]
            sahip_ad, sahip_soyad, sahip_dept = KURUMSAL_KADRO[i]
            tam_isim = f"{sahip_ad} {sahip_soyad}"
            # Departman kesinlikle kişinin KURUMSAL_KADRO'daki departmanı oluyor!
            donanim_verileri.append((grup, f"DN-{i+1:03d}", d_adi, d_tipi, d_seri, d_marka, d_model, stok, sahip_dept, tam_isim))
        imlec.executemany("INSERT INTO donanim (varlik_grubu, varlik_kodu, donanim_adi, donanim_tipi, seri_no, marka, model, stok_durumu, departman, varlik_sahibi) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", donanim_verileri)

    # Diğer tabloları da aynı kati kuralla dolduruyoruz
    imlec.execute("SELECT COUNT(*) FROM yazilim")
    if imlec.fetchone()[0] == 0:
        yazilim_isimleri = ["SolarWinds NMS", "Cisco Packet Tracer", "Veeam Backup", "SAP ERP", "Oracle Database 19c", "Microsoft Office 365", "GitLab Enterprise", "Kaspersky Endpoint", "SOTI MobiControl", "AutoCAD 2024", "Siemens IoT Platform", "Milestone XProtect", "Ubiquiti UniFi", "ZKTeco BioTime", "Pardus OS", "Zoom Pro", "Jira Premium", "Adobe Creative Cloud", "Windows 11 Pro", "PRTG Network Monitor", "VMware vSphere", "Nagios Core", "HikCentral Pro", "Slack Enterprise"]
        yazilim_verileri = []
        for i, grup in enumerate(aktif_gruplar):
            sahip_ad, sahip_soyad, sahip_dept = KURUMSAL_KADRO[i]
            tam_isim = f"{sahip_ad} {sahip_soyad}"
            yazilim_verileri.append((grup, f"YZ-{i+1:03d}", yazilim_isimleri[i], "Kurumsal Yazılım", "v2.0", "Lisans Sağlayıcı", "5000", "01.01.2023", "01.01.2023", "Süresiz", "Lisanslı", sahip_dept, tam_isim))
        imlec.executemany("INSERT INTO yazilim (varlik_grubu, varlik_kodu, yazilim_adi, uretici, versiyon, satici, fiyat, satin_alma_tarihi, lisans_baslangic, lisans_bitis, lisans_tipi, departman, varlik_sahibi) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", yazilim_verileri)

    imlec.execute("SELECT COUNT(*) FROM sistem")
    if imlec.fetchone()[0] == 0:
        sistem_isimlendirme = {"1 - AĞ VE SİSTEMLER": "Kurumsal Ağ Altyapı Sistemi", "1.1 - NETWORK CİHAZLARI": "Omurga Anahtarlama (Backbone) Sistemi", "1.2 - SUNUCU VE YEDEKLEME ÜNİTELERİ": "Felaket Kurtarma ve Yedekleme Sistemi", "2 - UYGULAMALAR": "İç Intranet ve İletişim Sistemi", "2.1 - KRİTİK VERİ İŞLEYEN UYGULAMALAR": "Kurumsal Kaynak Planlama (ERP) Sistemi", "2.2 - KRİTİK VERİ İŞLEMEYEN UYGULAMALAR": "Yardım Masası (Helpdesk) Sistemi", "2.3 - GELİŞTİRİLEN UYGULAMALAR": "Ar-Ge Yazılım Entegrasyon Sistemi", "3 - TAŞINABİLİR CİHAZ VE ORTAMLAR": "Uç Nokta Veri Güvenliği Sistemi (DLP)", "3.1 - AKILLI TELEFON VE TABLETLER": "Mobil Cihaz Yönetim Sistemi (MDM)", "3.2 - DİZÜSTÜ VE MASAÜSTÜ BİLGİSAYARLAR": "İstemci (Client) Yönetim Sistemi", "4 - NESNELERİN İNTERNETİ (IOT) CİHAZLARI": "Akıllı Bina Otomasyon Sistemi", "4.1 - GÜVENLİK KAMERALARI": "Kapalı Devre Kamera Sistemi (CCTV)", "4.2 - ACCESS POINTLER": "Kurumsal Kablosuz Ağ (Wi-Fi) Sistemi", "4.3 - TURNIKE, PDKS": "Personel Devam Kontrol Sistemi (PDKS)", "5 - PERSONEL": "Kimlik ve Erişim Yönetimi Sistemi (IAM)", "5.1 - ÜST YÖNETİCİLER": "Yönetici Bilgi Sistemi (MIS)", "5.2 - BİRİM SORUMLULARI": "Performans ve Hedef Takip Sistemi", "5.3 - KRİTİK KULLANICILAR": "Ayrıcalıklı Erişim Yönetim Sistemi (PAM)", "5.4 - SON KULLANICILAR": "Aktif Dizin (Active Directory) Sistemi", "6 - FİZİKSEL MEKANLAR": "Fiziksel Çevre Güvenlik Sistemi", "6.1 - ANA MERKEZ SUNUCU ODASI": "Veri Merkezi İklimlendirme ve Enerji Sistemi", "6.3 - NETWORK DAĞITIM NOKTALARI": "Kenar Anahtar (Edge Switch) İzleme Sistemi", "6.4 - CCTV ODASI": "Merkezi Güvenlik İzleme ve Kayıt Sistemi", "6.5 - PERSONEL ODALARI": "Akıllı Yangın ve Duman Algılama Sistemi"}
        sistem_verileri = []
        for i, grup in enumerate(aktif_gruplar):
            sahip_ad, sahip_soyad, sahip_dept = KURUMSAL_KADRO[i]
            tam_isim = f"{sahip_ad} {sahip_soyad}"
            sis_adi = sistem_isimlendirme.get(grup, "Genel Bilişim Sistemi")
            sistem_verileri.append((grup, f"SS-{i+1:03d}", sis_adi, sahip_dept, tam_isim))
        imlec.executemany("INSERT INTO sistem (varlik_grubu, varlik_kodu, sistem_adi, departman, sorumlu) VALUES (?, ?, ?, ?, ?)", sistem_verileri)

    imlec.execute("SELECT COUNT(*) FROM fiziksel_mekan")
    if imlec.fetchone()[0] == 0:
        mekan_verileri = []
        for i, grup in enumerate(aktif_gruplar):
            sahip_ad, sahip_soyad, sahip_dept = KURUMSAL_KADRO[i]
            tam_isim = f"{sahip_ad} {sahip_soyad}"
            mekan_verileri.append((grup, f"FM-{i+1:03d}", sahip_dept, tam_isim))
        imlec.executemany("INSERT INTO fiziksel_mekan (varlik_grubu, varlik_kodu, departman, sorumlu) VALUES (?, ?, ?, ?)", mekan_verileri)

    baglanti.commit()
    baglanti.close()

def varlik_gruplarini_getir():
    baglanti = sqlite3.connect("envanter.db")
    imlec = baglanti.cursor()
    imlec.execute("SELECT kod, ad FROM varlik_gruplari ORDER BY kod ASC")
    sonuclar = [f"{kod} - {ad}" for kod, ad in imlec.fetchall()]
    baglanti.close()
    return sonuclar

def personelleri_getir():
    baglanti = sqlite3.connect("envanter.db")
    imlec = baglanti.cursor()
    imlec.execute("SELECT ad, soyad FROM personel WHERE durumu != 'İşten Ayrıldı' ORDER BY ad ASC")
    sonuclar = [f"{row[0]} {row[1]}" for row in imlec.fetchall()]
    baglanti.close()
    return sonuclar

def departmanlari_getir():
    baglanti = sqlite3.connect("envanter.db")
    imlec = baglanti.cursor()
    imlec.execute("SELECT ad FROM departmanlar ORDER BY ad ASC")
    sonuclar = [row[0] for row in imlec.fetchall()]
    baglanti.close()
    return sonuclar

def siradaki_kodu_getir(tablo_adi, on_ek):
    baglanti = sqlite3.connect("envanter.db")
    imlec = baglanti.cursor()
    sorgu = f"SELECT varlik_kodu FROM {tablo_adi} ORDER BY id DESC LIMIT 1"
    imlec.execute(sorgu)
    sonuc = imlec.fetchone()
    baglanti.close()
    if sonuc and sonuc[0]:
        try:
            yeni_sayi = int(sonuc[0].split('-')[1]) + 1
        except:
            yeni_sayi = 1
    else:
        yeni_sayi = 1
    return f"{on_ek}-{yeni_sayi:03d}"