# Laporan Praktikum Aplikasi Website (Modul 3 dan 4)
Topik: Visualisasi Interaktif dan Analitik Data Keuangan Perusahaan (company_data.csv) menggunakan Streamlit.

## Struktur Direktori
laprak_p2/
company_data.csv: Dataset mentah (1.000 data perusahaan)
company_data_clean.csv: Dataset bersih hasil pra-pemrosesan
preprocessing_dan_eksplorasi.ipynb: Jupyter Notebook pra-pemrosesan dan EDA
app.py: Aplikasi Web Dashboard Interaktif Streamlit
requirements.txt: Daftar dependensi aplikasi

## Konsep Praktikum yang Diimplementasikan

### 1. Data Preprocessing dan Exploratory Data Analysis (EDA)
Terdapat pada preprocessing_dan_eksplorasi.ipynb:
Pembersihan nama kolom (lowercase) dan pengecekan missing value serta duplikat.
Feature Engineering:
profit_margin: (profit / revenue) * 100
rev_per_employee: Produktivitas pendapatan per karyawan
valuation_status: Klasifikasi P/E ratio (Undervalued, Fair Value, Overvalued)
company_size: Skala perusahaan berdasarkan jumlah karyawan (Small, Medium, Large, Enterprise)
Visualisasi awal menggunakan matplotlib dan seaborn.

### 2. Implementasi Konsep Modul 3
Caching (st.cache_data): Memastikan dataset hanya dibaca dan diproses sekali di memori.
Progress Bar dan Status Widgets (st.progress, st.spinner, st.empty, st.toast, st.balloons).
Multi-view Layout (Tabs Navigation):
1. Ikhtisar dan Distribusi
2. Analisis Valuasi dan Performa
3. Kalkulator dan Callback Form
4. Data Mentah dan Ekspor
Session State dan Callbacks:
Reset filter callback menggunakan st.session_state dan on_click.
Formulir simulasi investasi interaktif menggunakan st.form dan submit callback.

### 3. Implementasi Konsep Modul 4
Normalisasi kolom dengan lambda function.
Histogram distribusi menggunakan np.histogram dan st.bar_chart().
Filter interaktif dengan st.slider(), st.multiselect(), dan st.checkbox().
Tampilan raw data dinamis dan unduh data hasil filter (.csv).

## Cara Menjalankan Aplikasi
Buka terminal dan jalankan:
py -m streamlit run laprak_p2/app.py
