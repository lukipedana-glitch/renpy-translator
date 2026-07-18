import streamlit as st
import re
from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor

def make_it_casual(text):
    """
    Mengubah kata-kata kaku formal bawaan mesin translator 
    menjadi bahasa gaul santai sehari-hari di dunia nyata.
    """
    if not text or not isinstance(text, str):
        return text
        
    casual_dictionary = {
        r'\bAnda\b': 'kamu',
        r'\bSaya\b': 'aku',
        r'\bTidak\b': 'nggak',
        r'\bApakah\b': 'apa',
        r'\bBenar\b': 'bener',
        r'\bSangat\b': 'banget',
        r'\bMengapa\b': 'kenapa',
        r'\bBagaimana\b': 'gimana',
        r'\bTetapi\b': 'tapi',
        r'\bNamun\b': 'tapi',
        r'\bBisa\b': 'bisa',
        r'\bAkan\b': 'bakal',
        r'\bMelihat\b': 'liat',
        r'\bSudah\b': 'udah',
        r'\bSaja\b': 'aja',
        r'\bBukan\b': 'bukan',
        r'\bPergi\b': 'pergi',
        r'\bKembali\b': 'balik',
        r'\bUang\b': 'duit',
        r'\bTeman\b': 'temen',
        r'\bAyah\b': 'bokap',
        r'\bIbu\b': 'nyokap',
    }
    
    for formal, casual in casual_dictionary.items():
        text = re.sub(formal, casual, text, flags=re.IGNORECASE)
        
    return text

def clean_strictly_for_joiplay(text):
    """
    SISTEM PROTEKSI UTAMA JOIPLAY:
    Menghapus dan menetralkan tanda kutip dua internal agar Joiplay tidak menutup paksa.
    """
    if not text:
        return ""
    # Menghapus kutip dua dekoratif bawaan keyboard HP / Google Translate menjadi kutip satu
    text = text.replace('“', "'").replace('”', "'").replace('„', "'")
    text = text.replace('"', "'")
    text = text.replace('%', ' persen').replace('\\', '/')
    return text.strip()

def translate_single_item(data, target_lang):
    """
    Fungsi pekerja paralel untuk mengekstrak arti teks Spanyol secara mandiri
    """
    try:
        # source='auto' sangat peka membaca aksen Spanyol (ñ, ¿, ¡, á, é)
        translator = GoogleTranslator(source='auto', target=target_lang)
        raw_translation = translator.translate(data['text'])
        
        casual_text = make_it_casual(raw_translation)
        safe_text = clean_strictly_for_joiplay(casual_text)
        
        return {'line_idx': data['line_idx'], 'result': f'{data["prefix"]}"{safe_text}"{data["suffix"]}'}
    except:
        # Jika baris ini gagal karena gangguan jaringan, kembalikan teks asli murni agar file tidak korup
        return {'line_idx': data['line_idx'], 'result': f'{data["prefix"]}"{data["text"]}"{data["suffix"]}'}

def translate_rpy_turbo_final(content, target_lang='id'):
    lines = content.split('\n')
    
    # REGEX COCOK: Membagi baris menjadi (Luar_Depan) "Teks_Dalam" (Luar_Belakang)
    # Non-greedy (.*?) menjamin aksen Spanyol terjaring akurat tanpa merusak sintaks luar program Ren'Py
    dialog_pattern = re.compile(r'^([^"\n]*?)"([^"\n]*?)"([^"\n]*?)$')
    dialog_data = []
    
    # LANGKAH 1: Kumpulkan semua data dialog
    for idx, line in enumerate(lines):
        match = dialog_pattern.match(line)
        if match:
            text_inside = match.group(2)
            if text_inside.strip(): 
                dialog_data.append({
                    'line_idx': idx,
                    'text': text_inside,
                    'prefix': match.group(1),
                    'suffix': match.group(3)
                })
                
    if not dialog_data:
        return content

    # LANGKAH 2: Multi-Threading Turbo Execution (Pemrosesan Paralel Berkelompok)
    progress_bar = st.progress(0)
    st.write(f"Berhasil mengunci {len(dialog_data)} baris dialog Spanyol! Memulai akselerasi multi-thread...")
    
    processed_count = 0
    total_dialogs = len(dialog_data)
    batch_size = 100  # Mengelompokkan per 100 baris agar server stabil tanpa terkena rate limit
    
    for i in range(0, total_dialogs, batch_size):
        batch = dialog_data[i:i + batch_size]
        
        # max_workers=10 berarti server memproses 10 baris dialog sekaligus secara bersamaan dalam 1 detik
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(translate_single_item, data, target_lang) for data in batch]
            
            for future in futures:
                res_data = future.result()
                lines[res_data['line_idx']] = res_data['result']
                
                processed_count += 1
                if processed_count % 10 == 0 or processed_count == total_dialogs:
                    progress_bar.progress(processed_count / total_dialogs)
            
    return '\n'.join(lines)

st.title("Ren'Py Translator - TURBO PARALEL EDITION v4 🏎️⚡")
st.write("Hanya menerjemahkan isi tanda kutip dua. Menggunakan deep-translator paralel, instan, otomatis bahasa gaul, dan Joiplay anti-crash.")

# Menggunakan daftar opsi bahasa dengan kode ISO standar milik deep-translator
lang_options = {'Indonesia': 'id', 'Inggris': 'en', 'Jepang': 'ja'}
selected_lang = st.selectbox("Pilih Bahasa Target:", list(lang_options.keys()))
target_code = lang_options[selected_lang]

uploaded_file = st.file_uploader("Pilih file .rpy", type=["rpy"])

if uploaded_file is not None:
    file_contents = uploaded_file.getvalue().decode("utf-8")
    if st.button("Mulai Akselerasi Terjemahan"):
        with st.spinner("Membongkar aksen Spanyol ke bahasa gaul Indonesia... Mohon tunggu."):
            result = translate_rpy_turbo_final(file_contents, target_code)
            st.success("Selesai total! File diproteksi penuh dari Joiplay Force Close.")
            
            # Memaksa file keluaran berformat UTF-8-BOM untuk kelancaran Joiplay di Android
            bom_result = '\ufeff' + result
            st.download_button(
                label="Unduh File Terjemahan Joiplay",
                data=bom_result.encode('utf-8'),
                file_name=f"translated_{uploaded_file.name}",
                mime="text/plain"
            )
