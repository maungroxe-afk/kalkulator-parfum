import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Fragrance Production & AI Storyteller", layout="wide")

st.title("🧪 Custom Perfume Production & Price Optimizer")
st.write("Input bahan kustom, hitung HPP presisi, dan racik filosofi aroma dengan AI.")

# --- SIDEBAR: KONFIGURASI API KEY ---
st.sidebar.header("🔑 Konfigurasi AI")
api_key = st.sidebar.text_input("Google Gemini API Key", type="password", help="Masukkan API Key dari Google AI Studio")

st.markdown("---")

# --- INPUT BAHAN KUSTOM ---
st.header("📦 1. Input Pembelian & Modal Bahan Baku")
st.write("Masukkan detail bahan yang Anda beli beserta harganya untuk menghitung modal per ml secara otomatis.")

col_b1, col_b2, col_b3 = st.columns(3)

with col_b1:
    st.subheader("🧪 Bahan 1: Bibit Parfum")
    name_fragrance = st.text_input("Nama Bibit", value="Bibit Varian A")
    buy_vol_fragrance = st.number_input("Volume yang Dibeli (ml)", min_value=1, value=100, key="bv_f")
    buy_price_fragrance = st.number_input("Total Harga Beli (Rp)", min_value=0, value=150000, key="bp_f")
    # Hitung per ml
    price_fragrance_per_ml = buy_price_fragrance / buy_vol_fragrance if buy_vol_fragrance > 0 else 0
    st.caption(f"💰 Modal {name_fragrance}: **Rp {price_fragrance_per_ml:,.1f} / ml**")

with col_b2:
    st.subheader("💧 Bahan 2: Pelarut / Alkohol")
    name_solvent = st.text_input("Nama Pelarut", value="Absolute Premium")
    buy_vol_solvent = st.number_input("Volume yang Dibeli (ml)", min_value=1, value=1000, key="bv_s")
    buy_price_solvent = st.number_input("Total Harga Beli (Rp)", min_value=0, value=120000, key="bp_s")
    # Hitung per ml
    price_solvent_per_ml = buy_price_solvent / buy_vol_solvent if buy_vol_solvent > 0 else 0
    st.caption(f"💰 Modal {name_solvent}: **Rp {price_solvent_per_ml:,.1f} / ml**")

with col_b3:
    st.subheader("⚗️ Bahan 3: Fixative / Pengikat")
    name_fixative = st.text_input("Nama Fixative", value="Fixative Super")
    buy_vol_fixative = st.number_input("Volume yang Dibeli (ml)", min_value=1, value=50, key="bv_x")
    buy_price_fixative = st.number_input("Total Harga Beli (Rp)", min_value=0, value=100000, key="bp_x")
    # Hitung per ml
    price_fixative_per_ml = buy_price_fixative / buy_vol_fixative if buy_vol_fixative > 0 else 0
    st.caption(f"💰 Modal {name_fixative}: **Rp {price_fixative_per_ml:,.1f} / ml**")

st.markdown("---")

# --- TABS UTUK FORMULASI & AI ---
tab1, tab2, tab3 = st.tabs(["📊 Formulasi, HPP & Harga Jual", "🔮 AI Filosofi & Notes", "🤖 Optimasi Sisa Stok"])

with tab1:
    st.header("Formulasi & Strategi Harga")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.subheader("⚙️ Parameter Produksi & Kemasan")
        target_bottles = st.number_input("Target Jumlah Botol", min_value=1, value=10)
        bottle_size = st.number_input("Ukuran Botol (ml)", min_value=5, value=50)
        price_bottle = st.number_input("Harga Kemasan (Botol + Stiker per pcs)", min_value=0, value=5000)
        
        st.markdown("---")
        st.subheader("🎯 Target Keuntungan")
        pricing_method = st.radio("Metode Penentuan Harga Jual:", ["Target Markup (Kenaikan dari Modal)", "Target Margin Laba Kotor (%)"])
        if pricing_method == "Target Markup (Kenaikan dari Modal)":
            markup_pct = st.slider("Persentase Kenaikan Harga (%)", 50, 500, 200, step=10)
        else:
            margin_pct = st.slider("Target Margin Laba Kotor (%)", 10, 90, 60, step=5)
        
    with col_f2:
        st.subheader("🧪 Persentase Racikan Racikan (%)")
        pct_fragrance = st.slider(f"Persentase {name_fragrance} (%)", 0, 100, 30)
        pct_fixative = st.slider(f"Persentase {name_fixative} (%)", 0, 10, 2)
        pct_solvent = 100 - (pct_fragrance + pct_fixative)
        
        if pct_solvent < 0:
            st.error("⚠️ Total persentase melebihi 100%! Kurangi bibit atau fixative.")
            pct_solvent = 0
        else:
            st.info(f"Persentase {name_solvent} Otomatis: {pct_solvent}%")

    # Kalkulasi Volume & Biaya Cairan
    total_volume_needed = target_bottles * bottle_size
    req_fragrance = (pct_fragrance / 100) * total_volume_needed
    req_solvent = (pct_solvent / 100) * total_volume_needed
    req_fixative = (pct_fixative / 100) * total_volume_needed
    
    cost_fragrance = req_fragrance * price_fragrance_per_ml
    cost_solvent = req_solvent * price_solvent_per_ml
    cost_fixative = req_fixative * price_fixative_per_ml
    cost_bottles = target_bottles * price_bottle
    
    total_cost = cost_fragrance + cost_solvent + cost_fixative + cost_bottles
    hpp_per_bottle = total_cost / target_bottles if target_bottles > 0 else 0

    # Kalkulasi Rekomendasi Harga Jual
    if pricing_method == "Target Markup (Kenaikan dari Modal)":
        suggested_price = hpp_per_bottle * (1 + (markup_pct / 100))
    else:
        suggested_price = hpp_per_bottle / (1 - (margin_pct / 100)) if margin_pct < 100 else hpp_per_bottle

    total_revenue = suggested_price * target_bottles
    total_profit = total_revenue - total_cost

    st.markdown("---")
    res_c1, res_c2 = st.columns(2)
    with res_c1:
        st.write(f"**Detail Kebutuhan Total Cairan ({total_volume_needed} ml):**")
        st.write(f"* 🧪 {name_fragrance}: **{req_fragrance:.1f} ml** (Biaya: Rp {cost_fragrance:,.0f})")
        st.write(f"* 💧 {name_solvent}: **{req_solvent:.1f} ml** (Biaya: Rp {cost_solvent:,.0f})")
        st.write(f"* ⚗️ {name_fixative}: **{req_fixative:.1f} ml** (Biaya: Rp {cost_fixative:,.0f})")
        st.write(f"* 🍾 Kemasan Botol & Stiker: **{target_bottles} pcs** (Biaya: Rp {cost_bottles:,.0f})")
        
    with res_c2:
        st.metric(label="Harga Pokok Penjualan (HPP) per Botol", value=f"Rp {hpp_per_bottle:,.0f}")
        st.metric(label="💡 Rekomendasi Harga Jual per Botol", value=f"Rp {suggested_price:,.0f}", delta=f"Profit/Botol: Rp {suggested_price - hpp_per_bottle:,.0f}")
        
    st.markdown("---")
    st.subheader("💰 Proyeksi Keuntungan Total")
    p_col1, p_col2, p_col3 = st.columns(3)
    p_col1.metric(label="Total Modal Produksi", value=f"Rp {total_cost:,.0f}")
    p_col2.metric(label="Estimasi Total Omzet", value=f"Rp {total_revenue:,.0f}")
    p_col3.metric(label="Estimasi Laba Bersih", value=f"Rp {total_profit:,.0f}")

with tab2:
    st.header("🔮 AI Fragrance Storyteller")
    if not api_key:
        st.warning("⚠️ Masukkan Google Gemini API Key di sidebar untuk mengaktifkan AI.")
    else:
        aroma_type = st.multiselect("Karakter Utama Aroma:", ["Manis (Sweet)", "Segar (Fresh/Citrus)", "Bunga (Floral)", "Kayu (Woody/Oud)", "Rempah (Spicy)", "Mewah", "Calm/Powdery"])
        target_pasar = st.text_input("Target Konsumen:")
        catatan_tambahan = st.text_area("Catatan Khusus Varian:")
        
        if st.button("✨ Generasikan Filosofi & Notes"):
            if not aroma_type:
                st.error("Pilih minimal satu karakter utama aroma!")
            else:
                with st.spinner("AI sedang meracik cerita varian baru Anda..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt = f"Buatkan nama (3 opsi), filosofi puitis, dan rincian Top, Middle, Base notes untuk parfum berkarakter {', '.join(aroma_type)} dengan target pasar {target_pasar}. Catatan: {catatan_tambahan}"
                        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                        st.markdown("---")
                        st.success("🎉 Konsep Parfum Berhasil Dibuat!")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Terjadi kesalahan: {e}")

with tab3:
    st.header("🤖 Smart Stock Optimizer")
    st.write("Gunakan sisa total stok bahan yang Anda miliki saat ini untuk mengetahui batas maksimal produksi.")
    
    opt_c1, opt_c2 = st.columns(2)
    with opt_c1:
        stok_f = st.number_input(f"Sisa Stok {name_fragrance} yang Dimiliki (ml)", min_value=0.0, value=float(buy_vol_fragrance))
        stok_s = st.number_input(f"Sisa Stok {name_solvent} yang Dimiliki (ml)", min_value=0.0, value=float(buy_vol_solvent))
        stok_x = st.number_input(f"Sisa Stok {name_fixative} yang Dimiliki (ml)", min_value=0.0, value=float(buy_vol_fixative))
    with opt_c2:
        target_size = st.selectbox("Pilih Ukuran Botol Target Produksi (ml)", [30, 50, 100], index=1)
        
    vol_f_per_b = (pct_fragrance / 100) * target_size
    vol_s_per_b = (pct_solvent / 100) * target_size
    vol_x_per_b = (pct_fixative / 100) * target_size
    
    max_f = stok_f // vol_f_per_b if vol_f_per_b > 0 else 0
    max_s = stok_s // vol_s_per_b if vol_s_per_b > 0 else 0
    max_x = stok_x // vol_x_per_b if vol_x_per_b > 0 else 0
    
    max_production = int(min(max_f, max_s, max_x))
    
    st.markdown("---")
    st.success(f"Berdasarkan sisa bahan paling terbatas, Anda dapat meracik maksimal **{max_production} botol** ukuran {target_size} ml.")
