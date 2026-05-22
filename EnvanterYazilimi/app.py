# =============================================================================
#  KURUMSAL ENVANTER YÖNETİM SİSTEMİ (ANA MOTOR)
# =============================================================================

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3
import shutil
import datetime
import threading
import os
import traceback
import sys

# --- Gerekli Kütüphaneler ---
try:
    import google.generativeai as genai
    from PIL import Image, ImageTk
except ImportError:
    messagebox.showerror("Eksik Kütüphane",
                         "Lütfen terminale şunu yazın:\npip install customtkinter pillow google-generativeai pandas openpyxl")
    sys.exit()

# --- Projedeki Diğer Modüllerimiz ---
import veritabani
import Donanım
import Yazılım
import Personel
import Sistem
import Fiziksel_Mekan

# Veritabanını Başlat
try:
    veritabani.tablolari_olustur()
except Exception as e:
    print("Veritabanı başlatılamadı:", e)

# =============================================================================
# 1. YAPAY ZEKA (GEMINI) AYARLARI
# =============================================================================
API_DOSYASI = "api_key.txt"
GEMINI_API_KEY = ""

if os.path.exists(API_DOSYASI):
    with open(API_DOSYASI, "r", encoding="utf-8") as f:
        GEMINI_API_KEY = f.read().strip()

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# 🛑 ÇÖZÜM: 'gemini-1.5-flash' yerine en stabil olan 'gemini-pro' modeline geçildi!
ai_model = genai.GenerativeModel('gemini-pro')


def build_ai_ui(parent):
    ctk.CTkLabel(parent, text="🧠 Gemini AI Asistanı", font=("Segoe UI", 28, "bold"), text_color="#1E293B").pack(
        anchor="w", pady=(0, 5))
    ctk.CTkLabel(parent, text="Envanter hakkında sorular sorabilir, analiz isteyebilirsin.", text_color="#64748B").pack(
        anchor="w", pady=(0, 15))

    chat_frame = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=15)
    chat_frame.pack(fill="both", expand=True, pady=5)

    chat_box = ctk.CTkTextbox(chat_frame, font=("Segoe UI", 14), fg_color="#F8FAFC", text_color="#0F172A", wrap="word")
    chat_box.pack(fill="both", expand=True, padx=20, pady=20)

    if not GEMINI_API_KEY:
        chat_box.insert("0.0",
                        "⚠️ SİSTEM UYARISI: API Anahtarı Bulunamadı!\nLütfen 'api_key.txt' dosyasını kontrol edin.\n\n")
    else:
        chat_box.insert("0.0", "Gemini: Merhaba! BTK Envanter Sistemine bağlandım. Bana istediğini sorabilirsin!\n\n")

    input_frame = ctk.CTkFrame(parent, fg_color="transparent")
    input_frame.pack(fill="x", pady=10)

    prompt_entry = ctk.CTkEntry(input_frame, height=50, font=("Segoe UI", 14),
                                placeholder_text="Örn: Sistemde toplam kaç donanım var? Boşta olanlar hangileri?")
    prompt_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

    def ask_gemini():
        user_text = prompt_entry.get().strip()
        if not user_text: return

        chat_box.insert(tk.END, f"Sen: {user_text}\n")
        prompt_entry.delete(0, tk.END)
        chat_box.see(tk.END)

        if not GEMINI_API_KEY:
            chat_box.insert(tk.END, "Gemini: Lütfen 'api_key.txt' dosyasını oluşturup API anahtarını girin.\n\n")
            chat_box.see(tk.END)
            return

        def fetch_and_respond():
            try:
                db = sqlite3.connect("envanter.db");
                c = db.cursor()
                c.execute("SELECT donanim_adi, varlik_sahibi, departman FROM donanim")
                donanimlar = c.fetchall()
                c.execute("SELECT ad, soyad, departman, durumu FROM personel")
                personeller = c.fetchall()
                db.close()

                context = f"Sen BTK Envanter Sisteminin AI asistanısın. Türkçe, net ve kurumsal yanıt ver.\n"
                context += f"Donanımlar: {donanimlar}\nPersoneller: {personeller}\n\nSoru: {user_text}"

                response = ai_model.generate_content(context)
                chat_box.insert(tk.END, f"Gemini: {response.text}\n\n")
                chat_box.see(tk.END)
            except Exception as e:
                chat_box.insert(tk.END, f"Hata (API Anahtarını veya İnterneti Kontrol Et!): {e}\n\n")
                chat_box.see(tk.END)

        threading.Thread(target=fetch_and_respond).start()

    ctk.CTkButton(input_frame, text="SOR 🚀", height=50, font=("Segoe UI", 14, "bold"), fg_color="#4318FF",
                  command=ask_gemini).pack(side="right")
    parent.bind('<Return>', lambda e: ask_gemini())


# =============================================================================
# 2. ANA UYGULAMA (DASHBOARD VE SPA MİMARİSİ)
# =============================================================================
def build_app(parent):
    # Ana çerçeveyi ayarla
    parent.title(" Envanter Yazılımı | Modern Dashboard")
    parent.configure(bg="#F4F7FE")

    sidebar = ctk.CTkFrame(parent, fg_color="#FFFFFF", width=280, corner_radius=0)
    sidebar.pack(side="left", fill="y");
    sidebar.pack_propagate(False)

    logo_f = ctk.CTkFrame(sidebar, fg_color="transparent");
    logo_f.pack(fill="x", pady=40, padx=30)
    ctk.CTkLabel(logo_f, text="KTÜ", font=("Segoe UI", 32, "bold"), text_color="#4318FF").pack(side="left")
    ctk.CTkLabel(logo_f, text=" ENVANTER", font=("Segoe UI", 18, "bold"), text_color="#05CD99").pack(side="left",
                                                                                                     pady=(10, 0))

    main_content = ctk.CTkFrame(parent, fg_color="transparent")
    main_content.pack(side="right", fill="both", expand=True)

    # Menü Çerçeveleri
    frames = {n: ctk.CTkFrame(main_content, fg_color="transparent") for n in
              ("Dashboard", "Donanım", "Yazılım", "Personel", "Sistem", "Mekan", "AI")}

    def show_frame(name):
        for f in frames.values(): f.pack_forget()
        frames[name].pack(fill="both", expand=True, padx=40, pady=30)

    def side_btn(txt, ico, tgt, color="#2B3674"):
        b = ctk.CTkButton(sidebar, text=f"  {ico}   {txt}", command=lambda: show_frame(tgt), fg_color="transparent",
                          text_color=color, hover_color="#F4F7FE", font=("Segoe UI", 15, "bold"), anchor="w", height=50,
                          corner_radius=15)
        b.pack(fill="x", pady=5, padx=20);
        return b

    side_btn("Ana Sayfa", "📊", "Dashboard")
    side_btn("Donanım", "💻", "Donanım")
    side_btn("Yazılım", "💿", "Yazılım")
    side_btn("Personel", "👤", "Personel")
    side_btn("Sistem", "⚙️", "Sistem")
    side_btn("Fiziksel Mekan", "🏢", "Mekan")
    side_btn("Yapay Zeka AI", "🧠", "AI", color="#4318FF")

    def yedek_al():
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        yol = filedialog.asksaveasfilename(initialfile=f"Yedek_{ts}.db", defaultextension=".db")
        if yol:
            shutil.copy("envanter.db", yol)
            messagebox.showinfo("Başarılı", "Yedek alındı.", parent=parent)

    ctk.CTkButton(sidebar, text="🛡️ Sistemi Yedekle", command=yedek_al, fg_color="#E0E5F2", text_color="#4318FF",
                  hover_color="#D1D9E8", font=("Segoe UI", 14, "bold"), height=50, corner_radius=15).pack(side="bottom",
                                                                                                          fill="x",
                                                                                                          padx=20,
                                                                                                          pady=40)

    # -------------------------------------------------------------------------
    # DASHBOARD GRAFİKLERİ
    # -------------------------------------------------------------------------
    dash_f = frames["Dashboard"]
    top_header = ctk.CTkFrame(dash_f, fg_color="transparent");
    top_header.pack(fill="x", pady=(0, 20))
    ctk.CTkLabel(top_header, text="Ana Sayfa", font=("Segoe UI", 34, "bold"), text_color="#2B3674").pack(side="left")
    ctk.CTkLabel(top_header, text=datetime.datetime.now().strftime("%d %B %Y"), font=("Segoe UI", 15, "bold"),
                 text_color="#4318FF").pack(side="right", pady=15)

    stats_frame = ctk.CTkFrame(dash_f, fg_color="transparent");
    stats_frame.pack(fill="x", pady=10)
    stats_frame.columnconfigure((0, 1, 2, 3, 4), weight=1);
    stat_refs = {}

    def create_card(col, title, color):
        c = ctk.CTkFrame(stats_frame, fg_color="#FFFFFF", corner_radius=20);
        c.grid(row=0, column=col, padx=10, sticky="nsew")
        i = ctk.CTkFrame(c, fg_color="transparent");
        i.pack(fill="both", padx=20, pady=25)
        ctk.CTkLabel(i, text=title, font=("Segoe UI", 14, "bold"), text_color="#A3AED0").pack(anchor="w")
        lbl = ctk.CTkLabel(i, text="0", font=("Segoe UI", 36, "bold"), text_color="#2B3674");
        lbl.pack(anchor="w", pady=(10, 0))
        return lbl

    stat_refs["donanim"] = create_card(0, "Donanım", "#4318FF")
    stat_refs["yazilim"] = create_card(1, "Yazılım", "#05CD99")
    stat_refs["personel"] = create_card(2, "Personel", "#EE5D50")
    stat_refs["sistem"] = create_card(3, "Sistem", "#868CFF")
    stat_refs["mekan"] = create_card(4, "Fiziksel Mekan", "#FFCE20")

    charts_row = ctk.CTkFrame(dash_f, fg_color="transparent");
    charts_row.pack(fill="both", expand=True, pady=20)
    charts_row.columnconfigure((0, 1), weight=1);
    charts_row.rowconfigure(0, weight=1)

    def chart_box(col, title):
        box = ctk.CTkFrame(charts_row, fg_color="#FFFFFF", corner_radius=20);
        box.grid(row=0, column=col, padx=10, sticky="nsew")
        ctk.CTkLabel(box, text=title, font=("Segoe UI", 18, "bold"), text_color="#2B3674").pack(pady=(20, 5))
        cv = tk.Canvas(box, width=280, height=280, bg="#FFFFFF", highlightthickness=0);
        cv.pack(expand=True)
        cv.create_arc(30, 30, 250, 250, start=0, extent=359.9, outline="#E5E7EB", width=30, style=tk.ARC)
        txt = ctk.CTkLabel(box, text="0", font=("Segoe UI", 16, "bold"), text_color="#2B3674", bg_color="#FFFFFF")
        txt.place(relx=0.5, rely=0.48, anchor="center")
        return box, cv, txt

    b1, cv1, txt1 = chart_box(0, "Kullanım Durumu Analizi")
    a1 = cv1.create_arc(30, 30, 250, 250, start=90, extent=0, outline="#4318FF", width=30, style=tk.ARC)
    a2 = cv1.create_arc(30, 30, 250, 250, start=90, extent=0, outline="#05CD99", width=30, style=tk.ARC)
    lbl_a1 = ctk.CTkLabel(b1, text="Zimmetli: 0", font=("Segoe UI", 12, "bold"));
    lbl_a1.pack(side="left", padx=30, pady=20)
    lbl_a2 = ctk.CTkLabel(b1, text="Boşta: 0", font=("Segoe UI", 12, "bold"));
    lbl_a2.pack(side="right", padx=30, pady=20)

    b2, cv2, txt2 = chart_box(1, "Genel Envanter Dağılımı")
    d1 = cv2.create_arc(30, 30, 250, 250, start=90, extent=0, outline="#4318FF", width=30, style=tk.ARC)
    d2 = cv2.create_arc(30, 30, 250, 250, start=90, extent=0, outline="#05CD99", width=30, style=tk.ARC)
    d3 = cv2.create_arc(30, 30, 250, 250, start=90, extent=0, outline="#EE5D50", width=30, style=tk.ARC)
    d4 = cv2.create_arc(30, 30, 250, 250, start=90, extent=0, outline="#868CFF", width=30, style=tk.ARC)
    d5 = cv2.create_arc(30, 30, 250, 250, start=90, extent=0, outline="#FFCE20", width=30, style=tk.ARC)

    def live_engine():
        if not parent.winfo_exists(): return
        try:
            db = sqlite3.connect("envanter.db");
            cursor = db.cursor()
            q = {"donanim": "SELECT COUNT(*) FROM donanim", "yazilim": "SELECT COUNT(*) FROM yazilim",
                 "personel": "SELECT COUNT(*) FROM personel", "sistem": "SELECT COUNT(*) FROM sistem",
                 "mekan": "SELECT COUNT(*) FROM fiziksel_mekan"}
            for k, sql in q.items():
                cursor.execute(sql);
                stat_refs[k].configure(text=str(cursor.fetchone()[0]))

            cursor.execute("SELECT varlik_sahibi FROM donanim");
            d_sahipler = cursor.fetchall()
            cursor.execute("SELECT varlik_sahibi FROM yazilim");
            y_sahipler = cursor.fetchall()
            tum_varliklar = d_sahipler + y_sahipler

            aktif_count = sum(1 for r in tum_varliklar if r[0] and str(r[0]).strip() not in ["", "Boşta", "None"])
            bosta_count = len(tum_varliklar) - aktif_count
            total1 = aktif_count + bosta_count
            txt1.configure(text=f"TOPLAM\n{total1} Kayıt")

            if total1 > 0:
                cv1.itemconfig(a1, extent=(aktif_count / total1) * 359.9);
                cv1.itemconfig(a2, start=90 + (aktif_count / total1) * 360, extent=(bosta_count / total1) * 359.9)
                lbl_a1.configure(text=f"Zimmetli: {aktif_count} (%{(aktif_count / total1) * 100:.1f})")
                lbl_a2.configure(text=f"Boşta: {bosta_count} (%{(bosta_count / total1) * 100:.1f})")

            d_count = len(d_sahipler);
            y_count = len(y_sahipler)
            p_count = int(stat_refs["personel"].cget("text"));
            s_count = int(stat_refs["sistem"].cget("text"));
            m_count = int(stat_refs["mekan"].cget("text"))
            total2 = d_count + y_count + p_count + s_count + m_count
            txt2.configure(text=f"ENVANTER\n{total2} Birim")

            if total2 > 0:
                ang1 = (d_count / total2) * 360;
                ang2 = (y_count / total2) * 360;
                ang3 = (p_count / total2) * 360;
                ang4 = (s_count / total2) * 360;
                ang5 = (m_count / total2) * 360
                cv2.itemconfig(d1, extent=max(ang1 - 0.1, 0));
                cv2.itemconfig(d2, start=90 + ang1, extent=max(ang2 - 0.1, 0))
                cv2.itemconfig(d3, start=90 + ang1 + ang2, extent=max(ang3 - 0.1, 0));
                cv2.itemconfig(d4, start=90 + ang1 + ang2 + ang3, extent=max(ang4 - 0.1, 0))
                cv2.itemconfig(d5, start=90 + ang1 + ang2 + ang3 + ang4, extent=max(ang5 - 0.1, 0))
            db.close()
        except Exception:
            pass
        parent.after(2000, live_engine)

    live_engine()

    # 🛑 SENİN PYCHARM'DAKİ MODÜLLERİNİ BURAYA ENJEKTE EDİYORUZ 🛑
    try:
        Donanım.build_ui(frames["Donanım"])
        Yazılım.build_ui(frames["Yazılım"])
        Personel.build_ui(frames["Personel"])
        Sistem.build_ui(frames["Sistem"])
        Fiziksel_Mekan.build_ui(frames["Mekan"])
        build_ai_ui(frames["AI"])
    except Exception as e:
        print("Modüller yüklenirken hata oluştu:", e)

    show_frame("Dashboard")


# =============================================================================
# 3. GİRİŞ EKRANI (BAŞLANGIÇ)
# =============================================================================
def giris_yap(event=None):
    k_adi = entry_kullanici.get().strip()
    sifre = entry_sifre.get().strip()

    if not k_adi or not sifre:
        return messagebox.showwarning("Hata", "Boş bırakılamaz!")

    if k_adi == "admin" and sifre == "12345":
        root.unbind('<Configure>')
        root.unbind('<Return>')
        for w in root.winfo_children(): w.destroy()  # Ekranı sil
        build_app(root)  # Dashboard'u aynı ekrana çiz
    else:
        messagebox.showerror("Hata", "Yanlış giriş!")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("BTK Envanter Yazılımı | Güvenli Giriş")
    root.state("zoomed")
    root.configure(bg="#0B0F19")

    try:
        bg_img = Image.open("arkaplan.jpg")
        bg_img = bg_img.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_img)
        lbl_bg = tk.Label(root, image=bg_photo, bg="#0B0F19")
        lbl_bg.place(x=0, y=0, relwidth=1, relheight=1)
    except:
        pass  # Resim yoksa siyah kalsın

    frame_login = tk.Frame(root, bg="#161B22", bd=0, highlightthickness=1, highlightbackground="#30363D")
    frame_login.place(relx=0.5, rely=0.5, anchor="center", width=400, height=480)

    tk.Label(frame_login, text="BTK ENVANTER YÖNETİM SİSTEMİ", font=("Segoe UI", 26, "bold"), fg="#2563EB", bg="#161B22").pack(
        pady=(40, 5))
    tk.Label(frame_login, text="Kurumsal Yönetim Yazılımı", font=("Segoe UI", 10), fg="#8B949E", bg="#161B22").pack(
        pady=(0, 30))

    tk.Label(frame_login, text="Kullanıcı Adı", font=("Segoe UI", 11, "bold"), fg="#2563EB", bg="#161B22").pack(
        anchor="w", padx=50)
    entry_kullanici = tk.Entry(frame_login, font=("Segoe UI", 14), bg="#090B10", fg="white", insertbackground="white",
                               bd=0, highlightthickness=1, highlightbackground="#30363D")
    entry_kullanici.pack(fill="x", padx=50, pady=(5, 20), ipady=8)

    tk.Label(frame_login, text="Şifre", font=("Segoe UI", 11, "bold"), fg="#2563EB", bg="#161B22").pack(anchor="w",
                                                                                                        padx=50)
    entry_sifre = tk.Entry(frame_login, show="*", font=("Segoe UI", 14), bg="#090B10", fg="white",
                           insertbackground="white", bd=0, highlightthickness=1, highlightbackground="#30363D")
    entry_sifre.pack(fill="x", padx=50, pady=(5, 30), ipady=8)

    tk.Button(frame_login, text="GİRİŞ YAP", command=giris_yap, font=("Segoe UI", 12, "bold"), bg="#2563EB", fg="white",
              bd=0, cursor="hand2").pack(fill="x", padx=50, ipady=10)

    root.bind('<Return>', giris_yap)
    root.mainloop()