import streamlit as st
import re
from deep_translator import GoogleTranslator

st.set_page_config(page_title="RenPy Translator V6", layout="wide")
st.title("RenPy Translator V6 - Anti FC Pro")
st.write("Translate.rpy aman. Tag {sc=3} {i} {color} tidak akan rusak")

file = st.file_uploader("Upload file.rpy", type=["rpy"])

lang_map = {"id": "Bahasa Indonesia", "es": "Espanol", "en": "English", "jp": "Japanese"}
lang = st.selectbox("Pilih Bahasa Tujuan:", list(lang_map.keys()), format_func=lambda x: lang_map[x])

if file and st.button("MULAI TRANSLATE"):
    content = file.read().decode('utf-8', errors='ignore')
    lines = content.split('\n')
    out = []
    progress = st.progress(0)

    for idx, line in enumerate(lines):
        m = re.match(r'^(\s*\w*\s*)"((?:[^"\\]|\\.)*)"(.*)$', line)
        if m:
            text = m.group(2)
            # Proteksi tag { } [ ] \n
            tags = re.findall(r'\{[^}]*\}|\[[^\]]*\]|\\.|~', text)
            for i,t in enumerate(tags):
                text = text.replace(t, f'@@TAG{i}@@')
            # Translate
            try:
                hasil = GoogleTranslator(source='auto', target=lang).translate(text)
                for i,t in enumerate(tags):
                    hasil = hasil.replace(f'@@TAG{i}@@', t)
            except:
                hasil = text
            out.append(f'{m.group(1)}"{hasil}"{m.group(3)}')
        else:
            out.append(line)
        progress.progress((idx + 1) / len(lines))

    st.success("Selesai!")
    st.download_button("DOWNLOAD HASIL", '\n'.join(out), f"{lang.upper()}_" + file.name)

st.info("Cara Pakai: Upload > Pilih Bahasa > Download > Pindah ke game/tl/Spanish/")
