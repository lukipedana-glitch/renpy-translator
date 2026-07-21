import streamlit as st
import re
import time
import base64
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Universal to ID V7.6")
st.title("Universal to ID Translator V7.6 - Fix Download")

file = st.file_uploader("Upload file.rpy", type=["rpy"])

def protect(text):
    tags = re.findall(r'\{[^}]*\}|\[[^\]]*\]|\\[nrt"\\]|\.\.|~|none', text, flags=re.IGNORECASE)
    temp = text
    for i,t in enumerate(tags):
        temp = temp.replace(t, f'@@P{i}@@')
    return temp, tags

def unprotect(text, tags):
    for i,t in enumerate(tags):
        text = text.replace(f'@@P{i}@@', t)
    return text

def get_download_link(content, filename):
    b64 = base64.b64encode(content.encode('utf-8')).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">KLIK UNTUK DOWNLOAD FILE ID</a>'

if file and st.button("TERJEMAHKAN KE INDONESIA", type="primary", use_container_width=True):
    content = file.read().decode('utf-8', errors='ignore')
    lines = content.split('\n')
    batch = []
    batch_index = []

    with st.status("Scan & Translate...") as s:
        for idx, line in enumerate(lines):
            m = re.match(r'^(\s*\w+\s*)"((?:[^"\\]|\\.)*)"(.*)$', line)
            if m:
                prefix, text, suffix = m.groups()
                if text.strip() and text.strip().lower()!= "none":
                    clean_text, tags = protect(text)
                    if clean_text.strip():
                        batch.append(clean_text)
                        batch_index.append((idx, prefix, tags, suffix))

        # Translate per chunk 100
        for i in range(0, len(batch), 100):
            chunk = batch[i:i+100]
            chunk_idx = batch_index[i:i+100]
            try:
                results = GoogleTranslator(source='auto', target='id').translate_batch(chunk)
            except:
                results = chunk
                time.sleep(5)

            for (idx, prefix, tags, suffix), result in zip(chunk_idx, results):
                final_text = unprotect(result, tags)
                lines[idx] = f'{prefix}"{final_text}"{suffix}'
            time.sleep(1.5)

    final_content = '\n'.join(lines)
    s.update(label="Selesai!", state="complete")
    st.success("Selesai! Scroll ke bawah")

    # TOMBOL DOWNLOAD BARU YANG GAK ILANG
    st.markdown(get_download_link(final_content, "ID_V76_" + file.name), unsafe_allow_html=True)
    st.info("Kalau link di atas gak bisa diklik, copy paste ke browser baru")

st.caption("Tag { } \\n... none aman 100%")
