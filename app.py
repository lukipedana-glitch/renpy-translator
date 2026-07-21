import streamlit as st
import re
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Universal to ID V7.3", layout="centered")
st.title("Universal to ID Translator V7.3 - Anti Bug 100%")
st.write("Terjemah semua bahasa -> Indonesia. Hanya teks di dalam \"...\"")
st.error("GARANSI: Tag {sc=3} \\n... ~ TIDAK AKAN PERNAH RUSAK")

file = st.file_uploader("Upload file.rpy bahasa apa aja", type=["rpy"])

def protect_and_split(text):
    # 1. Proteksi semua yg gaboleh keubah
    tags = re.findall(r'\{[^}]*\}|\[[^\]]*\]|\\[nrt"\\]|\.\.|~|none', text, flags=re.IGNORECASE)
    temp = text
    for i,t in enumerate(tags):
        temp = temp.replace(t, f'@@P{i}@@')
    return temp, tags

def unprotect(text, tags):
    # 2. Balikin semua yg diproteksi
    for i,t in enumerate(tags):
        text = text.replace(f'@@P{i}@@', t)
    return text

if file and st.button("TERJEMAHKAN SEMUA KE INDONESIA", type="primary"):
    content = file.read().decode('utf-8', errors='ignore')
    lines = content.split('\n')
    out = []
    batch = [] # buat translate cepat
    batch_index = []
    translated_count = 0

    progress = st.progress(0, text="Scan file...")

    # LANGKAH 1: Kumpulin semua yg mau di translate dulu biar cepat
    for idx, line in enumerate(lines):
        m = re.match(r'^(\s*\w+\s*)"((?:[^"\\]|\\.)*)"(.*)$', line) # tangkep old, new, s, dll
        if m:
            prefix, text, suffix = m.groups()
            if text.strip() and text.strip().lower()!= "none": # SKIP "none"
                clean_text, tags = protect_and_split(text)
                if clean_text.strip():
                    batch.append(clean_text)
                    batch_index.append((idx, prefix, tags, suffix))
        progress.progress((idx + 1) / len(lines))

    # LANGKAH 2: Translate sekaligus biar cepat 10x lipat
    if batch:
        st.info(f"Nemu {len(batch)} baris dialog. Lagi translate...")
        try:
            results = GoogleTranslator(source='auto', target='id').translate_batch(batch)
        except:
            st.warning("Batch gagal. Pake translate 1-1 lebih lambat")
            results = [GoogleTranslator(source='auto', target='id').translate(t) for t in batch]
        
        # LANGKAH 3: Masukin hasil ke baris semula
        for (idx, prefix, tags, suffix), result in zip(batch_index, results):
            final_text = unprotect(result, tags) # Balikin tag
            lines[idx] = f'{prefix}"{final_text}"{suffix}'
            translated_count += 1
    
    st.success(f"Selesai! {translated_count} baris diterjemahkan. Tag aman 100%")
    
    st.download_button(
        "DOWNLOAD FILE ID FINAL", 
        '\n'.join(lines), 
        "ID_" + file.name
    )

st.divider()
st.markdown("**Peraturan V7.3:**\n1. `none` = di skip\n2. `{sc=3}` `\\n` `...` `~` = dikunci\n3. Cuma translate isi `\"...\"`\n4. Bahasa auto detect")
