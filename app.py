import streamlit as st
import re
import time
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Universal to ID V7.5")
st.title("Universal to ID Translator V7.5 - Final")
st.write("Terjemah semua bahasa -> Indonesia. 100% jaga tag { } \\n...")

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

if file and st.button("TERJEMAHKAN KE INDONESIA", type="primary", use_container_width=True):
    content = file.read().decode('utf-8', errors='ignore')
    lines = content.split('\n')
    batch = []
    batch_index = []
    error_log = []

    with st.status("1. Scan file...") as s:
        for idx, line in enumerate(lines):
            m = re.match(r'^(\s*\w+\s*)"((?:[^"\\]|\\.)*)"(.*)$', line)
            if m:
                prefix, text, suffix = m.groups()
                if text.strip() and text.strip().lower()!= "none": # SKIP none & kosong
                    clean_text, tags = protect(text)
                    if clean_text.strip():
                        batch.append(clean_text)
                        batch_index.append((idx, prefix, tags, suffix))
        s.update(label=f"2. Nemu {len(batch)} baris. Estimasi: {len(batch)//100 + 1} menit", state="running")

    chunk_size = 100 # naikin biar lebih cepat
    progress = st.progress(0)
    
    for i in range(0, len(batch), chunk_size):
        chunk = batch[i:i+chunk_size]
        chunk_idx = batch_index[i:i+chunk_size]
        
        for attempt in range(3):
            try:
                results = GoogleTranslator(source='auto', target='id').translate_batch(chunk)
                break
            except Exception as e:
                if attempt == 2: 
                    error_log.append(f"Chunk {i}-{i+chunk_size} gagal. Pake teks asli")
                    results = chunk
                time.sleep(5)
        
        for (idx, prefix, tags, suffix), result in zip(chunk_idx, results):
            try:
                final_text = unprotect(result, tags)
                # Cek kesehatan tag
                if final_text.count('{')!= final_text.count('}'):
                    final_text = unprotect(batch[batch_index.index((idx, prefix, tags, suffix))], tags)
                    error_log.append(f"Line {idx+1}: Tag rusak. Pake teks asli")
                lines[idx] = f'{prefix}"{final_text}"{suffix}'
            except:
                error_log.append(f"Line {idx+1}: Error saat gabung")
        
        progress.progress((i + chunk_size) / len(batch))
        time.sleep(1.5)

    st.success(f"Selesai! {len(batch)} baris diproses")
    
    if error_log:
        with st.expander("Lihat Log Error"):
            st.code("\n".join(error_log))

    st.download_button(
        "DOWNLOAD FILE ID V7.5", 
        '\n'.join(lines), 
        "ID_V75_" + file.name,
        use_container_width=True
    )

st.caption("Catatan: {sc=3} \\n... none TIDAK AKAN PERNAH BERUBAH")
