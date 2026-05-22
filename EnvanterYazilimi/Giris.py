import tkinter as tk
from tkinter import messagebox
import traceback
import sys
import os

try:
    import Ana_Sayfa
    import veritabani

    veritabani.tablolari_olustur()
except Exception as e:
    hata_mesaji = traceback.format_exc()
    hata_penceresi = tk.Tk()
    hata_penceresi.withdraw()
    messagebox.showerror("Kritik Sistem Hatası", f"Sistem bileşenleri yüklenemedi:\n\n{hata_mesaji}")
    sys.exit()

try:
    from PIL import Image, ImageTk

    PIL_YUKLU = True
except ImportError:
    PIL_YUKLU = False


def giris_yap(event=None):
    kullanici_adi = entry_kullanici.get().strip()
    sifre = entry_sifre.get().strip()

    if not kullanici_adi or not sifre:
        messagebox.showwarning("Giriş Engellendi", "Kullanıcı adı veya şifre alanı boş bırakılamaz!")
        return

    if kullanici_adi == "admin" and sifre == "12345":
        try:
            # 🛑 EKRAN KAPANMADAN GEÇİŞ MANTIĞI 🛑
            root.unbind('<Configure>')
            root.unbind('<Return>')
            for widget in root.winfo_children():
                widget.destroy()  # Sadece ekrandaki giriş kutularını sil

            Ana_Sayfa.build_app(root)  # Yeni arayüzü AYNI pencereye çiz
        except Exception as e:
            messagebox.showerror("Arayüz Hatası", f"Ana sayfa yüklenirken hata oluştu:\n{e}")
    else:
        messagebox.showerror("Hatalı Kimlik Doğrulama", "Geçersiz kullanıcı adı veya şifre girdiniz!")


root = tk.Tk()
root.title("KTÜ Envanter Yazılımı | Güvenli Giriş")
root.state("zoomed")

ekran_genislik = root.winfo_screenwidth()
ekran_yukseklik = root.winfo_screenheight()

canvas = tk.Canvas(root, highlightthickness=0)
canvas.pack(fill="both", expand=True)

if PIL_YUKLU and os.path.exists("arkaplan.jpg"):
    try:
        orijinal_resim = Image.open("arkaplan.jpg")
        yenilendirilmis_resim = orijinal_resim.resize((ekran_genislik, ekran_yukseklik), Image.Resampling.LANCZOS)
        bg_resim = ImageTk.PhotoImage(yenilendirilmis_resim)
        canvas.create_image(0, 0, image=bg_resim, anchor="nw")
        root.bg_resim = bg_resim
    except Exception:
        canvas.configure(bg="#0B0F19")
else:
    canvas.configure(bg="#0B0F19")

frame_login = tk.Frame(root, bg="#161B22", bd=0, highlightthickness=1, highlightbackground="#30363D")
frame_login.place(relx=0.5, rely=0.5, anchor="center", width=400, height=480)

tk.Label(frame_login, text="KTÜ ENVANTER", font=("Segoe UI", 26, "bold"), fg="#2563EB", bg="#161B22").pack(pady=(40, 5))
tk.Label(frame_login, text="Kurumsal Yönetim Yazılımı", font=("Segoe UI", 10), fg="#8B949E", bg="#161B22").pack(
    pady=(0, 30))

tk.Label(frame_login, text="Kullanıcı Adı", font=("Segoe UI", 11, "bold"), fg="#2563EB", bg="#161B22").pack(anchor="w",
                                                                                                            padx=50)
entry_kullanici = tk.Entry(frame_login, font=("Segoe UI", 14), bg="#090B10", fg="white", insertbackground="white", bd=0,
                           highlightthickness=1, highlightbackground="#30363D", highlightcolor="#2563EB")
entry_kullanici.pack(fill="x", padx=50, pady=(5, 20), ipady=8)

tk.Label(frame_login, text="Şifre", font=("Segoe UI", 11, "bold"), fg="#2563EB", bg="#161B22").pack(anchor="w", padx=50)
entry_sifre = tk.Entry(frame_login, show="*", font=("Segoe UI", 14), bg="#090B10", fg="white", insertbackground="white",
                       bd=0, highlightthickness=1, highlightbackground="#30363D", highlightcolor="#2563EB")
entry_sifre.pack(fill="x", padx=50, pady=(5, 30), ipady=8)

btn_giris = tk.Button(frame_login, text="GİRİŞ YAP", command=giris_yap, font=("Segoe UI", 12, "bold"), bg="#2563EB",
                      fg="white", activebackground="#1D4ED8", activeforeground="white", bd=0, cursor="hand2")
btn_giris.pack(fill="x", padx=50, ipady=10)

tk.Label(frame_login, text="KTÜ Kurumsal Güvenlik Altyapısı", font=("Segoe UI", 8, "bold"), fg="#10B981",
         bg="#161B22").pack(side="bottom", pady=20)

root.bind('<Return>', giris_yap)
root.mainloop()