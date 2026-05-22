import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import veritabani
import pandas as pd


def build_ui(new_window):
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Asset.Treeview", background="#FFFFFF", foreground="#0F172A", rowheight=35,
                    fieldbackground="#FFFFFF", borderwidth=0, font=("Segoe UI", 11))
    style.map('Asset.Treeview', background=[('selected', '#4318FF')], foreground=[('selected', 'white')])
    style.configure("Asset.Treeview.Heading", background="#F8FAFC", foreground="#334155", font=("Segoe UI", 12, "bold"),
                    borderwidth=0, padding=5)

    style.configure("TCombobox", fieldbackground="#F8FAFC", background="#FFFFFF", foreground="#0F172A",
                    bordercolor="#CBD5E1", arrowcolor="#4318FF", padding=4)
    style.map("TCombobox", fieldbackground=[("readonly", "#F8FAFC")], selectbackground=[("readonly", "#4318FF")],
              selectforeground=[("readonly", "#FFFFFF")], bordercolor=[("focus", "#4318FF")])

    def temizle():
        combo_varlik_grubu.set('')
        entry_varlik_kodu.configure(state="normal")
        entry_varlik_kodu.delete(0, tk.END)
        entry_varlik_kodu.insert(0, veritabani.siradaki_kodu_getir("donanim", "DN"))
        entry_varlik_kodu.configure(state="readonly")
        for e in (entry_donanim_adi, entry_donanim_tipi, entry_seri_no, entry_marka, entry_model, entry_ara): e.delete(
            0, tk.END)
        entry_stok.delete(0, tk.END);
        entry_stok.insert(0, "1")
        combo_departman.set('');
        combo_sahip.set('')
        kayitlari_getir()

    def kayitlari_getir(aranan_metin=""):
        for row in tablo.get_children(): tablo.delete(row)
        baglanti = sqlite3.connect("envanter.db")
        imlec = baglanti.cursor()
        sorgu = "SELECT * FROM donanim WHERE 1=1"
        parametreler = []
        if aranan_metin != "":
            sorgu += " AND (varlik_grubu LIKE ? OR varlik_kodu LIKE ? OR donanim_adi LIKE ? OR donanim_tipi LIKE ? OR seri_no LIKE ? OR marka LIKE ? OR model LIKE ? OR departman LIKE ? OR varlik_sahibi LIKE ?)"
            parametreler.extend(['%' + aranan_metin + '%'] * 9)
        imlec.execute(sorgu, parametreler)
        for index, satir in enumerate(imlec.fetchall(), start=1): tablo.insert("", tk.END, values=(index,) + satir[1:])
        baglanti.close()

    def ekle():
        # Varlık Sahibi (combo_sahip) kontrol listesinden çıkarıldı
        gerekli_alanlar = [combo_varlik_grubu.get().strip(), entry_donanim_adi.get().strip(),
                           entry_donanim_tipi.get().strip(), entry_seri_no.get().strip(), entry_marka.get().strip(),
                           entry_model.get().strip(), entry_stok.get().strip(), combo_departman.get().strip()]

        if not all(gerekli_alanlar):
            messagebox.showwarning("Eksik Veri", "Lütfen Varlık Sahibi hariç tüm kutucukları eksiksiz doldurun!")
            return

        sahip = combo_sahip.get().strip()
        if not sahip: sahip = "Boşta"  # Eğer seçilmediyse otomatik Boşta yazdır

        baglanti = sqlite3.connect("envanter.db");
        imlec = baglanti.cursor()
        # ... (Kayıt kodları aynı)
        imlec.execute("SELECT * FROM donanim WHERE seri_no=?", (entry_seri_no.get().strip(),))
        if imlec.fetchone(): messagebox.showerror("Hata", "Bu Seri Numarası kullanımda!"); baglanti.close(); return
        imlec.execute("INSERT OR IGNORE INTO departmanlar (ad) VALUES (?)", (combo_departman.get().strip(),))
        imlec.execute(
            "INSERT INTO donanim (varlik_grubu, varlik_kodu, donanim_adi, donanim_tipi, seri_no, marka, model, stok_durumu, departman, varlik_sahibi) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (combo_varlik_grubu.get(), entry_varlik_kodu.get(), entry_donanim_adi.get(), entry_donanim_tipi.get(),
             entry_seri_no.get(), entry_marka.get(), entry_model.get(), entry_stok.get(), combo_departman.get(),
             combo_sahip.get().strip()))
        baglanti.commit();
        baglanti.close();
        messagebox.showinfo("Başarılı", "Donanım eklendi.");
        temizle()

    def tablo_tiklandi(event):
        secilen = tablo.focus();
        degerler = tablo.item(secilen, "values")
        if degerler:
            combo_varlik_grubu.set(degerler[1])
            entry_varlik_kodu.configure(state="normal");
            entry_varlik_kodu.delete(0, tk.END);
            entry_varlik_kodu.insert(0, degerler[2]);
            entry_varlik_kodu.configure(state="readonly")
            for i, ent in enumerate(
                    (entry_donanim_adi, entry_donanim_tipi, entry_seri_no, entry_marka, entry_model, entry_stok),
                    start=3):
                ent.delete(0, tk.END);
                ent.insert(0, degerler[i])
            combo_departman.set(degerler[9]);
            combo_sahip.set(degerler[10])

    def sil():
        if not tablo.focus(): return
        if messagebox.askyesno("Onay", "Kayıt silinsin mi?"):
            baglanti = sqlite3.connect("envanter.db")
            baglanti.cursor().execute("DELETE FROM donanim WHERE varlik_kodu=?",
                                      (tablo.item(tablo.focus(), "values")[2],))
            baglanti.commit();
            baglanti.close();
            temizle()

    def guncelle():
        secilen = tablo.focus();
        degerler = tablo.item(secilen, "values")
        if not degerler: return

        # 🛑 VARLIK SAHİBİ DE ZORUNLU ALANLARA EKLENDİ 🛑
        gerekli_alanlar = [combo_varlik_grubu.get().strip(), entry_donanim_adi.get().strip(),
                           entry_donanim_tipi.get().strip(), entry_seri_no.get().strip(), entry_marka.get().strip(),
                           entry_model.get().strip(), entry_stok.get().strip(), combo_departman.get().strip(),
                           combo_sahip.get().strip()]
        if not all(gerekli_alanlar):
            messagebox.showwarning("Eksik Veri", "Lütfen tüm kutucukları eksiksiz doldurun!")
            return

        baglanti = sqlite3.connect("envanter.db");
        imlec = baglanti.cursor()
        imlec.execute("SELECT varlik_kodu FROM donanim WHERE seri_no=?", (entry_seri_no.get().strip(),))
        sonuc = imlec.fetchone()
        if sonuc and sonuc[0] != degerler[2]: messagebox.showerror("Hata",
                                                                   "Seri no başka cihaza ait!"); baglanti.close(); return
        imlec.execute("INSERT OR IGNORE INTO departmanlar (ad) VALUES (?)", (combo_departman.get().strip(),))
        imlec.execute(
            "UPDATE donanim SET varlik_grubu=?, donanim_adi=?, donanim_tipi=?, seri_no=?, marka=?, model=?, stok_durumu=?, departman=?, varlik_sahibi=? WHERE varlik_kodu=?",
            (combo_varlik_grubu.get(), entry_donanim_adi.get(), entry_donanim_tipi.get(), entry_seri_no.get(),
             entry_marka.get(), entry_model.get(), entry_stok.get(), combo_departman.get(), combo_sahip.get().strip(),
             degerler[2]))
        baglanti.commit();
        baglanti.close();
        messagebox.showinfo("Başarılı", "Güncellendi.");
        temizle()

    def ara():
        kayitlari_getir(entry_ara.get().strip())

    def excel_disa_aktar():
        baglanti = sqlite3.connect("envanter.db");
        df = pd.read_sql_query("SELECT * FROM donanim", baglanti);
        baglanti.close()
        dosya = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if dosya: df.to_excel(dosya, index=False); messagebox.showinfo("Başarılı", "Aktarıldı.")

    def excel_ice_aktar():
        dosya = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if not dosya: return
        try:
            df = pd.read_excel(dosya);
            baglanti = sqlite3.connect("envanter.db");
            imlec = baglanti.cursor()
            for _, row in df.iterrows():
                sahip = str(row.get("Varlık Sahibi", "")).strip()
                imlec.execute("INSERT OR IGNORE INTO departmanlar (ad) VALUES (?)", (str(row.get("Departman", "")),))
                imlec.execute(
                    "INSERT INTO donanim (varlik_grubu, varlik_kodu, donanim_adi, donanim_tipi, seri_no, marka, model, stok_durumu, departman, varlik_sahibi) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (str(row.get("Varlık Grubu", "")), str(row.get("Varlık Kodu", "")), str(row.get("Donanım Adı", "")),
                     str(row.get("Donanım Tipi", "")), str(row.get("Seri No", "")), str(row.get("Marka", "")),
                     str(row.get("Model", "")), str(row.get("Stok Durumu", "")), str(row.get("Departman", "")), sahip))
            baglanti.commit();
            baglanti.close();
            messagebox.showinfo("Başarılı", "Yüklendi.");
            temizle()
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    ctk.CTkLabel(new_window, text="Donanım", font=("Segoe UI", 24, "bold"), text_color="#1E293B").pack(
        anchor="w", pady=(0, 5))

    frame_kontrol = ctk.CTkFrame(new_window, fg_color="#FFFFFF", corner_radius=10);
    frame_kontrol.pack(pady=5, fill="x")
    inner_kontrol = ctk.CTkFrame(frame_kontrol, fg_color="transparent");
    inner_kontrol.pack(padx=20, pady=10, fill="x")

    ctk.CTkButton(inner_kontrol, text="EKLE", command=ekle, fg_color="#05CD99", hover_color="#04A37A",
                  font=("Segoe UI", 12, "bold"), width=110, height=35, corner_radius=6).pack(side="left", padx=4)
    ctk.CTkButton(inner_kontrol, text="SİL", command=sil, fg_color="#EE5D50", hover_color="#C64A3F",
                  font=("Segoe UI", 12, "bold"), width=110, height=35, corner_radius=6).pack(side="left", padx=4)
    ctk.CTkButton(inner_kontrol, text="TEMİZLE", command=temizle, fg_color="#A3AED0", hover_color="#8F9BBA",
                  font=("Segoe UI", 12, "bold"), width=110, height=35, corner_radius=6).pack(side="left", padx=4)
    ctk.CTkButton(inner_kontrol, text="GÜNCELLE", command=guncelle, fg_color="#FFCE20", hover_color="#D1A715",
                  text_color="#2B3674", font=("Segoe UI", 12, "bold"), width=110, height=35, corner_radius=6).pack(
        side="left", padx=4)

    entry_ara = ctk.CTkEntry(inner_kontrol, width=220, height=35, font=("Segoe UI", 12), fg_color="#F8FAFC",
                             border_width=1, border_color="#CBD5E1", text_color="#0F172A",
                             placeholder_text="Arama yap...", corner_radius=6)
    entry_ara.pack(side="left", padx=(20, 8))
    ctk.CTkButton(inner_kontrol, text="ARA", command=ara, fg_color="#4318FF", hover_color="#3311CC",
                  font=("Segoe UI", 12, "bold"), width=90, height=35, corner_radius=6).pack(side="left", padx=4)

    frame_excel = ctk.CTkFrame(inner_kontrol, fg_color="transparent");
    frame_excel.pack(side="right", padx=5)
    ctk.CTkButton(frame_excel, text="EXCEL'E AKTAR", command=excel_disa_aktar, fg_color="#10B981",
                  hover_color="#059669", font=("Segoe UI", 11, "bold"), width=130, height=22, corner_radius=4).pack(
        side="top", pady=(0, 2), fill="x")
    ctk.CTkButton(frame_excel, text="EXCEL'DEN YÜKLE", command=excel_ice_aktar, fg_color="#34D399",
                  hover_color="#10B981", font=("Segoe UI", 11, "bold"), width=130, height=22, corner_radius=4).pack(
        side="top", pady=(0, 0), fill="x")

    form_frame = ctk.CTkFrame(new_window, fg_color="#FFFFFF", corner_radius=10);
    form_frame.pack(fill="x", pady=5)
    inner_form = ctk.CTkFrame(form_frame, fg_color="transparent");
    inner_form.pack(padx=20, pady=5)  # 🛑 PADY İYİCE DARALTILDI 🛑

    lbl_font = ("Segoe UI", 12, "bold");
    ent_font = ("Segoe UI", 12);
    lbl_color = "#334155";
    ent_color = "#0F172A";
    ent_bg = "#F8FAFC";
    ent_border = "#CBD5E1"

    # 🛑 YÜKSEKLİKLER (HEIGHT) 30 YAPILDI, PADY 4 YAPILDI 🛑
    ctk.CTkLabel(inner_form, text="Varlık Grubu:", font=lbl_font, text_color=lbl_color, width=110, anchor="w").grid(
        row=0, column=0, padx=8, pady=4)
    combo_varlik_grubu = ttk.Combobox(inner_form, width=28, state="readonly", font=ent_font)
    combo_varlik_grubu.grid(row=0, column=1, padx=8, pady=4, ipady=2)
    combo_varlik_grubu.configure(
        postcommand=lambda: combo_varlik_grubu.configure(values=veritabani.varlik_gruplarini_getir()))

    ctk.CTkLabel(inner_form, text="Varlık Kodu:", font=lbl_font, text_color=lbl_color, width=110, anchor="w").grid(
        row=0, column=2, padx=8, pady=4)
    entry_varlik_kodu = ctk.CTkEntry(inner_form, width=280, height=30, font=ent_font, fg_color=ent_bg,
                                     border_color=ent_border, border_width=1, text_color=ent_color)
    entry_varlik_kodu.grid(row=0, column=3, padx=8, pady=4);
    entry_varlik_kodu.insert(0, veritabani.siradaki_kodu_getir("donanim", "DN"));
    entry_varlik_kodu.configure(state="readonly")

    ctk.CTkLabel(inner_form, text="Donanım Adı:", font=lbl_font, text_color=lbl_color, width=110, anchor="w").grid(
        row=1, column=0, padx=8, pady=4)
    entry_donanim_adi = ctk.CTkEntry(inner_form, width=280, height=30, font=ent_font, fg_color=ent_bg,
                                     border_color=ent_border, border_width=1, text_color=ent_color)
    entry_donanim_adi.grid(row=1, column=1, padx=8, pady=4)

    ctk.CTkLabel(inner_form, text="Donanım Tipi:", font=lbl_font, text_color=lbl_color, width=110, anchor="w").grid(
        row=1, column=2, padx=8, pady=4)
    entry_donanim_tipi = ctk.CTkEntry(inner_form, width=280, height=30, font=ent_font, fg_color=ent_bg,
                                      border_color=ent_border, border_width=1, text_color=ent_color)
    entry_donanim_tipi.grid(row=1, column=3, padx=8, pady=4)

    ctk.CTkLabel(inner_form, text="Seri No:", font=lbl_font, text_color=lbl_color, width=110, anchor="w").grid(row=2,
                                                                                                               column=0,
                                                                                                               padx=8,
                                                                                                               pady=4)
    entry_seri_no = ctk.CTkEntry(inner_form, width=280, height=30, font=ent_font, fg_color=ent_bg,
                                 border_color=ent_border, border_width=1, text_color=ent_color)
    entry_seri_no.grid(row=2, column=1, padx=8, pady=4)

    ctk.CTkLabel(inner_form, text="Marka:", font=lbl_font, text_color=lbl_color, width=110, anchor="w").grid(row=2,
                                                                                                             column=2,
                                                                                                             padx=8,
                                                                                                             pady=4)
    entry_marka = ctk.CTkEntry(inner_form, width=280, height=30, font=ent_font, fg_color=ent_bg,
                               border_color=ent_border, border_width=1, text_color=ent_color)
    entry_marka.grid(row=2, column=3, padx=8, pady=4)

    ctk.CTkLabel(inner_form, text="Model:", font=lbl_font, text_color=lbl_color, width=110, anchor="w").grid(row=3,
                                                                                                             column=0,
                                                                                                             padx=8,
                                                                                                             pady=4)
    entry_model = ctk.CTkEntry(inner_form, width=280, height=30, font=ent_font, fg_color=ent_bg,
                               border_color=ent_border, border_width=1, text_color=ent_color)
    entry_model.grid(row=3, column=1, padx=8, pady=4)

    ctk.CTkLabel(inner_form, text="Stok Miktarı:", font=lbl_font, text_color=lbl_color, width=110, anchor="w").grid(
        row=3, column=2, padx=8, pady=4)
    entry_stok = ctk.CTkEntry(inner_form, width=280, height=30, font=ent_font, fg_color=ent_bg, border_color=ent_border,
                              border_width=1, text_color=ent_color)
    entry_stok.grid(row=3, column=3, padx=8, pady=4);
    entry_stok.insert(0, "1")

    ctk.CTkLabel(inner_form, text="Departman:", font=lbl_font, text_color=lbl_color, width=110, anchor="w").grid(row=4,
                                                                                                                 column=0,
                                                                                                                 padx=8,
                                                                                                                 pady=4)
    combo_departman = ttk.Combobox(inner_form, width=28, state="readonly", font=ent_font)
    combo_departman.grid(row=4, column=1, padx=8, pady=4, ipady=2)
    combo_departman.configure(postcommand=lambda: combo_departman.configure(values=veritabani.departmanlari_getir()))

    ctk.CTkLabel(inner_form, text="Varlık Sahibi:", font=lbl_font, text_color=lbl_color, width=110, anchor="w").grid(
        row=4, column=2, padx=8, pady=4)
    combo_sahip = ttk.Combobox(inner_form, width=28, state="readonly", font=ent_font)
    combo_sahip.grid(row=4, column=3, padx=8, pady=4, ipady=2)
    combo_sahip.configure(postcommand=lambda: combo_sahip.configure(values=veritabani.personelleri_getir()))

    frame_tablo = ctk.CTkFrame(new_window, fg_color="#FFFFFF", corner_radius=10)
    frame_tablo.pack(pady=5, fill="both", expand=True)

    sutunlar = ("ID", "Varlık Grubu", "Varlık Kodu", "Donanım Adı", "Donanım Tipi", "Seri No", "Marka", "Model",
                "Stok Durumu", "Departman", "Varlık Sahibi")
    genislikler = {"ID": 40, "Varlık Grubu": 160, "Varlık Kodu": 80, "Donanım Adı": 140, "Donanım Tipi": 120,
                   "Seri No": 100, "Marka": 100, "Model": 100, "Stok Durumu": 80, "Departman": 120,
                   "Varlık Sahibi": 130}

    tablo = ttk.Treeview(frame_tablo, columns=sutunlar, show="headings", style="Asset.Treeview")
    for sutun in sutunlar:
        tablo.heading(sutun, text=sutun)
        tablo.column(sutun, width=genislikler.get(sutun, 100), anchor="center")

    tablo.bind("<ButtonRelease-1>", tablo_tiklandi)
    scrollbar = ttk.Scrollbar(frame_tablo, orient=tk.VERTICAL, command=tablo.yview)
    tablo.configure(yscroll=scrollbar.set);
    scrollbar.pack(side="right", fill="y");
    tablo.pack(fill="both", expand=True, padx=10, pady=10)

    kayitlari_getir()