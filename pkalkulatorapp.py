import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Fragrance Production & AI Storyteller", layout="wide")

st.title("🧪 Perfume Production, Pricing & AI Storyteller")
st.write("Hitung formula, HPP, optimasi harga, dan biarkan AI merancang filosofi aroma parfum Anda.")

# --- SIDEBAR: INPUT HARGA BAHAN & API KEY ---
st.sidebar.header("🔑 Konfigurasi & Harga Bahan")
api_key = st.sidebar.text_input("Google Gemini API Key", type="password", help="Masukkan API Key Anda dari Google AI Studio")

st.sidebar.markdown("---")
price_fragrance = st.sidebar.number_input("Harga Bibit Parfum (per ml)", min_value=0, value=1500)
price_solvent = st.sidebar.number_input("Harga Pelarut/Alkohol (per ml)", min_value=0, value=200)
price_fixative = st.sidebar.number_input("Harga Fixative (per ml)", min_value=0, value=3000)
price_bottle = st.sidebar.number_input("Harga Botol + Stiker (per pcs)", min_value=0, value=5000)

# --- TABS UNTUK FITUR ---
tab1, tab2, tab3 = st.tabs(["📊 Hitung HPP & Saran Harga Jual", "🔮 AI Filosofi & Notes Parfum", "🤖 Optimasi Stok"])

with tab1:
    st.header("Formulasi, HPP & Strategi Harga Jual")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⚙️ Parameter Produksi")
        target_bottles = st.number_input("Target Jumlah Botol", min_value=1, value=10)
        bottle_size = st.number_input("Ukuran Botol (ml)", min_value=5, value=50)
        
        st.markdown("---")
        st.subheader("🎯 Target Keuntungan & Harga")
        pricing_method = st.radio("Metode Penentuan Harga Jual:", ["Target Markup (Kenaikan dari Modal)", "Target Margin Laba Kotor (%)"])
        
        if pricing_method == "Target Markup (Kenaikan dari Modal)":
            markup_pct = st.slider("Persentase Kenaikan Harga (%)", 50, 500, 200, step=10)
        else:
            margin_pct = st.slider("Target Margin Laba Kotor (%)", 10, 90, 60, step=5)
        
    with col2:
        st.subheader("🧪 Rasio Konsentrasi Parfum")
        pct_fragrance = st.slider("Persentase Bibit Parfum (%)", 0, 100, 30)
        pct_fixative = st.slider("Persentase Fixative (%)", 0, 10, 2)
        pct_solvent = 100 - (pct_fragrance + pct_fixative)
        
        if pct_solvent < 0:
            st.error("⚠️ Total persentase melebihi 100%! Kurangi bibit atau fixative.")
            pct_solvent = 0
        else:
            st.info(f"Persentase Pelarut Otomatis: {pct_solvent}%")

    # Kalkulasi Finansial
    total_volume_needed = target_bottles * bottle_size
    req_fragrance = (pct_fragrance / 100) * total_volume_needed
    req_solvent = (pct_solvent / 100) * total_volume_needed
    req_fixative = (pct_fixative / 100) * total_volume_needed
    
    cost_fragrance = req_fragrance * price_fragrance
    cost_solvent = req_solvent * price_solvent
    cost_fixative = req_fixative * price_fixative
    cost_bottles = target_bottles * price_bottle
    
    total_cost = cost_fragrance + cost_solvent + cost_fixative + cost_bottles
    hpp_per_bottle = total_cost / target_bottles if target_bottles > 0 else 0

    if pricing_method == "Target Markup (Kenaikan dari Modal)":
        suggested_price = hpp_per_bottle * (1 + (markup_pct / 100))
    else:
        suggested_price = hpp_per_bottle / (1 - (margin_pct / 100)) if margin_pct < 100 else hpp_per_bottle

    total_revenue = suggested_price * target_bottles
    total_profit = total_revenue - total_cost

    st.markdown("---")
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.write(f"**Detail Kebutuhan Bahan (Total: {total_volume_needed} ml):**")
        st.write(f"* 🧪 Bibit Parfum: **{req_fragrance:.1f} ml**")
        st.write(f"* 💧 Pelarut/Alkohol: **{req_solvent:.1f} ml**")
        st.write(f"* ⚗️ Fixative: **{req_fixative:.1f} ml**")
        
    with res_col2:
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
    st.write("Gunakan AI untuk menciptakan nama, filosofi mendalam, serta struktur *notes* parfum Anda.")
    
    if not api_key:
        st.warning("⚠️ Silakan masukkan Google Gemini API Key di sidebar sebelah kiri untuk menggunakan fitur AI ini.")
    else:
        # Input karakteristik aroma dari user
        aroma_type = st.multiselect(
            "Pilih Karakter Utama Aroma Parfum Anda:",
            ["Manis (Sweet/Vanilla)", "Segar/Buah (Fresh/Citrus/Fruit)", "Bunga (Floral)", "Kayu-kayuan (Woody/Oud)", "Rempah (Spicy)", "Mewah/Eksklusif", "Menenangkan (Calm/Powdery)", "Maskulin/Sporty", "Feminin/Anggun"]
        )
        
        target_pasar = st.text_input("Siapa target konsumennya? (Contoh: Wanita karir urban, Anak muda skena, Pria kantoran formal)")
        catatan_tambahan = st.text_area("Catatan Tambahan untuk AI (Contoh: Ingin ada kesan aroma kopi setelah hujan, atau aroma teh melati mewah)")
        
        if st.button("✨ Generasikan Filosofi & Notes"):
            if not aroma_type:
                st.error("Pilih minimal satu karakter utama aroma!")
            else:
                with st.spinner("AI sedang meracik cerita dan filosofi untuk parfum Anda..."):
                    try:
                        # Inisialisasi client Gemini versi terbaru
                        client = genai.Client(api_key=api_key)
                        
                        # Menyusun prompt instruksi untuk AI
                        prompt = f"""
                        Kamu adalah seorang Ahli Peracik Parfum (Perfumer) Internasional dan Brand Strategist handal.
                        Buatkan konsep parfum komersial yang menarik berdasarkan data berikut:
                        - Karakter Aroma: {', '.join(aroma_type)}
                        - Target Pasar: {target_pasar if target_pasar else 'Umum'}
                        - Inspirasi/Catatan Khusus: {catatan_tambahan if catatan_tambahan else 'Tidak ada'}
                        
                        Berikan output dengan format Markdown yang rapi:
                        1. **Rekomendasi Nama Parfum** (Berikan 3 opsi nama yang komersial, modern, dan unik beserta artinya singkat).
                        2. **Filosofi Parfum** (Sebuah narasi cerita/filosofi puitis yang mendalam tentang makna di balik keharuman parfum ini, sangat cocok untuk deskripsi jualan atau konten marketing).
                        3. **Rincian Parfum Notes**: Break down aroma ini secara logis dan harmonis ke dalam:
                           - *Top Notes* (Aroma yang pertama kali tercium saat disemprot)
                           - *Heart/Middle Notes* (Inti dari karakter parfum setelah beberapa menit)
                           - *Base Notes* (Aroma dasar yang tertinggal paling lama dan mengunci keharuman)
                        """
                        
                        # Memanggil model Gemini 2.5 Flash yang cepat dan cerdas
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt,
                        )
                        
                        st.markdown("---")
                        st.success("🎉 Konsep Parfum Berhasil Dibuat!")
                        st.markdown(response.text)
                        
                    except Exception as e:
                        st.error(f"Terjadi kesalahan saat menghubungi AI: {e}")

with tab3:
    st.header("Smart Stock Optimizer")
    # (Kode pencarian bottleneck sisa stok tetap sama seperti versi sebelumnya)
    stok_fragrance = st.number_input("Sisa Stok Bibit Parfum (ml)", min_value=0.0, value=500.0)
    stok_solvent = st.number_input("Sisa Stok Pelarut (ml)", min_value=0.0, value=1000.0)
    stok_fixative = st.number_input("Sisa Stok Fixative (ml)", min_value=0.0, value=100.0)
    target_size = st.selectbox("Pilih Ukuran Botol Target (ml)", [30, 50, 100], index=1)
    
    vol_fragrance_per_bottle = (pct_fragrance / 100) * target_size
    vol_solvent_per_bottle = (pct_solvent / 100) * target_size
    vol_fixative_per_bottle = (pct_fixative / 100) * target_size
    
    max_by_fragrance = stok_fragrance // vol_fragrance_per_bottle if vol_fragrance_per_bottle > 0 else 0
    max_by_solvent = stok_solvent // vol_solvent_per_bottle if vol_solvent_per_bottle > 0 else 0
    max_by_fixative = stok_fixative // vol_fixative_per_bottle if vol_fixative_per_bottle > 0 else 0
    
    max_production = int(min(max_by_fragrance, max_by_solvent, max_by_fixative))
    
    st.markdown("---")
    st.success(f"Anda dapat meracik maksimal **{max_production} botol** ukuran {target_size} ml.")
