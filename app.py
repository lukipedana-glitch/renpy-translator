import streamlit as st
from deep_translator import GoogleTranslator
import re, time, io

st.set_page_config(page_title="RenPy Translator", layout="wide")
st.title("🌏 Translator.rpy Anti FC buat Joiplay")

uploaded_file = st.file_uploader("Upload file.rpy kamu", type=["rpy"])
target_lang = st.selectbox("Translate ke bahasa:", ["id", "en", "ja", "ko", "zh-CN"])

def protect_and_clean(text):
    tags = re.findall(r'\{.*?\}', text)
    for i, tag in enumerate(tags): text = text.replace(tag, f'@@TAG{i}@@')
    text = text.replace('"', "'").replace('%', ' persen').replace('\\', '/')
    for i, tag in enumerate(tags): text = text.replace(f'@@TAG{i}@@', tag)
    return text

def make_it_casual(text):
    kamus = {r'\bAnda\b': 'kamu', r'\bSaya\b': 'aku', r'\bTidak\b': 'nggak', r'\bSangat\b': 'banget'}
    for k, v in kamus.items(): text = re.sub(k, v, text, flags=re.IGNORECASE)
    return text

if uploaded_file is not None:
    if st.button("Mulai Translate"):
        with st.spinner("Lagi translate... 1-5 menit"):
            content = uploaded_file.read().decode('utf-8', errors='ignore')
            lines = content.split('\n')
            pattern = re.compile(r'^(\s*[a-zA-Z0-9_#]*\s*)"([^"]*?)"(.*)$')
            translator = GoogleTranslator(source='auto', target=target_lang)
            count = 0
            progress = st.progress(0)

            for i, line in enumerate(lines):
                m = pattern.match(line)
                if m and m.group(2).strip():
                    try:
                        text = protect_and_clean(m.group(2))
                        hasil = translator.translate(text)
                        hasil = make_it_casual(hasil)
                        lines[i] = f'{m.group(1)}"{hasil}"{m.group(3)}'
                        count += 1
                    except:
                        time.sleep(2)
                progress.progress(i / len(lines))

            output = '\n'.join(lines)
            st.success(f"SELESAI! {count} baris diterjemahkan")
            
            st.download_button(
                label="Download Hasil.rpy",
                data=output,
                file_name="ID_" + uploaded_file.name,
                mime="text/plain"
    )
