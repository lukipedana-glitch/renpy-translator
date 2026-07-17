import streamlit as st
import re
from deep_translator import GoogleTranslator

def translate_rpy_fast_and_accurate(content, target_lang='id'):
    lines = content.split('\n')
    
    # Regex super akurat: Hanya menangkap apa yang ada di dalam tanda kutip dua pertama dan terakhir pada baris dialog
    # Group 1: Kode/Nama di luar kutip (termasuk spasi)
    # Group 2: Teks asli di dalam kutip dua yang AKAN diterjemahkan
    # Group 3: Sisa karakter setelah kutip dua penutup (jika ada)
    dialog_pattern = re.compile(r'^([^"\n]*)"([^"\n]+)"([^"\n]*)$')
    
    texts_to_translate = []
    saved_matches = []
    
    # LANGKAH 1: Kumpulkan teks di dalam kutip secara kilat
    for idx, line in enumerate(lines):
        match = dialog_pattern.match(line)
        if match:
            text_inside = match.group(2)
            if text_inside.strip(): # Pastikan bukan kutip kosong
                texts_to_translate.append(text_inside)
                saved_matches.append({
                    'line_idx': idx,
                    'prefix': match.group(1),
                    'suffix': match.group(3)
                })
                
    if not texts_to_translate:
        return content

    # LANGKAH 2: Kirim massal ke Google Translator (Sangat Cepat & Hemat Request)
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        # Fungsi translate_batch mengirimkan list teks sekaligus dalam satu paket data
        translated_texts = translator.translate_batch(texts_to_translate)
        
        # LANGKAH 3: Rakit kembali teks terjemahan ke baris aslinya
        for i, match_info in enumerate(saved_matches):
            idx = match_info['line_idx']
            prefix = match_info['prefix']
            suffix = match_info['suffix']
            new_text = translated_texts[i]
            
            # Gabungkan kembali: Luar_Kutip + "Hasil_Terjemahan" + Sisa_Luar_Kutip
            lines[idx] = f'{prefix}"{new_text}"{suffix}'
            
    except Exception as e:
        st.error(f"Gagal memproses batch: {e}. Menggunakan mode aman otomatis...")
        # Cadangan jika batch error, terjemahkan sisa per baris
        translator = GoogleTranslator(source='auto', target=target_lang)
        for match_info in saved_matches:
            idx = match_info['line_idx']
            prefix = match_info['prefix']
            suffix = match_info['suffix']
            try:
                original_text = lines[idx].split('"')[1]
                lines[idx] = f'{prefix}"{translator.translate(original_text)}"{suffix}'
            except:
                pass
                
    return '\n'.join(lines)

st.title("Ren'Py (.rpy) Translator - KILAT & AKURAT ⚡")
st.write("Hanya menerjemahkan teks di dalam simbol \"...\". Nama karakter dan perintah kode di luar simbol dijamin aman.")

lang_options = {'Indonesia': 'id', 'Inggris': 'en', 'Jepang': 'ja', 'Spanyol': 'es'}
selected_lang = st.selectbox("Pilih Bahasa Target:", list(lang_options.keys()))
target_code = lang_options[selected_lang]

uploaded_file = st.file_uploader("Pilih file .rpy", type=["rpy"])

if uploaded_file is not None:
    file_contents = uploaded_file.getvalue().decode("utf-8")
    if st.button("Mulai Terjemahkan Kilat"):
        with st.spinner("Sedang memproses dokumen dengan kecepatan tinggi..."):
            result = translate_rpy_fast_and_accurate(file_contents, target_code)
            st.success("Penerjemahan selesai!")
            st.download_button(
                label="Unduh File Terjemahan",
                data=result,
                file_name=f"translated_{uploaded_file.name}",
                mime="text/plain"
            )
