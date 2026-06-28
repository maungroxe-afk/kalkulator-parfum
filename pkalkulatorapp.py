import streamlit as st
import pandas as pd
from google import genai

st.set_page_config(page_title="UCP ALPHA - Raw Material Calculator", layout="wide")

st.title("🧪 Perfume Raw Material & HPP Calculator")
st.write("Input seluruh komponen raw material Anda dalam tabel ala Excel, hitung HPP otomatis, dan optimasi harga jual.")

# --- SIDEBAR: KONFIGURASI AI ---
st.sidebar.header("🔑 Konfigurasi AI")
api_key = st.sidebar.text_input("Google Gemini API Key", type="password", help="Masukkan API Key dari Google AI Studio")

st.markdown("---")

# --- 1. TABEL INPUT BAHAN BAKU ---
st.header("📋 1. Tabel Komponen Raw Material")
st.write("Silakan isi nama bahan, detail pembelian, dan target formula Anda di bawah. Klik dua kali pada kotak untuk mengisi. Anda bisa menambah baris di bagian bawah tabel jika butuh lebih dari 5 bahan.")

# Data awal sebagai contoh/template pengisian
initial_data = {
    "Nama Raw Material": ["Bibit Utama A", "Absolute/Pelarut", "Fixative/Pengikat", "Bahan Tambahan D", "Bahan Tambahan E"],
    "Volume Dibeli (ml)": [100.0, 1000.0, 50.0, 10.0, 10.0],
    "Harga Beli (Rp)": [200000, 120000, 100000, 50000, 0],
    "Rasio Racikan (%)": [20.0, 75.0, 3.0, 2.0, 0.0]
}
df_template = pd.DataFrame(initial_data)

# Mengaktifkan tabel interaktif yang bisa diedit, ditambah barisnya, atau dikurangi
edited_df = st.data_editor(
    df_template, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config={
        "Harga Beli (Rp)": st.column_config.NumberColumn(format="Rp %d"),
        "Volume Dibeli (ml)": st.column_config.NumberColumn(format="%.1f ml"),
        "Rasio Racikan (%)": st.column_config.NumberColumn(format="%.2f %%")
    }
)

# --- PROSES KALKULASI DARI TABEL ---
# Menghitung Harga per ml untuk setiap baris
edited_df["Modal per ml (Rp)"] = edited_df["Harga Beli (Rp)"] / edited_df["Volume Dibeli (ml)"]
edited_df["Modal per ml (Rp)"] = edited_df["Modal per ml (Rp)"].fillna(0)

# Validasi Total Persentase
total_percentage = edited_df["Rasio Racikan (%)"].sum()

if total_percentage != 100.0:
    st.warning(f"⚠️ Total Rasio Racikan saat ini: **{total_percentage:.2f}%**. Pastikan totalnya pas **100%** agar perhitungan HPP akurat.")
else:
    st.success(f"✅ Total Rasio Racikan sempurna: **100%**")

st.markdown("---")

# --- 2. PARAMETER PRODUKSI & FINANSIAL ---
tab1, tab2, tab3 = st.tabs(["📊 Perhitungan HPP & Harga Jual", "🔮 AI Filosofi & Karakter Varian", "🤖 Optimasi Stok"])

with tab1:
    st.header("Formulasi Bisnis & Harga")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.subheader("⚙️ Volume & Kemasan")
        target_bottles = st.number_input("Target Jumlah Botol yang Dibuat", min_value=1, value=50)
        bottle_size = st.number_input("Ukuran Botol per Pcs (ml)", min_value=5, value=50)
        price_bottle = st.number_input("Harga Kemasan Terpasang (Botol + Stiker per pcs)", min_value=0, value=6000)
        
    with col_f2:
        st.subheader("🎯 Strategi Profit")
        pricing_method = st.radio("Metode Penentuan Harga Jual:", ["Target Markup (Kenaikan dari Modal)", "Target Margin Laba Kotor (%)"])
        if pricing_method == "Target Markup (Kenaikan dari Modal)":
            markup_pct = st.slider("Persentase Kenaikan Harga (%)", 50, 500, 200, step=10)
        else:
            margin_pct = st.slider("Target Margin Laba Kotor (%)", 10, 90, 60, step=5)

    # Hitung Kebutuhan & Biaya Riil berdasarkan isi tabel
    total_volume_needed = target_bottles * bottle_size
    
    # Hitung HPP cairan per botol
    # Rumus: Jumlah cairan per botol untuk bahan X dikali modal per ml bahan X
    edited_df["Vol Needed per Bottle (ml)"] = (edited_df["Rasio Racikan (%)"] / 100) * bottle_size
    edited_df["Cost per Bottle (Rp)"] = edited_df["Vol Needed per Bottle (ml)"] * edited_df["Modal per ml (Rp)"]
    
    total_liquid_cost_per_bottle = edited_df["Cost per Bottle (Rp)"].sum()
    hpp_per_bottle = total_liquid_cost_per_bottle + price_bottle
    total_production_cost = hpp_per_bottle * target_bottles

    # Perhitungan Harga Jual
    if pricing_method == "Target Markup (Kenaikan dari Modal)":
        suggested_price = hpp_per_bottle * (1 + (markup_pct / 100))
    else:
        suggested_price = hpp_per_bottle / (1 - (margin_pct / 100)) if margin_pct < 100 else hpp_per_bottle

    total_revenue = suggested_price * target_bottles
    total_profit = total_revenue - total_production_cost

    st.markdown("---")
    res_c1, res_c2 = st.columns(2)
    with res_c1:
        st.write("📊 **Rincian Formula per Botol:**")
        for _, row in edited_df.iterrows():
            if row["Rasio Racikan (%)"] > 0:
                st.write(f"* **{row['Nama Raw Material']}**: {row['Vol Needed per Bottle (ml)']:.2f} ml / botol (Biaya: Rp {row['Cost per Bottle (Rp)']:,.0f})")
        st.write(f"* 🍾 **Biaya Botol & Kemasan**: Rp {price_bottle:,.0f} / botol")
        
    with res_c2:
        st.metric(label="Harga Pokok Penjualan (HPP) per Botol", value=f"Rp {hpp_per_bottle:,.0f}")
        st.metric(label="💡 Saran Harga Jual per Botol", value=f"Rp {suggested_price:,.0f}", delta=f"Profit Bersih/Botol: Rp {suggested_price - hpp_per_bottle:,.0f}")
        
    st.markdown("---")
    st.subheader("💰 Proyeksi Keuntungan Total")
    p_col1, p_col2, p_col3 = st.columns(3)
    p_col1.metric(label="Total Modal Produksi Batch", value=f"Rp {total_production_cost:,.0f}")
    p_col2.metric(label="Estimasi Total Omzet", value=f"Rp {total_revenue:,.0f}")
    p_col3.metric(label="Estimasi Laba Bersih", value=f"Rp {total_profit:,.0f}")

with tab2:
    st.header("🔮 AI Fragrance Storyteller")
    if not api_key:
        st.warning("⚠️ Masukkan Google Gemini API Key di sidebar untuk mengaktifkan AI.")
    else:
        # Mengambil daftar nama bahan yang diinput di tabel sebagai referensi AI
        active_ingredients = edited_df[edited_df["Rasio Racikan (%)"] > 0]["Nama Raw Material"].tolist()
        
        st.write(f"Bahan aktif terdeteksi: *{', '.join(active_ingredients)}*")
        aroma_type = st.multiselect("Pilih Vibes Utama Aroma:", ["Manis (Sweet)", "Segar (Fresh/Citrus)", "Bunga (Floral)", "Kayu (Woody/Oud)", "Rempah (Spicy)", "Mewah/Eksklusif", "Calm/Powdery"])
        target_pasar = st.text_input("Target Pasar Spasifik:")
        catatan_tambahan = st.text_area("Deskripsi Tambahan / Nuansa Khusus yang Ingin Ditonjolkan:")
        
        if st.button("✨ Racik Filosofi Varian"):
            if not aroma_type:
                st.error("Pilih minimal satu vibes aroma!")
            else:
                with st.spinner("AI sedang menerjemahkan formula Anda menjadi cerita produk..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt = f"""
                        Kamu adalah perfumer profesional sekaligus copywriter brand mewah. Buatkan konsep parfum dengan:
                        - Struktur Komponen: {', '.join(active_ingredients)}
                        - Vibes Aroma: {', '.join(aroma_type)}
                        - Target Pasar: {target_pasar}
                        - Catatan Khusus: {catatan_tambahan}
                        
                        Output harus rapi dalam format Markdown meliputi: 3 Usulan Nama Eksklusif, Narasi Filosofi Produk untuk jualan/stiker, serta breakdown Top, Middle, dan Base Notes yang selaras secara teoritis.
                        """
                        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                        st.markdown("---")
                        st.success("🎉 Konsep Varian Sukses Dibuat!")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Gagal memanggil AI: {e}")

with tab3:
    st.header("🤖 Smart Stock Optimizer")
    st.write("Mencari batas maksimal botol yang bisa diracik berdasarkan sisa stok *raw material* Anda.")
    
    # Membuat input stok otomatis berdasarkan daftar nama bahan di tabel
    stok_list = []
    st.write("**Masukkan Sisa Stok Bahan Anda Saat Ini (ml):**")
    
    opt_cols = st.columns(2)
    count = 0
    
    for idx, row in edited_df.iterrows():
        if row["Rasio Racikan (%)"] > 0:
            current_col = opt_cols[0] if count % 2 == 0 else opt_cols[1]
            user_stok = current_col.number_input(f"Sisa Stok: {row['Nama Raw Material']} (ml)", min_value=0.0, value=float(row['Volume Dibeli (ml)']), key=f"stok_{idx}")
            stok_list.append((row['Nama Raw Material'], user_stok, row['Vol Needed per Bottle (ml)']))
            count += 1
            
    if stok_list:
        max_bottles_possible = []
        for name, current_stok, vol_per_b in stok_list:
            if vol_per_b > 0:
                max_bottles_possible.append(current_stok // vol_per_b)
            else:
                max_bottles_possible.append(float('inf'))
        
        final_max_production = int(min(max_bottles_possible)) if max_bottles_possible else 0
        
        st.markdown("---")
        st.success(f"Berdasarkan komponen bahan yang paling kritis, Anda hanya dapat memproduksi maksimal **{final_max_production} botol** (ukuran botol saat ini).")
