import streamlit as st
import pandas as pd
import plotly.express as px
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
# 2. MENU NAVIGASI SIDEBAR (GAYA SPK)
# ==========================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/2/20/Adidas_Logo.svg", width=120)
st.sidebar.markdown("---")
st.sidebar.title("📌 Menu Navigasi")
menu = st.sidebar.radio(
    "Pilih Halaman:",
    ["🏠 Beranda", "📂 Dataset", "📊 Dashboard & Analisis", "🏆 Keputusan (Ranking)"]
)
st.sidebar.markdown("---")

# Cek & Load Data
if os.path.exists(default_file_path):
    df = load_data(default_file_path)
else:
    st.sidebar.warning("⚠️ File lokal tidak ditemukan. Silakan unggah di menu Dataset.")

# ==========================================
# 3. KONTEN HALAMAN
# ==========================================

# --- HALAMAN BERANDA ---
if menu == "🏠 Beranda":
    st.title("👟 Sistem Pendukung Keputusan & Analisis Penjualan Adidas US")
    st.markdown("""
    Selamat datang di aplikasi SPK dan Dashboard Analisis Penjualan Adidas!
    
    Aplikasi ini dirancang untuk membantu manajemen dalam mengambil keputusan strategis berdasarkan performa historis penjualan di Amerika Serikat.
    
    **Fitur Utama:**
    * **Dataset:** Melihat dan mengelola data mentah yang digunakan.
    * **Dashboard & Analisis:** Memantau KPI dan tren penjualan secara visual.
    * **Keputusan (Ranking):** Menentukan peringkat alternatif (Retailer, Produk, atau Kota) terbaik berdasarkan kriteria tertentu.
    
    Silakan gunakan menu navigasi di sebelah kiri untuk mulai mengeksplorasi sistem.
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
        st.success("Dataset berhasil dimuat dan siap diolah.")
        st.markdown(f"**Total Data:** {df.shape[0]} Baris | {df.shape[1]} Kolom")
        st.dataframe(df, use_container_width=True)

# --- HALAMAN DASHBOARD & ANALISIS ---
elif menu == "📊 Dashboard & Analisis":
    st.title("📊 Dashboard Analisis Penjualan")
    
    if df is not None:
        # Filter Data bergaya Expandable Panel
        with st.expander("⚙️ Filter Data Analisis", expanded=True):
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                region_opt = df['Region'].dropna().unique()
                sel_region = st.multiselect("Region", region_opt, default=region_opt)
            with col_f2:
                filtered_df_reg = df[df['Region'].isin(sel_region)] if sel_region else df
                state_opt = filtered_df_reg['State'].dropna().unique()
                sel_state = st.multiselect("State", state_opt, default=state_opt)
            with col_f3:
                retailer_opt = df['Retailer'].dropna().unique()
                sel_retailer = st.multiselect("Retailer", retailer_opt, default=retailer_opt)
            with col_f4:
                sales_meth_opt = df['Sales Method'].dropna().unique()
                sel_method = st.multiselect("Metode", sales_meth_opt, default=sales_meth_opt)

        # Terapkan Filter
        filtered_df = df[
            (df['Region'].isin(sel_region)) &
            (df['State'].isin(sel_state)) &
            (df['Retailer'].isin(sel_retailer)) &
            (df['Sales Method'].isin(sel_method))
        ]

        if filtered_df.empty:
            st.warning("Data kosong dengan filter saat ini.")
        else:
            # KPI Cards
            st.markdown("### 💡 Key Performance Indicators (KPI)")
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Sales", f"${filtered_df['Total Sales'].sum():,.0f}")
            k2.metric("Operating Profit", f"${filtered_df['Operating Profit'].sum():,.0f}")
            k3.metric("Avg Margin", f"{filtered_df['Operating Margin'].mean():.2%}")
            k4.metric("Total Units", f"{filtered_df['Units Sold'].sum():,.0f}")
            
            st.markdown("---")
            
            # Charts
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
                df_product = filtered_df.groupby('Product')['Total Sales'].sum().reset_index().sort_values('Total Sales', ascending=True)
                fig2 = px.bar(df_product, x='Total Sales', y='Product', orientation='h', title="Total Sales per Produk", color='Total Sales', color_continuous_scale='Blues')
                st.plotly_chart(fig2, use_container_width=True)
                
                df_state = filtered_df.groupby(['Region', 'State'])[['Total Sales', 'Operating Profit']].sum().reset_index()
                fig4 = px.scatter(df_state, x='Total Sales', y='Operating Profit', color='Region', size='Total Sales', hover_name='State', title="Korelasi Sales vs Profit per State")
                st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("Silakan muat dataset terlebih dahulu di menu 📂 Dataset.")

# --- HALAMAN KEPUTUSAN / PERANKINGAN ---
elif menu == "🏆 Keputusan (Ranking)":
    st.title("🏆 Sistem Perankingan Alternatif")
    st.markdown("Gunakan modul ini untuk menentukan alternatif terbaik berdasarkan kriteria (metrik) yang dipilih.")
    
    if df is not None:
        st.markdown("### Konfigurasi Kriteria Keputusan")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            rank_entity = st.selectbox("🎯 Pilih Alternatif:", ['Retailer', 'Product', 'City'])
        with col_r2:
            rank_metric = st.selectbox("📏 Pilih Kriteria (Benefit):", ['Total Sales', 'Operating Profit', 'Units Sold'])
            
        # Proses SPK Sederhana (Ranking)
        st.markdown(f"### Hasil Rekomendasi Peringkat: **{rank_entity}** berdasarkan **{rank_metric}**")
        
        df_rank = df.groupby(rank_entity)[rank_metric].sum().reset_index()
        df_rank = df_rank.sort_values(by=rank_metric, ascending=False).reset_index(drop=True)
        df_rank.index = df_rank.index + 1
        df_rank.index.name = "Peringkat"
        
        # Formatting Tabel
        df_rank_display = df_rank.copy()
        if rank_metric in ['Total Sales', 'Operating Profit']:
            df_rank_display[rank_metric] = df_rank_display[rank_metric].apply(lambda x: f"${x:,.2f}")
        else:
            df_rank_display[rank_metric] = df_rank_display[rank_metric].apply(lambda x: f"{x:,.0f}")
            
        st.dataframe(df_rank_display, use_container_width=True)
        
        # Kesimpulan Otomatis
        if not df_rank.empty:
            top_1 = df_rank.iloc[0]
            st.success(f"**Kesimpulan:** Berdasarkan perhitungan data, alternatif terbaik untuk kriteria {rank_metric} adalah **{top_1[rank_entity]}**.")
    else:
         st.warning("Silakan muat dataset terlebih dahulu di menu 📂 Dataset.")