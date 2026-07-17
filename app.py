import streamlit as st
import re
from deep_translator import GoogleTranslator

def translate_rpy_mega_fast(content, target_lang='id'):
    lines = content.split('\n')
    
    # Regex akurat: Group 1 = luar kutip depan, Group 2 = teks dalam kutip, Group 3 = luar kutip belakang
    dialog_pattern = re.compile(r'^([^"\n]*)"([^"\n]+)"([^"\n]*)$')
    
    dialog_data = []
    
    # LANGKAH 1: Kumpulkan semua teks di dalam kutip ganda
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

    # LANGKAH 2: Satukan menjadi chunk besar (< 4500 karakter) agar proses kirim ke Google instan
    chunks = []
    current_chunk = []
    current_length = 0
    separator = " ||| " 
    
    for data in dialog_data:
        added_length = len(data['text']) + len(separator)
        if current_length + added_length > 4500:
            chunks.append(current_chunk)
            current_chunk = [data]
            current_length = len(data['text'])
        else:
            current_chunk.append(data)
            current_length += added_length
            
    if current_chunk:
        chunks.append(current_chunk)

    # LANGKAH 3: Kirim balok teks besar ke Google Translator
    translator = GoogleTranslator(source='auto', target=target_lang)
    
    for chunk in chunks:
        # Satukan teks dalam chunk dengan pemisah |||
        combined_text = separator.join([data['text'] for data in chunk])
        try:
            # Terjemahkan satu paragraf besar sekaligus (sangat cepat)
            translated_combined = translator.translate(combined_text)
            # Pisahkan kembali hasilnya berdasarkan pemisah
            translated_list = translated_combined.split(separator)
            
            # Jika jumlah potongannya pas, masukkan kembali tepat ke dalam kutip dua
            if len(translated_list) == len(chunk):
                for i, data in enumerate(chunk):
                    idx = data['line_idx']
                    prefix = data['prefix']
                    suffix = data['suffix']
                    # Ganti baris asli: teks luar kutip tidak disentuh, teks dalam kutip diperbarui
                    lines[idx] = f'{prefix}"{translated_list[i].strip()}"{suffix}'
            else:
                # Mode cadangan darurat khusus untuk chunk ini jika pemisah dirusak oleh Google
                for data in chunk:
                    try:
                        idx = data['line_idx']
                        lines[idx] = f'{data["prefix"]}"{translator.translate(data["text"])}"{data["suffix"]}'
                    except:
                        pass
        except:
            # Jika gagal total, biarkan baris teks aslinya aman
            pass
            
    return '\n'.join(lines)

st.title("Ren'Py (.rpy) Translator - MEGA FAST & ACCURATE ⚡")
st.write("Sistem Pemrosesan Balok Teks: Hanya menerjemahkan isi di dalam kutip dua dengan kecepatan maksimal.")

lang_options = {'Indonesia': 'id', 'Inggris': 'en', 'Jepang': 'ja', 'Spanyol': 'es'}
selected_lang = st.selectbox("Pilih Bahasa Target:", list(lang_options.keys()))
target_code = lang_options[selected_lang]

uploaded_file = st.file_uploader("Pilih file .rpy", type=["rpy"])

if uploaded_file is not None:
    file_contents = uploaded_file.getvalue().decode("utf-8")
    if st.button("Mulai Terjemahkan Super Kilat"):
        with st.spinner("Menerjemahkan ribuan baris dalam beberapa detik..."):
            result = translate_rpy_mega_fast(file_contents, target_code)
            st.success("Penerjemahan selesai!")
            st.download_button(
                label="Unduh File Terjemahan",
                data=result,
                file_name=f"translated_{uploaded_file.name}",
                mime="text/plain"
            )
