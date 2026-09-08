import os
import time
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Dashboard Analitik Perusahaan",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

current_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_dir, "company_data.csv")
if not os.path.exists(data_path):
    data_path = "company_data.csv"

@st.cache_data(show_spinner=False)
def load_and_preprocess_data(filepath):
    df = pd.read_csv(filepath)
    df.columns = [col.strip().lower() for col in df.columns]
    
    float_cols = ['price', 'pe_ratio', 'revenue', 'profit']
    df[float_cols] = df[float_cols].round(2)
    
    df['profit_margin'] = ((df['profit'] / df['revenue']) * 100).round(2)
    df['rev_per_employee'] = (df['revenue'] / df['employees']).round(4)
    
    def categorize_pe(pe):
        if pe < 15:
            return 'Undervalued'
        elif pe <= 30:
            return 'Fair Value'
        else:
            return 'Overvalued'
            
    def categorize_size(emp):
        if emp < 50000:
            return 'Small (<50k)'
        elif emp <= 100000:
            return 'Medium (50k-100k)'
        elif emp <= 150000:
            return 'Large (100k-150k)'
        else:
            return 'Enterprise (>150k)'

    df['valuation_status'] = df['pe_ratio'].apply(categorize_pe)
    df['company_size'] = df['employees'].apply(categorize_size)
    return df

if 'initialized' not in st.session_state:
    st.session_state['initialized'] = False

if not st.session_state['initialized']:
    progress_placeholder = st.empty()
    bar = progress_placeholder.progress(0, text="Menginisialisasi pipeline data...")
    for percent_complete in range(1, 101, 25):
        time.sleep(0.03)
        bar.progress(percent_complete, text=f"Memuat data ({percent_complete}%)...")
    progress_placeholder.empty()
    st.session_state['initialized'] = True

data_load_state = st.empty()
with st.spinner("Memproses data..."):
    df = load_and_preprocess_data(data_path)
data_load_state.caption("Data berhasil dimuat dan di-cache menggunakan st.cache_data")

def reset_filters_callback():
    st.session_state['selected_valuations'] = ['Undervalued', 'Fair Value', 'Overvalued']
    st.session_state['selected_sizes'] = ['Small (<50k)', 'Medium (50k-100k)', 'Large (100k-150k)', 'Enterprise (>150k)']
    st.session_state['price_filter'] = (float(df['price'].min()), float(df['price'].max()))
    st.session_state['pe_max'] = float(df['pe_ratio'].max())
    st.toast("Filter berhasil direset ke setelan awal")

if 'selected_valuations' not in st.session_state:
    st.session_state['selected_valuations'] = ['Undervalued', 'Fair Value', 'Overvalued']
if 'selected_sizes' not in st.session_state:
    st.session_state['selected_sizes'] = ['Small (<50k)', 'Medium (50k-100k)', 'Large (100k-150k)', 'Enterprise (>150k)']
if 'price_filter' not in st.session_state:
    st.session_state['price_filter'] = (float(df['price'].min()), float(df['price'].max()))
if 'pe_max' not in st.session_state:
    st.session_state['pe_max'] = float(df['pe_ratio'].max())

with st.sidebar:
    st.header("Filter dan Navigasi")
    st.write("Saring data perusahaan melalui opsi berikut:")
    
    selected_valuations = st.multiselect(
        "Kategori Valuasi (P/E Status):",
        options=['Undervalued', 'Fair Value', 'Overvalued'],
        default=st.session_state['selected_valuations']
    )
    
    size_options = ['Small (<50k)', 'Medium (50k-100k)', 'Large (100k-150k)', 'Enterprise (>150k)']
    selected_sizes = st.multiselect(
        "Skala Perusahaan:",
        options=size_options,
        default=st.session_state['selected_sizes']
    )
    
    price_min = float(df['price'].min())
    price_max = float(df['price'].max())
    price_range = st.slider(
        "Rentang Harga Saham ($):",
        min_value=price_min,
        max_value=price_max,
        value=st.session_state['price_filter'],
        step=50.0
    )
    
    pe_limit = st.slider(
        "Batas Maksimum P/E Ratio:",
        min_value=float(df['pe_ratio'].min()),
        max_value=float(df['pe_ratio'].max()),
        value=st.session_state['pe_max'],
        step=1.0
    )
    
    st.button("Reset Filter ke Default", on_click=reset_filters_callback, use_container_width=True)
    if st.button("Jalankan Animasi Selebrasi", use_container_width=True):
        st.balloons()

filtered_df = df[
    (df['valuation_status'].isin(selected_valuations)) &
    (df['company_size'].isin(selected_sizes)) &
    (df['price'] >= price_range[0]) &
    (df['price'] <= price_range[1]) &
    (df['pe_ratio'] <= pe_limit)
]

st.markdown('<div class="main-header">Dashboard Analitik Performa Finansial Perusahaan</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Laporan Praktikum Aplikasi Website (Modul 3 dan 4)</div>', unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("Tidak ada data yang sesuai dengan filter saat ini. Silakan sesuaikan filter di sidebar.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="Total Perusahaan Terpilih",
        value=f"{len(filtered_df):,} entitas",
        delta=f"{(len(filtered_df)/len(df)*100):.1f}% dari populasi"
    )
with col2:
    st.metric(
        label="Rata-rata Harga Saham",
        value=f"${filtered_df['price'].mean():,.2f}",
        delta=f"Median: ${filtered_df['price'].median():,.2f}"
    )
with col3:
    st.metric(
        label="Rata-rata Pendapatan",
        value=f"${filtered_df['revenue'].mean():,.2f}",
        delta=f"Total: ${filtered_df['revenue'].sum():,.0f}"
    )
with col4:
    avg_margin = filtered_df['profit_margin'].mean()
    st.metric(
        label="Rata-rata Profit Margin",
        value=f"{avg_margin:.2f}%",
        delta="Efisiensi Laba"
    )

tab_overview, tab_analysis, tab_calc, tab_data = st.tabs([
    "Ikhtisar dan Distribusi", 
    "Analisis Valuasi dan Performa", 
    "Kalkulator dan Callback Form", 
    "Data Mentah dan Ekspor"
])

with tab_overview:
    st.subheader("Distribusi Finansial dan Karakteristik Pasar")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**1. Distribusi Frekuensi Harga Saham (Histogram st.bar_chart)**")
        hist_prices = np.histogram(filtered_df['price'], bins=20)[0]
        st.bar_chart(hist_prices)
        st.caption("Frekuensi sebaran harga saham dalam 20 interval harga.")
        
    with col_b:
        st.markdown("**2. Rata-rata Pendapatan dan Laba Berdasarkan Skala Perusahaan**")
        size_agg = filtered_df.groupby('company_size')[['revenue', 'profit']].mean().reset_index()
        size_agg = size_agg.set_index('company_size')
        st.bar_chart(size_agg)
        st.caption("Perbandingan rata-rata pendapatan (Revenue) vs laba bersih (Profit).")

    st.markdown("**3. Distribusi P/E Ratio (Price-to-Earnings)**")
    pe_hist = np.histogram(filtered_df['pe_ratio'], bins=25)[0]
    st.line_chart(pe_hist)
    st.caption("Kurva frekuensi nilai valuasi P/E Ratio pada data yang disaring.")

with tab_analysis:
    st.subheader("Korelasi Pendapatan vs Laba Bersih")
    col_chart, col_top = st.columns([3, 2])
    
    with col_chart:
        fig, ax = plt.subplots(figsize=(8, 5))
        palette_map = {'Undervalued': '#10B981', 'Fair Value': '#F59E0B', 'Overvalued': '#EF4444'}
        sns.scatterplot(
            data=filtered_df,
            x='revenue',
            y='profit',
            hue='valuation_status',
            palette=palette_map,
            alpha=0.75,
            s=60,
            ax=ax
        )
        ax.set_title("Scatter Plot: Revenue vs Profit", fontsize=12, fontweight='bold')
        ax.set_xlabel("Revenue ($)")
        ax.set_ylabel("Profit ($)")
        st.pyplot(fig)
        plt.close(fig)
        
    with col_top:
        st.markdown("**Top 5 Perusahaan dengan Profit Margin Tertinggi**")
        top_profit = filtered_df[['company_id', 'price', 'revenue', 'profit', 'profit_margin', 'valuation_status']]\
            .sort_values(by='profit_margin', ascending=False)\
            .head(5)
        st.dataframe(
            top_profit.style.format({
                'price': '${:,.2f}',
                'revenue': '${:,.2f}',
                'profit': '${:,.2f}',
                'profit_margin': '{:.2f}%'
            }),
            use_container_width=True
        )
        
        st.markdown("**Matriks Korelasi:**")
        corr_matrix = filtered_df[['price', 'revenue', 'profit', 'pe_ratio']].corr()
        st.dataframe(corr_matrix.style.background_gradient(cmap='Blues'), use_container_width=True)

with tab_calc:
    st.subheader("Simulasi dan Callback Form Interaktif")
    st.write("Formulir ini menggunakan st.form dan on_click callback sesuai materi Modul 3.")
    
    def calculate_investment_callback():
        nominal = st.session_state.get('invest_amount', 1000)
        target_pe = st.session_state.get('target_pe_choice', 'Undervalued')
        
        subset = df[df['valuation_status'] == target_pe]
        avg_ret = subset['profit_margin'].mean() / 100
        projected_gain = nominal * avg_ret
        
        st.session_state['sim_result'] = {
            'target': target_pe,
            'nominal': nominal,
            'gain': projected_gain,
            'total': nominal + projected_gain,
            'margin': subset['profit_margin'].mean()
        }

    with st.form(key='investment_simulator_form'):
        form_col1, form_col2 = st.columns(2)
        with form_col1:
            st.number_input(
                "Jumlah Investasi ($ USD):", 
                min_value=100.0, 
                max_value=1000000.0, 
                value=5000.0, 
                step=500.0, 
                key='invest_amount'
            )
        with form_col2:
            st.selectbox(
                "Target Portofolio Berdasarkan Valuasi:",
                options=['Undervalued', 'Fair Value', 'Overvalued'],
                key='target_pe_choice'
            )
            
        st.form_submit_button(
            label="Hitung Proyeksi Laba", 
            on_click=calculate_investment_callback,
            use_container_width=True
        )

    if 'sim_result' in st.session_state:
        res = st.session_state['sim_result']
        st.success(f"Hasil Proyeksi: Investasi sebesar ${res['nominal']:,.2f} pada kategori {res['target']} "
                   f"(rata-rata profit margin {res['margin']:.2f}%) menghasilkan estimasi laba tahunan sebesar ${res['gain']:,.2f} "
                   f"(Total Nilai: ${res['total']:,.2f}).")

with tab_data:
    st.subheader("Inspeksi Data Mentah dan Ekspor")
    show_raw = st.checkbox("Tampilkan Tabel Data Mentah", value=True)
    if show_raw:
        st.dataframe(filtered_df, use_container_width=True)
        st.caption(f"Menampilkan {len(filtered_df)} baris data.")
        
    csv_export = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Unduh Data Hasil Filter (.csv)",
        data=csv_export,
        file_name="filtered_company_data.csv",
        mime="text/csv",
        use_container_width=True
    )
