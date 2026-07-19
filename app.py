import streamlit as st, re, time
from deep_translator import GoogleTranslator

st.set_page_config(page_title="RenPy Translator V6", layout="wide")

st.title("🌏 RenPy Translator V6 - Anti FC Pro")
st.caption("Translate.rpy aman. Tag {sc=3} {i} {color} gak bakal rusak lagi")

col1, col2 = st.columns([2,1])

with col1:
    file = st.file_uploader("📂 Upload file.rpy kamu", type=["rpy"])
with col2:
    lang = st.selectbox(
        "🌐 Translate ke bahasa:",
        {"id": "Bahasa Indonesia", "es": "Español", "en": "English", "jp": "日本語", "kr": "한국어"},
        format_func=lambda x: {"id": "Bahasa Indonesia", "es": "Español", "en": "English", "jp": "日本語", "kr": "한국어"}[x]
    )

if file and st.button("🚀 MULAI TRANSLATE", use_container_width=True, type="primary"):
    content = file.read().decode('utf-8', errors='ignore')
    lines = content.split('\n')
    out = []
    progress = st.progress(0, text="Mulai translate...")

    for idx, line in enumerate(lines):
        m = re.match(r'^(\s*\w*\s*)"((?:[^"\\]|\\.)*)"(.*)$', line)
        if m:
            text = m.group(2)

            # 1. Proteksi semua tag RenPy biar gak dirusak
            # {sc=3} {/sc} {i} {b} {color=#000} {/color} {w} {nw} [ ] \n \~
            tags = re.findall(r'\{[^}]*\}|\[[^\]]*\]|\\.|~', text)
            for i,t in enumerate(tags):
                text = text.replace(t, f'@@TAG{i}@@')

            # 2. Translate teks bersih
            try:
                hasil = GoogleTranslator(source='auto', target=lang).translate(text)
                # Balikin tag ke tempat semula
                for i,t in enumerate(tags):
                    hasil = hasil.replace(f'@@TAG{i}@@', t)
            except:
                hasil = text # kalau gagal translate, pake teks asli

            out.append(f'{m.group(1)}"{hasil}"{m.group(3)}')
                                    else:
