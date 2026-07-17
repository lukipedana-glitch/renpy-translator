import streamlit as st
import re
from deep_translator import GoogleTranslator

def translate_rpy_safe_and_fast(content, target_lang='id'):
    lines = content.split('\n')
    
    # Regex akurat: Hanya mengambil teks di dalam kutip dua ("...")
    dialog_pattern = re.compile(r'^([^"\n]*)"([^"\n]+)"([^"\n]*)$')
    
    dialog_data = []
    
    # LANGKAH 1: Kumpulkan semua data dialog
    for idx, line in enumerate(lines):
        match = dialog_pattern.match(line)
        if match:
            text_inside = match.group(2)
            if text_inside.strip():  # Abaikan kutip kosong
                dialog_data.append({
                    'line_idx': idx,
                    'text': text_inside,
                    'prefix': match.group(1),
                    'suffix': match.group(3)
                })
                
    if not dialog_data:
        return content

    # LANGKAH 2: Proses kirim massal menggunakan daftar terisolasi (Batch Slicing)
    # Kita bagi menjadi kelompok kecil berisi 50 dialog agar Google tidak overload dan tetap kilat
    batch_size = 50
    translator = GoogleTranslator(source='auto', target=target_lang)
    
    # Ekstrak hanya teksnya saja untuk dikirim ke translator
    all_texts = [data['text'] for data in dialog_data]
    translated_texts = []
    
    progress_bar = st.progress(0)
    total_batches = (len(all_texts) + batch_size - 1) // batch_size

    for i in range(0, len(all_texts), batch_size):
        batch = all_texts[i:i + batch_size]
        try:
            # Mengirimkan list murni tanpa simbol pemisah buatan yang rawan rusak
            translated_batch = translator.translate_batch(batch)
            translated_texts.extend(translated_batch)
        except Exception as e:
            # Jika batch ini gagal, gunakan teks asli agar game tidak crash
            st.warning(f"Ada kendala di baris {i}, menggunakan teks asli untuk bagian ini.")
            translated_texts.extend(batch)
            
        # Update progress bar
        current_batch_idx = i // batch_size
        progress_bar.progress((current_batch_idx + 1) / total_batches)

    # LANGKAH 3: Tulis kembali hasil terjemahan ke dalam file .rpy
    # Karena strukturnya terisolasi, posisi baris dijamin 100% presisi dengan game asli
    for idx, data in enumerate(dialog_data):
        line_idx = data['line_idx']
        prefix = data['prefix']
        suffix = data['suffix']
        new_text = translated_texts[idx]
        
        # Kembalikan ke dalam kutip dua, bagian luar kutip tidak disentuh
        lines[line_idx] = f'{prefix}"{new_text}"{suffix}'
            
    return '\n'.join(lines)

st.title("Ren'Py (.rpy) Translator - SAFE BATCH MODE 🛡️⚡")
st.write("Versi Anti-Crash: Menggunakan isolasi list murni agar struktur internal game tidak rusak dan tetap cepat.")

lang_options = {'Indonesia': 'id', 'Inggris': 'en', 'Jepang': 'ja', 'Spanyol': 'es'}
selected_lang = st.selectbox("Pilih Bahasa Target:", list(lang_options.keys()))
target_code = lang_options[selected_lang]

uploaded_file = st.file_uploader("Pilih file .rpy", type=["rpy"])

if uploaded_file is not None:
    file_contents = uploaded_file.getvalue().decode("utf-8")
    if st.button("Mulai Terjemahkan Aman & Cepat"):
        with st.spinner("Menerjemahkan dengan metode isolasi batch... Mohon tunggu."):
            result = translate_rpy_safe_and_fast(file_contents, target_code)
            st.success("Penerjemahan selesai!")
            st.download_button(
                label="Unduh File Terjemahan",
                data=result,
                file_name=f"translated_{uploaded_file.name}",
                mime="text/plain"
            )
