import streamlit as st
import re
import time
import base64
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Universal to ID V7.8")
st.title("Universal to ID V7.8 - Support \"\\\"")
st.error("HANYA TEKS DALAM \"...\" YANG DITERJEMAHKAN. Termasuk \"\\\" ")

file = st.file_uploader("Upload file.rpy", type=["rpy"])

def protect(text):
    tags = re.findall(r'\{[^}]*\}|\[[^\]]*\]|\\[nrtw"\\]|\.\.|~|\bnone\b', text, flags=re.IGNORECASE)
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
    skipped = 0

    with st.status("1. Scan support \"\\\"...") as s:
        for idx, line in enumerate(lines):
            # REGEX BARU: BISA BACA \" DI DALEM
            matches = re.finditer(r'"((?:[^"\\]|\\.)*)"', line)
            for m in matches:
                original_text = m.group(1)
                if not original_text.strip() or original_text.strip().lower() == "none":
                    skipped += 1
                    continue
                clean_text, tags = protect(original_text)
                if clean_text.strip():
                    batch.append(clean_text)
                    batch_index.append((idx, m.start(1), m.end(1), tags))

        s.update(label=f"2. Nemu {len(batch)} teks. Skip {skipped}", state="running")

    # TRANSLATE
    progress = st.progress(0)
    for i in range(0, len(batch), 100):
        chunk = batch[i:i+100]
        chunk_idx = batch_index[i:i+100]
        try:
            results = GoogleTranslator(source='auto', target='id').translate_batch(chunk)
        except:
            results = chunk
            time.sleep(5)

        for (idx, start, end, tags), result in zip(chunk_idx, results):
            final_text = unprotect(result, tags)
            line = lines[idx]
            lines[idx] = line[:start+1] + final_text + line[end+1:]

        progress.progress((i + 100) / len(batch))
        time.sleep(1.5)

    final_content = '\n'.join(lines)
    s.update(label="Selesai!", state="complete")
    st.success(f"Selesai! {len(batch)} teks diterjemahkan")

    st.markdown(get_download_link(final_content, "ID_V78_" + file.name), unsafe_allow_html=True)

st.caption("Contoh: e \"Dia bilang \\\"halo\\\"\" -> e \"Dia bilang \\\"halo\\\"\"")
