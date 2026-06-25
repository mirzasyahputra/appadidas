import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# Konfigurasi Halaman
st.set_page_config(page_title="SPK Penjualan Adidas", page_icon="👟", layout="wide")

# ==========================================
# 1. FUNGSI PEMBACAAN & PEMBERSIHAN DATA
# ==========================================
@st.cache_data
def load_data(file_path_or_buffer):
    df = pd.read_csv(file_path_or_buffer, skiprows=4)
    df = df.dropna(subset=['Retailer', 'Total Sales'])
    df['Invoice Date'] = pd.to_datetime(df['Invoice Date'], format='%m/%d/%Y', errors='coerce')
    
    def clean_currency(x):
        if isinstance(x, str):
            x = x.replace('$', '').replace(',', '').strip()
        return float(x) if x != '' else 0.0
        
    def clean_percentage(x):
        if isinstance(x, str):
            x = x.replace('%', '').strip()
            return float(x) / 100
        return float(x) if x != '' else 0.0

    def clean_number(x):
        if isinstance(x, str):
            x = x.replace(',', '').strip()
        return float(x) if x != '' else 0.0

    df['Price per Unit'] = df['Price per Unit'].apply(clean_currency)
    df['Total Sales'] = df['Total Sales'].apply(clean_currency)
    df['Operating Profit'] = df['Operating Profit'].apply(clean_currency)
    df['Units Sold'] = df['Units Sold'].apply(clean_number)
    df['Operating Margin'] = df['Operating Margin'].apply(clean_percentage)
    return df

# Inisialisasi Data
df = None
default_file_path = "adidas_us_sales_datasets.csv"

# ==========================================
# 2. MENU NAVIGASI SIDEBAR
# ==========================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/2/20/Adidas_Logo.svg", width=120)
st.sidebar.markdown("---")
st.sidebar.title("📌 Menu Navigasi")
menu = st.sidebar.radio(
    "Pilih Halaman:",
    ["🏠 Beranda", "📂 Dataset", "📊 Dashboard & Analisis", "🏆 Keputusan (SPK)"]
)
st.sidebar.markdown("---")

if os.path.exists(default_file_path):
    df = load_data(default_file_path)
else:
    st.sidebar.warning("⚠️ File lokal tidak ditemukan. Silakan unggah di menu Dataset.")

# ==========================================
# 3. KONTEN HALAMAN
# ==========================================

# --- HALAMAN BERANDA ---
if menu == "🏠 Beranda":
    st.title("👟 Sistem Pendukung Keputusan (SPK) Penjualan Adidas US")
    st.markdown("""
    Selamat datang di aplikasi SPK menggunakan algoritma **TOPSIS** dan **WASPAS**.
    Gunakan menu navigasi di sebelah kiri untuk melihat Dataset, menganalisis Dashboard visual, atau menjalankan algoritma SPK.
    """)

# --- HALAMAN DATASET ---
elif menu == "📂 Dataset":
    st.title("📂 Manajemen Dataset")
    if df is None:
        st.info("Silakan unggah dataset Adidas Sales Anda (format .csv).")
        uploaded_file = st.file_uploader("Unggah File CSV", type=['csv'])
        if uploaded_file is not None:
            df = load_data(uploaded_file)
            st.success("Data berhasil diunggah!")
            st.dataframe(df.head(100), use_container_width=True)
    else:
        st.success("Dataset berhasil dimuat.")
        st.dataframe(df, use_container_width=True)

# --- HALAMAN DASHBOARD & ANALISIS ---
elif menu == "📊 Dashboard & Analisis":
    st.title("📊 Dashboard Analisis Penjualan")
    
    if df is not None:
        # PENGATURAN FILTER DROPDOWN & LOGIKA OTOMATIS
        st.markdown("### ⚙️ Filter Data")
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            state_opt = ['Semua'] + list(df['State'].dropna().unique())
            sel_state = st.selectbox("1. Pilih State", state_opt)
            
            # Logika Otomatis: Jika State dipilih, Region terisi otomatis
            if sel_state != 'Semua':
                auto_region = df[df['State'] == sel_state]['Region'].iloc[0]
                sel_region = auto_region
                st.info(f"💡 Region otomatis diset ke: **{auto_region}**")
            else:
                region_opt = ['Semua'] + list(df['Region'].dropna().unique())
                sel_region = st.selectbox("Atau Pilih Region", region_opt)

        with col_f2:
            retailer_opt = ['Semua'] + list(df['Retailer'].dropna().unique())
            sel_retailer = st.selectbox("2. Pilih Retailer", retailer_opt)

        with col_f3:
            sales_meth_opt = ['Semua'] + list(df['Sales Method'].dropna().unique())
            sel_method = st.selectbox("3. Pilih Metode", sales_meth_opt)

        # Menerapkan Filter ke Dataframe
        filtered_df = df.copy()
        if sel_state != 'Semua':
            filtered_df = filtered_df[filtered_df['State'] == sel_state]
        elif sel_region != 'Semua':
            filtered_df = filtered_df[filtered_df['Region'] == sel_region]
            
        if sel_retailer != 'Semua':
            filtered_df = filtered_df[filtered_df['Retailer'] == sel_retailer]
        if sel_method != 'Semua':
            filtered_df = filtered_df[filtered_df['Sales Method'] == sel_method]

        if filtered_df.empty:
            st.warning("Data kosong dengan kombinasi filter saat ini.")
        else:
            # KPI
            st.markdown("---")
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Sales", f"${filtered_df['Total Sales'].sum():,.0f}")
            k2.metric("Operating Profit", f"${filtered_df['Operating Profit'].sum():,.0f}")
            k3.metric("Avg Margin", f"{filtered_df['Operating Margin'].mean():.2%}")
            k4.metric("Total Units", f"{filtered_df['Units Sold'].sum():,.0f}")
            st.markdown("---")
            
            # Visualisasi
            c1, c2 = st.columns(2)
            with c1:
                df_monthly = filtered_df.groupby(filtered_df['Invoice Date'].dt.to_period('M'))['Total Sales'].sum().reset_index()
                df_monthly['Invoice Date'] = df_monthly['Invoice Date'].dt.to_timestamp()
                fig1 = px.line(df_monthly, x='Invoice Date', y='Total Sales', title="Tren Total Sales Bulanan", markers=True)
                st.plotly_chart(fig1, use_container_width=True)
                
                df_method = filtered_df.groupby('Sales Method')['Total Sales'].sum().reset_index()
                fig3 = px.pie(df_method, names='Sales Method', values='Total Sales', title="Kontribusi Metode Penjualan", hole=0.45)
                st.plotly_chart(fig3, use_container_width=True)

            with c2:
                df_product = filtered_df.groupby('Product')['Total Sales'].sum().reset_index()
                fig2 = px.bar(df_product, x='Total Sales', y='Product', orientation='h', title="Total Sales per Produk", color='Total Sales', color_continuous_scale='Blues')
                st.plotly_chart(fig2, use_container_width=True)
                
                # REVISI CHART KORELASI (Menggunakan Grouped Bar Chart untuk Top 10 State)
                df_corr = filtered_df.groupby('State')[['Total Sales', 'Operating Profit']].sum().reset_index()
                df_corr = df_corr.sort_values('Total Sales', ascending=False).head(10) # Ambil Top 10 agar mudah dibaca
                fig4 = px.bar(df_corr, x='State', y=['Total Sales', 'Operating Profit'], 
                              barmode='group', title="Perbandingan Sales vs Profit (Top 10 State)",
                              labels={'value': 'Jumlah ($)', 'variable': 'Metrik'})
                st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("Silakan muat dataset terlebih dahulu di menu 📂 Dataset.")

# --- HALAMAN SPK (TOPSIS & WASPAS) ---
elif menu == "🏆 Keputusan (SPK)":
    st.title("🏆 Sistem Pendukung Keputusan")
    st.markdown("Menentukan alternatif terbaik menggunakan algoritma **TOPSIS** dan **WASPAS**.")
    
    if df is not None:
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            rank_entity = st.selectbox("🎯 Pilih Alternatif yang diuji:", ['Retailer', 'City', 'Product'])
        with col_r2:
            algoritma = st.selectbox("⚙️ Pilih Algoritma SPK:", ['Perbandingan Keduanya (TOPSIS & WASPAS)', 'Hanya TOPSIS', 'Hanya WASPAS'])

        st.markdown("**Kriteria Penilaian (Benefit):** C1 (Total Sales), C2 (Operating Profit), C3 (Units Sold), C4 (Avg Margin)")
        
        # Persiapan Matriks Keputusan
        # Mengagregasi data berdasarkan entitas yang dipilih
        df_matrix = df.groupby(rank_entity).agg(
            C1_Sales=('Total Sales', 'sum'),
            C2_Profit=('Operating Profit', 'sum'),
            C3_Units=('Units Sold', 'sum'),
            C4_Margin=('Operating Margin', 'mean')
        ).reset_index()
        
        alternatives = df_matrix[rank_entity].values
        matrix_values = df_matrix[['C1_Sales', 'C2_Profit', 'C3_Units', 'C4_Margin']]
        
        # Bobot Kriteria (Misal: C1=40%, C2=30%, C3=20%, C4=10%)
        weights = np.array([0.40, 0.30, 0.20, 0.10])
        
        # ==========================================
        # IMPLEMENTASI ALGORITMA TOPSIS
        # ==========================================
        def calc_topsis(matrix, w):
            # 1. Normalisasi
            norm = matrix / np.sqrt((matrix**2).sum())
            # 2. Normalisasi Terbobot
            weighted_norm = norm * w
            # 3. Solusi Ideal (Karena semua kriteria adalah Benefit, max = ideal positif)
            ideal_pos = weighted_norm.max()
            ideal_neg = weighted_norm.min()
            # 4. Jarak ke Solusi Ideal
            d_pos = np.sqrt(((weighted_norm - ideal_pos)**2).sum(axis=1))
            d_neg = np.sqrt(((weighted_norm - ideal_neg)**2).sum(axis=1))
            # 5. Nilai Preferensi (Skor)
            score = d_neg / (d_pos + d_neg)
            return score

        # ==========================================
        # IMPLEMENTASI ALGORITMA WASPAS
        # ==========================================
        def calc_waspas(matrix, w):
            # 1. Normalisasi (Untuk kriteria benefit: Nilai / Max)
            norm = matrix / matrix.max()
            # 2. WSM (Weighted Sum Model)
            wsm = (norm * w).sum(axis=1)
            # 3. WPM (Weighted Product Model) -> Menghindari error nilai 0 dengan menggantinya jadi nilai sangat kecil
            norm_wpm = norm.replace(0, 1e-6)
            wpm = 1
            for i, col in enumerate(norm_wpm.columns):
                wpm *= norm_wpm[col] ** w[i]
            # 4. Agregasi (Q) dengan lambda = 0.5
            score = 0.5 * wsm + 0.5 * wpm
            return score

        # Eksekusi Algoritma
        df_matrix['Skor TOPSIS'] = calc_topsis(matrix_values, weights)
        df_matrix['Skor WASPAS'] = calc_waspas(matrix_values, weights)
        
        # Tampilan Hasil TOPSIS
        if algoritma in ['Hanya TOPSIS', 'Perbandingan Keduanya (TOPSIS & WASPAS)']:
            st.markdown("### 🥇 Hasil Perankingan TOPSIS")
            df_topsis = df_matrix[[rank_entity, 'Skor TOPSIS']].sort_values(by='Skor TOPSIS', ascending=False).reset_index(drop=True)
            df_topsis.index = df_topsis.index + 1
            st.dataframe(df_topsis.style.highlight_max(subset=['Skor TOPSIS'], color='lightgreen'), use_container_width=True)
            st.success(f"**Rekomendasi TOPSIS:** {df_topsis.iloc[0][rank_entity]}")

        # Tampilan Hasil WASPAS
        if algoritma in ['Hanya WASPAS', 'Perbandingan Keduanya (TOPSIS & WASPAS)']:
            st.markdown("### 🥇 Hasil Perankingan WASPAS")
            df_waspas = df_matrix[[rank_entity, 'Skor WASPAS']].sort_values(by='Skor WASPAS', ascending=False).reset_index(drop=True)
            df_waspas.index = df_waspas.index + 1
            st.dataframe(df_waspas.style.highlight_max(subset=['Skor WASPAS'], color='lightblue'), use_container_width=True)
            st.success(f"**Rekomendasi WASPAS:** {df_waspas.iloc[0][rank_entity]}")

    else:
         st.warning("Silakan muat dataset terlebih dahulu di menu 📂 Dataset.")
