import streamlit as st
import re
from deep_translator import GoogleTranslator

def translate_rpy_ultra_fast(content, target_lang='id'):
    lines = content.split('\n')
    dialog_pattern = re.compile(r'^(\s*(?:\w+\s+)?)["\']([^"\']+)["\']\s*$')
    
    # Kumpulan data dialog
    dialog_data = []
    
    # Langkah 1: Ekstrak semua dialog yang valid
    for idx, line in enumerate(lines):
        match = dialog_pattern.match(line)
        if match:
            text = match.group(2)
            if text.strip():  # Abaikan teks kosong
                dialog_data.append({'index': idx, 'text': text, 'prefix': match.group(1)})
                
    if not dialog_data:
        return content

    # Langkah 2: Gabungkan dialog menjadi blok-blok besar (Chunking) < 4500 karakter
    chunks = []
    current_chunk = []
    current_length = 0
    
    # Gunakan separator unik yang aman dari karakter normal game
    separator = " ||| " 
    
    for data in dialog_data:
        # Estimasi panjang jika teks digabungkan
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

    # Langkah 3: Kirim blok besar tersebut ke Google Translator
    translator = GoogleTranslator(source='auto', target=target_lang)
    progress_bar = st.progress(0)
    total_chunks = len(chunks)
    
    for chunk_idx, chunk in enumerate(chunks):
        # Gabungkan teks dalam satu chunk menjadi satu string tunggal
        combined_text = separator.join([data['text'] for data in chunk])
        try:
            translated_combined = translator.translate(combined_text)
            # Pisahkan kembali hasil terjemahan berdasarkan separator
            translated_list = translated_combined.split(separator)
            
            # Jika jumlah teks cocok, masukkan kembali ke baris asli file
            if len(translated_list) == len(chunk):
                for i, data in enumerate(chunk):
                    lines[data['index']] = f'{data["prefix"]}"{translated_list[i].strip()}"'
            else:
                # Mode aman cadangan jika separator rusak (diterjemahkan per baris khusus chunk ini)
                for data in chunk:
                    try:
                        lines[data['index']] = f'{data["prefix"]}"{translator.translate(data["text"])}"'
                    except:
                        pass
        except Exception as e:
            # Jika chunk gagal total, biarkan baris aslinya agar file tidak rusak
            pass
            
        # Update bar progress di layar HP
        progress_bar.progress((chunk_idx + 1) / total_chunks)
        
    return '\n'.join(lines)

st.title("Ren'Py (.rpy) Translator - ULTRA FAST MODE ⚡")
st.write("Menggunakan sistem enkapsulasi teks untuk memangkas waktu tunggu hingga 90%.")

lang_options = {'Indonesia': 'id', 'Inggris': 'en', 'Jepang': 'ja', 'Spanyol': 'es'}
selected_lang = st.selectbox("Pilih Bahasa Target:", list(lang_options.keys()))
target_code = lang_options[selected_lang]

uploaded_file = st.file_uploader("Pilih file .rpy", type=["rpy"])

if uploaded_file is not None:
    file_contents = uploaded_file.getvalue().decode("utf-8")
    if st.button("Mulai Terjemahkan Kilat"):
        with st.spinner("Sedang memproses dokumen massal... Mohon tunggu."):
            result = translate_rpy_ultra_fast(file_contents, target_code)
            st.success("Penerjemahan selesai!")
            st.download_button(
                label="Unduh File Terjemahan",
                data=result,
                file_name=f"translated_{uploaded_file.name}",
                mime="text/plain"
            )
