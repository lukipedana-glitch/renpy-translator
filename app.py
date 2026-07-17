import streamlit as st
import re
from deep_translator import GoogleTranslator

# Fungsi inisialisasi penerjemah modern
def translate_rpy(content, target_lang='id'):
    lines = content.split('\n')
    translated_lines = []
    
    # Inisialisasi GoogleTranslator dari deep-translator
    translator = GoogleTranslator(source='auto', target=target_lang)
    
    # Regex untuk Ren'Py
    dialog_pattern = re.compile(r'^(\s*(?:\w+\s+)?)["\']([^"\']+)["\']\s*$')

    for line in lines:
        match = dialog_pattern.match(line)
        if match:
            prefix = match.group(1) 
            text_to_translate = match.group(2) 
            try:
                # Proses terjemahan menggunakan library baru
                translated_text = translator.translate(text_to_translate)
                translated_lines.append(f'{prefix}"{translated_text}"')
            except Exception as e:
                translated_lines.append(line)
        else:
            translated_lines.append(line)
    return '\n'.join(translated_lines)

# UI Streamlit
st.title("Ren'Py (.rpy) Translator Web App")
st.write("Unggah file .rpy Anda dan terjemahkan dialognya secara otomatis.")

# Pilihan Bahasa (Kode bahasa sama)
lang_options = {'Indonesia': 'id', 'Inggris': 'en', 'Jepang': 'ja', 'Spanyol': 'es'}
selected_lang = st.selectbox("Pilih Bahasa Target:", list(lang_options.keys()))
target_code = lang_options[selected_lang]

# Upload File
uploaded_file = st.file_uploader("Pilih file .rpy", type=["rpy"])

if uploaded_file is not None:
    file_contents = uploaded_file.getvalue().decode("utf-8")
    if st.button("Mulai Terjemahkan"):
        with st.spinner("Sedang menerjemahkan... Mohon tunggu."):
            result = translate_rpy(file_contents, target_code)
            st.success("Penerjemahan selesai!")
            st.download_button(
                label="Unduh File Terjemahan",
                data=result,
                file_name=f"translated_{uploaded_file.name}",
                mime="text/plain"
            )

uploaded_file = st.file_uploader("Pilih file .rpy", type=["rpy"])

if uploaded_file is not None:
    file_contents = uploaded_file.getvalue().decode("utf-8")
    if st.button("Mulai Terjemahkan"):
        with st.spinner("Sedang menerjemahkan... Mohon tunggu."):
            result = translate_rpy(file_contents, target_code)
            st.success("Penerjemahan selesai!")
            st.download_button(
                label="Unduh File Terjemahan",
                data=result,
                file_name=f"translated_{uploaded_file.name}",
                mime="text/plain"
            )
