import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3
import shutil
import datetime

import Donanım, Yazılım, Personel, Sistem, Fiziksel_Mekan

def build_app(parent):
    # 🛑 YENİ PENCERE YERİNE GİRİŞ EKRANININ PENCERESİNİ KULLANIYORUZ 🛑
    new_window = parent
    new_window.title("KTÜ Envanter Yazılımı")
    new_window.configure(bg="#F4F7FE")

    CLR_BG = "#F4F7FE"; CLR_SIDEBAR = "#FFFFFF"; CLR_CARD = "#FFFFFF"
    CLR_DONANIM = "#4318FF"; CLR_YAZILIM = "#05CD99"; CLR_PERSONEL = "#EE5D50"
    CLR_SISTEM = "#868CFF"; CLR_MEKAN = "#FFCE20"
    CLR_TEXT = "#2B3674"; CLR_TEXT_LIGHT = "#A3AED0"

    sidebar = ctk.CTkFrame(new_window, fg_color=CLR_SIDEBAR, width=280, corner_radius=0)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
    logo_frame.pack(fill="x", pady=(40, 40), padx=30)

    ctk.CTkLabel(logo_frame, text="KTÜ", font=("Segoe UI", 32, "bold"), text_color=CLR_DONANIM).pack(side="left")
    ctk.CTkLabel(logo_frame, text=" ENVANTER", font=("Segoe UI", 18, "bold"), text_color=CLR_YAZILIM).pack(side="left", pady=(10, 0))

    main_content = ctk.CTkFrame(new_window, fg_color="transparent")
    main_content.pack(side="right", fill="both", expand=True)

    frames = {}
    for name in ("Dashboard", "Donanım", "Yazılım", "Personel", "Sistem", "Mekan"):
        frames[name] = ctk.CTkFrame(main_content, fg_color="transparent")

    def show_frame(name):
        for f in frames.values(): f.pack_forget()
        frames[name].pack(fill="both", expand=True, padx=40, pady=30)

    def create_side_btn(text, icon, target_frame):
        btn = ctk.CTkButton(
            sidebar, text=f"  {icon}   {text}", command=lambda: show_frame(target_frame),
            fg_color="transparent", text_color=CLR_TEXT, hover_color="#F4F7FE",
            font=("Segoe UI", 15, "bold"), anchor="w", height=50, corner_radius=15
        )
        btn.pack(fill="x", pady=(5, 10), padx=20)
        return btn

    create_side_btn("Ana Sayfa", "📊", "Dashboard")
    create_side_btn("Donanım", "💻", "Donanım")
    create_side_btn("Yazılım", "💿", "Yazılım")
    create_side_btn("Personel", "👤", "Personel")
    create_side_btn("Sistem", "⚙️", "Sistem")
    create_side_btn("Fiziksel Mekan", "🏢", "Mekan")

    def veritabani_yedekle():
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = filedialog.asksaveasfilename(initialfile=f"Yedek_{timestamp}.db", defaultextension=".db")
            if file_path:
                shutil.copy("envanter.db", file_path)
                messagebox.showinfo("Başarılı", "Sistem yedeği alındı.", parent=new_window)
        except Exception as e:
            messagebox.showerror("Hata", str(e), parent=new_window)

    ctk.CTkButton(sidebar, text="🛡️ Sistemi Yedekle", command=veritabani_yedekle, fg_color="#E0E5F2", text_color=CLR_DONANIM, hover_color="#D1D9E8", font=("Segoe UI", 14, "bold"), height=50, corner_radius=15).pack(side="bottom", fill="x", padx=20, pady=40)

    dash_f = frames["Dashboard"]
    top_header = ctk.CTkFrame(dash_f, fg_color="transparent")
    top_header.pack(fill="x", pady=(0, 20))

    header_left = ctk.CTkFrame(top_header, fg_color="transparent")
    header_left.pack(side="left")
    ctk.CTkLabel(header_left, text="Ana Sayfa", font=("Segoe UI", 34, "bold"), text_color=CLR_TEXT).pack(anchor="w")
    ctk.CTkLabel(header_left, text="Sistem durumunu ve envanter özetini buradan takip edebilirsiniz.", font=("Segoe UI", 14), text_color=CLR_TEXT_LIGHT).pack(anchor="w")

    ctk.CTkLabel(top_header, text=datetime.datetime.now().strftime("%d %B %Y, %A"), font=("Segoe UI", 15, "bold"), text_color=CLR_DONANIM).pack(side="right", pady=15)

    stats_frame = ctk.CTkFrame(dash_f, fg_color="transparent")
    stats_frame.pack(fill="x", pady=10)
    stats_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)
    stat_refs = {}

    def create_stat_card(col, title, color):
        card = ctk.CTkFrame(stats_frame, fg_color=CLR_CARD, corner_radius=20)
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", padx=20, pady=25)
        header_f = ctk.CTkFrame(inner, fg_color="transparent")
        header_f.pack(fill="x")
        ctk.CTkLabel(header_f, text=title, font=("Segoe UI", 15, "bold"), text_color=CLR_TEXT_LIGHT).pack(side="left")
        ctk.CTkFrame(header_f, fg_color=color, width=14, height=14, corner_radius=7).pack(side="right")
        lbl = ctk.CTkLabel(inner, text="0", font=("Segoe UI", 40, "bold"), text_color=CLR_TEXT)
        lbl.pack(anchor="w", pady=(15, 0))
        return lbl

    stat_refs["donanim"] = create_stat_card(0, "Donanım", CLR_DONANIM)
    stat_refs["yazilim"] = create_stat_card(1, "Yazılım", CLR_YAZILIM)
    stat_refs["personel"] = create_stat_card(2, "Personel", CLR_PERSONEL)
    stat_refs["sistem"] = create_stat_card(3, "Sistem", CLR_SISTEM)
    stat_refs["mekan"] = create_stat_card(4, "Fiziksel Mekan", CLR_MEKAN)

    charts_row = ctk.CTkFrame(dash_f, fg_color="transparent")
    charts_row.pack(fill="both", expand=True, pady=20)
    charts_row.columnconfigure((0, 1), weight=1)
    charts_row.rowconfigure(0, weight=1)

    def create_usage_chart(col):
        box = ctk.CTkFrame(charts_row, fg_color=CLR_CARD, corner_radius=20)
        box.grid(row=0, column=col, padx=10, sticky="nsew")
        ctk.CTkLabel(box, text="Varlık Atama Durumu", font=("Segoe UI", 20, "bold"), text_color=CLR_TEXT).pack(pady=(30, 10))
        cv = tk.Canvas(box, width=300, height=300, bg=CLR_CARD, highlightthickness=0)
        cv.pack(expand=True)
        cv.create_arc(40, 40, 260, 260, start=0, extent=359.9, outline="#E5E7EB", width=35, style=tk.ARC)
        arc_aktif = cv.create_arc(40, 40, 260, 260, start=90, extent=0, outline=CLR_DONANIM, width=35, style=tk.ARC)
        arc_bosta = cv.create_arc(40, 40, 260, 260, start=90, extent=0, outline=CLR_YAZILIM, width=35, style=tk.ARC)
        center_f = ctk.CTkFrame(box, fg_color="transparent")
        center_f.place(relx=0.5, rely=0.48, anchor="center")
        ctk.CTkLabel(center_f, text="TOPLAM", font=("Segoe UI", 14, "bold"), text_color=CLR_TEXT_LIGHT).pack()
        txt_bottom = ctk.CTkLabel(center_f, text="0 Kayıt", font=("Segoe UI", 20, "bold"), text_color=CLR_TEXT)
        txt_bottom.pack()
        legend_f = ctk.CTkFrame(box, fg_color="transparent")
        legend_f.pack(pady=(10, 30))
        def add_leg_grid(parent, row, col, color, title):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.grid(row=row, column=col, padx=15, pady=5, sticky="w")
            ctk.CTkFrame(f, width=14, height=14, fg_color=color, corner_radius=7).grid(row=0, column=0)
            lbl = ctk.CTkLabel(f, text=title, font=("Segoe UI", 13, "bold"), text_color=CLR_TEXT)
            lbl.grid(row=0, column=1, padx=(8, 0))
            return lbl
        lbl_aktif = add_leg_grid(legend_f, 0, 0, CLR_DONANIM, "Zimmetli: 0 (%0)")
        lbl_bosta = add_leg_grid(legend_f, 0, 1, CLR_YAZILIM, "Boşta: 0 (%0)")
        return cv, arc_aktif, arc_bosta, txt_bottom, lbl_aktif, lbl_bosta

    def create_dist_chart(col):
        box = ctk.CTkFrame(charts_row, fg_color=CLR_CARD, corner_radius=20)
        box.grid(row=0, column=col, padx=10, sticky="nsew")
        ctk.CTkLabel(box, text="Genel Envanter Dağılımı", font=("Segoe UI", 20, "bold"), text_color=CLR_TEXT).pack(pady=(30, 10))
        cv = tk.Canvas(box, width=300, height=300, bg=CLR_CARD, highlightthickness=0)
        cv.pack(expand=True)
        cv.create_arc(40, 40, 260, 260, start=0, extent=359.9, outline="#E5E7EB", width=35, style=tk.ARC)
        arc_donanim = cv.create_arc(40, 40, 260, 260, start=90, extent=0, outline=CLR_DONANIM, width=35, style=tk.ARC)
        arc_yazilim = cv.create_arc(40, 40, 260, 260, start=90, extent=0, outline=CLR_YAZILIM, width=35, style=tk.ARC)
        arc_personel = cv.create_arc(40, 40, 260, 260, start=90, extent=0, outline=CLR_PERSONEL, width=35, style=tk.ARC)
        arc_sistem = cv.create_arc(40, 40, 260, 260, start=90, extent=0, outline=CLR_SISTEM, width=35, style=tk.ARC)
        arc_mekan = cv.create_arc(40, 40, 260, 260, start=90, extent=0, outline=CLR_MEKAN, width=35, style=tk.ARC)
        center_f = ctk.CTkFrame(box, fg_color="transparent")
        center_f.place(relx=0.5, rely=0.48, anchor="center")
        ctk.CTkLabel(center_f, text="ENVANTER", font=("Segoe UI", 14, "bold"), text_color=CLR_TEXT_LIGHT).pack()
        txt_bottom = ctk.CTkLabel(center_f, text="0 Birim", font=("Segoe UI", 20, "bold"), text_color=CLR_TEXT)
        txt_bottom.pack()
        legend_f = ctk.CTkFrame(box, fg_color="transparent")
        legend_f.pack(pady=(10, 30))
        def add_leg_dist_grid(parent, row, col, color):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.grid(row=row, column=col, padx=12, pady=5, sticky="w")
            ctk.CTkFrame(f, width=12, height=12, fg_color=color, corner_radius=6).grid(row=0, column=0)
            lbl = ctk.CTkLabel(f, text="", font=("Segoe UI", 12, "bold"), text_color=CLR_TEXT)
            lbl.grid(row=0, column=1, padx=(6, 0))
            return lbl
        lbl_d = add_leg_dist_grid(legend_f, 0, 0, CLR_DONANIM)
        lbl_y = add_leg_dist_grid(legend_f, 0, 1, CLR_YAZILIM)
        lbl_p = add_leg_dist_grid(legend_f, 0, 2, CLR_PERSONEL)
        lbl_s = add_leg_dist_grid(legend_f, 1, 0, CLR_SISTEM)
        lbl_m = add_leg_dist_grid(legend_f, 1, 1, CLR_MEKAN)
        return cv, arc_donanim, arc_yazilim, arc_personel, arc_sistem, arc_mekan, txt_bottom, lbl_d, lbl_y, lbl_p, lbl_s, lbl_m

    cv1, arc1_aktif, arc1_bosta, txt_c1, lbl_aktif, lbl_bosta = create_usage_chart(0)
    cv2, arc2_donanim, arc2_yazilim, arc2_personel, arc2_sistem, arc2_mekan, txt_c2, lbl_d, lbl_y, lbl_p, lbl_s, lbl_m = create_dist_chart(1)

    def live_engine():
        if not new_window.winfo_exists(): return
        try:
            db = sqlite3.connect("envanter.db"); cursor = db.cursor()
            queries = {"donanim": "SELECT COUNT(*) FROM donanim", "yazilim": "SELECT COUNT(*) FROM yazilim", "personel": "SELECT COUNT(*) FROM personel", "sistem": "SELECT COUNT(*) FROM sistem", "mekan": "SELECT COUNT(*) FROM fiziksel_mekan"}
            for k, sql in queries.items():
                cursor.execute(sql); stat_refs[k].configure(text=str(cursor.fetchone()[0]))

            cursor.execute("SELECT varlik_sahibi FROM donanim"); d_sahipler = cursor.fetchall()
            cursor.execute("SELECT varlik_sahibi FROM yazilim"); y_sahipler = cursor.fetchall()
            tum_varliklar = d_sahipler + y_sahipler

            aktif_count = sum(1 for r in tum_varliklar if r[0] and str(r[0]).strip() not in ["", "Boşta", "None"])
            bosta_count = len(tum_varliklar) - aktif_count
            total1 = aktif_count + bosta_count
            txt_c1.configure(text=f"{total1} Kayıt")
            if total1 > 0:
                pct_aktif = (aktif_count / total1) * 100; pct_bosta = (bosta_count / total1) * 100
                lbl_aktif.configure(text=f"Zimmetli: {aktif_count} (%{pct_aktif:.1f})")
                lbl_bosta.configure(text=f"Boşta: {bosta_count} (%{pct_bosta:.1f})")
                ang_aktif = (aktif_count / total1) * 360; ang_bosta = (bosta_count / total1) * 360
                if ang_aktif >= 360: ang_aktif = 359.99
                if ang_bosta >= 360: ang_bosta = 359.99
                cv1.itemconfig(arc1_aktif, start=90, extent=ang_aktif); cv1.itemconfig(arc1_bosta, start=90 + ang_aktif, extent=ang_bosta)
            else:
                lbl_aktif.configure(text="Zimmetli: 0 (%0)"); lbl_bosta.configure(text="Boşta: 0 (%0)")
                cv1.itemconfig(arc1_aktif, extent=0); cv1.itemconfig(arc1_bosta, extent=0)

            d_count = len(d_sahipler); y_count = len(y_sahipler)
            cursor.execute("SELECT COUNT(*) FROM personel"); p_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM sistem"); s_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM fiziksel_mekan"); m_count = cursor.fetchone()[0]
            total2 = d_count + y_count + p_count + s_count + m_count
            txt_c2.configure(text=f"{total2} Birim")

            if total2 > 0:
                pct_d = (d_count / total2) * 100; pct_y = (y_count / total2) * 100; pct_p = (p_count / total2) * 100
                pct_s = (s_count / total2) * 100; pct_m = (m_count / total2) * 100
                lbl_d.configure(text=f"DN: {d_count} (%{pct_d:.1f})"); lbl_y.configure(text=f"YZLM: {y_count} (%{pct_y:.1f})")
                lbl_p.configure(text=f"PRSN: {p_count} (%{pct_p:.1f})"); lbl_s.configure(text=f"SİS: {s_count} (%{pct_s:.1f})")
                lbl_m.configure(text=f"FM: {m_count} (%{pct_m:.1f})")
                a1 = (d_count / total2) * 360; a2 = (y_count / total2) * 360; a3 = (p_count / total2) * 360; a4 = (s_count / total2) * 360; a5 = (m_count / total2) * 360
                if a1 >= 360: a1 = 359.99
                if a2 >= 360: a2 = 359.99
                if a3 >= 360: a3 = 359.99
                if a4 >= 360: a4 = 359.99
                if a5 >= 360: a5 = 359.99
                cv2.itemconfig(arc2_donanim, start=90, extent=a1); cv2.itemconfig(arc2_yazilim, start=90 + a1, extent=a2)
                cv2.itemconfig(arc2_personel, start=90 + a1 + a2, extent=a3); cv2.itemconfig(arc2_sistem, start=90 + a1 + a2 + a3, extent=a4)
                cv2.itemconfig(arc2_mekan, start=90 + a1 + a2 + a3 + a4, extent=a5)
            else:
                lbl_d.configure(text="DN: 0 (%0)"); lbl_y.configure(text="YZLM: 0 (%0)"); lbl_p.configure(text="PRSN: 0 (%0)")
                lbl_s.configure(text="SİS: 0 (%0)"); lbl_m.configure(text="FM: 0 (%0)")
                cv2.itemconfig(arc2_donanim, extent=0); cv2.itemconfig(arc2_yazilim, extent=0); cv2.itemconfig(arc2_personel, extent=0)
                cv2.itemconfig(arc2_sistem, extent=0); cv2.itemconfig(arc2_mekan, extent=0)
            db.close()
        except Exception: pass
        new_window.after(1000, live_engine)

    live_engine()

    try:
        Donanım.build_ui(frames["Donanım"])
        Yazılım.build_ui(frames["Yazılım"])
        Personel.build_ui(frames["Personel"])
        Sistem.build_ui(frames["Sistem"])
        Fiziksel_Mekan.build_ui(frames["Mekan"])
    except Exception as e:
        messagebox.showerror("Arayüz Hatası", f"Modüller yüklenirken hata oluştu:\n{e}", parent=new_window)

    show_frame("Dashboard")