import streamlit as st
import re
from googletrans import Translator

@st.cache_resource
def get_translator():
    return Translator(service_urls=['://google.com'])

translator = get_translator()

def translate_rpy(content, target_lang='id'):
    lines = content.split('\n')
    translated_lines = []
    dialog_pattern = re.compile(r'^(\s*(?:\w+\s+)?)["\']([^"\']+)["\']\s*$')

    for line in lines:
        match = dialog_pattern.match(line)
        if match:
            prefix = match.group(1) 
            text_to_translate = match.group(2) 
            try:
                translation = translator.translate(text_to_translate, dest=target_lang)
                translated_text = translation.text
                translated_lines.append(f'{prefix}"{translated_text}"')
            except Exception as e:
                translated_lines.append(line)
        else:
            translated_lines.append(line)
    return '\n'.join(translated_lines)

st.title("Ren'Py (.rpy) Translator Web App")
st.write("Unggah file .rpy Anda dan terjemahkan dialognya secara otomatis.")

lang_options = {'Indonesia': 'id', 'Inggris': 'en', 'Jepang': 'ja', 'Spanyol': 'es'}
selected_lang = st.selectbox("Pilih Bahasa Target:", list(lang_options.keys()))
target_code = lang_options[selected_lang]

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
