import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import veritabani


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
        entry_varlik_kodu.configure(state="normal");
        entry_varlik_kodu.delete(0, tk.END);
        entry_varlik_kodu.insert(0, veritabani.siradaki_kodu_getir("fiziksel_mekan", "FM"));
        entry_varlik_kodu.configure(state="readonly")
        combo_departman.set('');
        combo_sorumlu.set('')
        kayitlari_getir()

    def kayitlari_getir(aranan_metin=""):
        for row in tablo.get_children(): tablo.delete(row)
        baglanti = sqlite3.connect("envanter.db");
        imlec = baglanti.cursor()
        sorgu = "SELECT * FROM fiziksel_mekan WHERE 1=1";
        parametreler = []
        if aranan_metin != "":
            sorgu += " AND (varlik_grubu LIKE ? OR varlik_kodu LIKE ? OR departman LIKE ? OR sorumlu LIKE ?)"
            parametreler.extend(['%' + aranan_metin + '%'] * 4)
        imlec.execute(sorgu, parametreler)
        for index, satir in enumerate(imlec.fetchall(), start=1): tablo.insert("", tk.END, values=(index,) + satir[1:])
        baglanti.close()

    def ekle():
        gerekli_alanlar = [combo_varlik_grubu.get().strip(), combo_departman.get().strip(), combo_sorumlu.get().strip()]
        if not all(gerekli_alanlar): messagebox.showwarning("Eksik Veri",
                                                            "Lütfen tüm kutucukları eksiksiz doldurun!"); return
        baglanti = sqlite3.connect("envanter.db")
        baglanti.cursor().execute("INSERT OR IGNORE INTO departmanlar (ad) VALUES (?)",
                                  (combo_departman.get().strip(),))
        baglanti.cursor().execute(
            "INSERT INTO fiziksel_mekan (varlik_grubu, varlik_kodu, departman, sorumlu) VALUES (?, ?, ?, ?)",
            (combo_varlik_grubu.get(), entry_varlik_kodu.get(), combo_departman.get(), combo_sorumlu.get()))
        baglanti.commit();
        baglanti.close();
        messagebox.showinfo("Başarılı", "Mekan sisteme kaydedildi.");
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
            combo_departman.set(degerler[3]);
            combo_sorumlu.set(degerler[4])

    def sil():
        if not tablo.focus(): return
        if messagebox.askyesno("Onay", "Mekanı silmek istediğinize emin misiniz?"):
            baglanti = sqlite3.connect("envanter.db");
            baglanti.cursor().execute("DELETE FROM fiziksel_mekan WHERE varlik_kodu=?",
                                      (tablo.item(tablo.focus(), "values")[2],))
            baglanti.commit();
            baglanti.close();
            temizle()

    def guncelle():
        secilen = tablo.focus();
        degerler = tablo.item(secilen, "values")
        if not degerler: return
        gerekli_alanlar = [combo_varlik_grubu.get().strip(), combo_departman.get().strip(), combo_sorumlu.get().strip()]
        if not all(gerekli_alanlar): messagebox.showwarning("Eksik Veri",
                                                            "Lütfen tüm kutucukları eksiksiz doldurun!"); return
        baglanti = sqlite3.connect("envanter.db")
        baglanti.cursor().execute("INSERT OR IGNORE INTO departmanlar (ad) VALUES (?)",
                                  (combo_departman.get().strip(),))
        baglanti.cursor().execute(
            "UPDATE fiziksel_mekan SET varlik_grubu=?, departman=?, sorumlu=? WHERE varlik_kodu=?",
            (combo_varlik_grubu.get(), combo_departman.get(), combo_sorumlu.get(), degerler[2]))
        baglanti.commit();
        baglanti.close();
        messagebox.showinfo("Başarılı", "Kayıt güncellendi.");
        temizle()

    def ara():
        kayitlari_getir(entry_ara.get().strip())

    ctk.CTkLabel(new_window, text="Fiziksel Mekan", font=("Segoe UI", 24, "bold"), text_color="#1E293B").pack(
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

    form_frame = ctk.CTkFrame(new_window, fg_color="#FFFFFF", corner_radius=10);
    form_frame.pack(fill="x", pady=5)
    inner_form = ctk.CTkFrame(form_frame, fg_color="transparent");
    inner_form.pack(padx=20, pady=5)

    lbl_font = ("Segoe UI", 12, "bold");
    ent_font = ("Segoe UI", 12);
    lbl_color = "#334155";
    ent_color = "#0F172A";
    ent_bg = "#F8FAFC";
    ent_border = "#CBD5E1"

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
    entry_varlik_kodu.insert(0, veritabani.siradaki_kodu_getir("fiziksel_mekan", "FM"));
    entry_varlik_kodu.configure(state="readonly")

    ctk.CTkLabel(inner_form, text="Departman:", font=lbl_font, text_color=lbl_color, width=110, anchor="w").grid(row=1,
                                                                                                                 column=0,
                                                                                                                 padx=8,
                                                                                                                 pady=4)
    combo_departman = ttk.Combobox(inner_form, width=28, state="readonly", font=ent_font)
    combo_departman.grid(row=1, column=1, padx=8, pady=4, ipady=2)
    combo_departman.configure(postcommand=lambda: combo_departman.configure(values=veritabani.departmanlari_getir()))

    ctk.CTkLabel(inner_form, text="Sorumlu:", font=lbl_font, text_color=lbl_color, width=110, anchor="w").grid(row=1,
                                                                                                               column=2,
                                                                                                               padx=8,
                                                                                                               pady=4)
    combo_sorumlu = ttk.Combobox(inner_form, width=28, state="readonly", font=ent_font)
    combo_sorumlu.grid(row=1, column=3, padx=8, pady=4, ipady=2)
    combo_sorumlu.configure(postcommand=lambda: combo_sorumlu.configure(values=veritabani.personelleri_getir()))

    frame_tablo = ctk.CTkFrame(new_window, fg_color="#FFFFFF", corner_radius=10)
    frame_tablo.pack(pady=5, fill="both", expand=True)

    sutunlar = ("ID", "Varlık Grubu", "Varlık Kodu", "Departman", "Sorumlu")
    genislikler = {"ID": 40, "Varlık Grubu": 180, "Varlık Kodu": 80, "Departman": 160, "Sorumlu": 160}

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