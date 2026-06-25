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
    Selamat datang di aplikasi SPK untuk menentukan **Retailer Terbaik**.
    Gunakan menu navigasi di sebelah kiri untuk melihat Dataset, menganalisis Dashboard visual secara interaktif, atau menjalankan perhitungan algoritma SPK secara transparan.
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
        st.markdown("### ⚙️ Filter Data (Multi-select)")
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        
        with col_f1:
            region_opt = list(df['Region'].dropna().unique())
            sel_region = st.multiselect("1. Pilih Region", region_opt)
            
        with col_f2:
            # Otomatis menyesuaikan pilihan State berdasarkan Region
            if sel_region:
                state_opt = list(df[df['Region'].isin(sel_region)]['State'].dropna().unique())
            else:
                state_opt = list(df['State'].dropna().unique())
            sel_state = st.multiselect("2. Pilih State", state_opt)

        with col_f3:
            retailer_opt = list(df['Retailer'].dropna().unique())
            sel_retailer = st.multiselect("3. Pilih Retailer", retailer_opt)

        with col_f4:
            sales_meth_opt = list(df['Sales Method'].dropna().unique())
            sel_method = st.multiselect("4. Pilih Metode", sales_meth_opt)

        # Menerapkan Filter (Jika kosong, tampilkan semua)
        filtered_df = df.copy()
        if sel_region:
            filtered_df = filtered_df[filtered_df['Region'].isin(sel_region)]
        if sel_state:
            filtered_df = filtered_df[filtered_df['State'].isin(sel_state)]
        if sel_retailer:
            filtered_df = filtered_df[filtered_df['Retailer'].isin(sel_retailer)]
        if sel_method:
            filtered_df = filtered_df[filtered_df['Sales Method'].isin(sel_method)]

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
                
                df_corr = filtered_df.groupby('State')[['Total Sales', 'Operating Profit']].sum().reset_index()
                df_corr = df_corr.sort_values('Total Sales', ascending=False).head(10)
                fig4 = px.bar(df_corr, x='State', y=['Total Sales', 'Operating Profit'], 
                              barmode='group', title="Perbandingan Sales vs Profit (Top 10 State)",
                              labels={'value': 'Jumlah ($)', 'variable': 'Metrik'})
                st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("Silakan muat dataset terlebih dahulu di menu 📂 Dataset.")

# --- HALAMAN SPK (RETAILER TERBAIK) ---
elif menu == "🏆 Keputusan (SPK)":
    st.title("🏆 SPK Penentuan Retailer Terbaik")
    st.markdown("Sistem membandingkan kinerja Retailer menggunakan metode **TOPSIS** dan **WASPAS** berdasarkan 4 Kriteria Benefit.")
    
    if df is not None:
        # INPUT BOBOT DINAMIS
        st.markdown("### 🎛️ Input Bobot Kriteria")
        st.info("Tentukan tingkat kepentingan (bobot) untuk masing-masing kriteria. Angka akan dinormalisasi secara otomatis.")
        b1, b2, b3, b4 = st.columns(4)
        w1 = b1.number_input("C1: Total Sales", min_value=1, max_value=100, value=40)
        w2 = b2.number_input("C2: Total Units Sold", min_value=1, max_value=100, value=30)
        w3 = b3.number_input("C3: Operating Profit", min_value=1, max_value=100, value=20)
        w4 = b4.number_input("C4: Avg Margin", min_value=1, max_value=100, value=10)
        
        # Normalisasi Bobot agar totalnya 1
        total_w = w1 + w2 + w3 + w4
        weights = np.array([w1, w2, w3, w4]) / total_w

        # TAHAP 1: MATRIKS KEPUTUSAN AWAL
        st.markdown("---")
        st.markdown("### 📊 Tahap 1: Matriks Keputusan Awal")
        df_matrix = df.groupby('Retailer').agg(
            C1_Sales=('Total Sales', 'sum'),
            C2_Units=('Units Sold', 'sum'),
            C3_Profit=('Operating Profit', 'sum'),
            C4_Margin=('Operating Margin', 'mean')
        ).reset_index()
        
        # Tampilkan tabel format yang rapi
        df_display = df_matrix.copy()
        df_display['C1_Sales'] = df_display['C1_Sales'].apply(lambda x: f"${x:,.0f}")
        df_display['C2_Units'] = df_display['C2_Units'].apply(lambda x: f"{x:,.0f}")
        df_display['C3_Profit'] = df_display['C3_Profit'].apply(lambda x: f"${x:,.0f}")
        df_display['C4_Margin'] = df_display['C4_Margin'].apply(lambda x: f"{x:.2%}")
        st.dataframe(df_display, use_container_width=True)

        matrix_vals = df_matrix[['C1_Sales', 'C2_Units', 'C3_Profit', 'C4_Margin']].values

        # TAHAP 2: MATRIKS NORMALISASI (TOPSIS & WASPAS)
        st.markdown("### 🧮 Tahap 2: Matriks Normalisasi")
        
        # Normalisasi TOPSIS (Akar Kuadrat)
        norm_topsis = matrix_vals / np.sqrt((matrix_vals**2).sum(axis=0))
        df_norm_topsis = pd.DataFrame(norm_topsis, columns=['C1 (Norm)', 'C2 (Norm)', 'C3 (Norm)', 'C4 (Norm)'])
        df_norm_topsis.insert(0, 'Retailer', df_matrix['Retailer'])

        # Normalisasi WASPAS (Nilai / Max untuk Kriteria Benefit)
        norm_waspas = matrix_vals / matrix_vals.max(axis=0)
        df_norm_waspas = pd.DataFrame(norm_waspas, columns=['C1 (Norm)', 'C2 (Norm)', 'C3 (Norm)', 'C4 (Norm)'])
        df_norm_waspas.insert(0, 'Retailer', df_matrix['Retailer'])

        c_norm1, c_norm2 = st.columns(2)
        with c_norm1:
            st.markdown("**Normalisasi TOPSIS**")
            st.dataframe(df_norm_topsis.style.format({col: "{:.4f}" for col in df_norm_topsis.columns if col != 'Retailer'}), use_container_width=True)
        with c_norm2:
            st.markdown("**Normalisasi WASPAS**")
            st.dataframe(df_norm_waspas.style.format({col: "{:.4f}" for col in df_norm_waspas.columns if col != 'Retailer'}), use_container_width=True)

        # KALKULASI TOPSIS
        weighted_norm = norm_topsis * weights
        ideal_pos = weighted_norm.max(axis=0)
        ideal_neg = weighted_norm.min(axis=0)
        d_pos = np.sqrt(((weighted_norm - ideal_pos)**2).sum(axis=1))
        d_neg = np.sqrt(((weighted_norm - ideal_neg)**2).sum(axis=1))
        score_topsis = d_neg / (d_pos + d_neg)

        # KALKULASI WASPAS
        wsm = (norm_waspas * weights).sum(axis=1)
        norm_waspas_safe = np.where(norm_waspas == 0, 1e-6, norm_waspas) # Menghindari perkalian 0 di WPM
        wpm = np.prod(norm_waspas_safe ** weights, axis=1)
        score_waspas = 0.5 * wsm + 0.5 * wpm

        # TAHAP 3: HASIL AKHIR
        st.markdown("### 🥇 Tahap 3: Hasil Akhir & Perbandingan Ranking")
        df_final = pd.DataFrame({
            'Retailer': df_matrix['Retailer'],
            'Skor TOPSIS': score_topsis,
            'Skor WASPAS': score_waspas
        })
        
        # Buat Ranking
        df_final['Ranking TOPSIS'] = df_final['Skor TOPSIS'].rank(ascending=False, method='min').astype(int)
        df_final['Ranking WASPAS'] = df_final['Skor WASPAS'].rank(ascending=False, method='min').astype(int)
        
        # Urutkan berdasarkan Ranking TOPSIS sebagai default tampilan
        df_final = df_final.sort_values(by='Ranking TOPSIS').reset_index(drop=True)
        
        # Tampilkan tabel akhir
        st.dataframe(df_final.style.format({
            'Skor TOPSIS': "{:.4f}", 
            'Skor WASPAS': "{:.4f}"
        }).background_gradient(subset=['Ranking TOPSIS', 'Ranking WASPAS'], cmap='YlGn_r'), use_container_width=True)
        
        # Kesimpulan
        top_topsis = df_final[df_final['Ranking TOPSIS'] == 1]['Retailer'].values[0]
        top_waspas = df_final[df_final['Ranking WASPAS'] == 1]['Retailer'].values[0]
        
        st.success(f"**KESIMPULAN:** Berdasarkan bobot yang Anda tetapkan, Retailer terbaik menurut metode TOPSIS adalah **{top_topsis}**, dan menurut metode WASPAS adalah **{top_waspas}**.")

    else:
         st.warning("Silakan muat dataset terlebih dahulu di menu 📂 Dataset.")
