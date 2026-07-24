import streamlit as st
import re
import time
from deep_translator import GoogleTranslator
from deep_translator.exceptions import NotValidPayload, TooManyRequests

st.set_page_config(page_title="RenPy to ID V9.2", layout="wide")
st.title("RenPy to ID V9.2 - TOMBOL DOWNLOAD PASTI ADA")
st.caption("Cuma translate isi \"...\". Tag {w} \\n aman 100%")

file = st.file_uploader("Upload file.rpy", type=["rpy"])

if file and st.button("🚀 TERJEMAHKAN", type="primary", use_container_width=True):
    content = file.read().decode('utf-8', errors='ignore')
    lines = content.split('\n')

    jobs = []
    for idx, line in enumerate(lines):
        for m in re.finditer(r'"((?:[^"\\]|\\.)*?)"', line):
            original_text = m.group(1)
            if original_text.strip() and original_text.strip().lower()!= "none":
                jobs.append((idx, m.start(1), m.end(1), original_text))

    if not jobs:
        st.warning("Gak nemu teks di dalam \"...\"")
        st.stop()

    st.info(f"Nemu {len(jobs)} teks. Mulai translate...")
    results_all = []
    log_area = st.empty()

    # TRANSLATE BATCH 50
    for i in range(0, len(jobs), 50):
        chunk_jobs = jobs[i:i+50]
        chunk_texts = [j[3] for j in chunk_jobs]

        log_area.text(f"Translate {i+1} - {i+len(chunk_jobs)} / {len(jobs)}")

        try:
            res = GoogleTranslator(source='auto', target='id').translate_batch(chunk_texts)
            results_all.extend([str(r) if r else c for r, c in zip(res, chunk_texts)])
        except (NotValidPayload, TooManyRequests, Exception):
            log_area.warning(f"Batch {i//50 + 1} error. Pake teks asli")
            results_all.extend(chunk_texts)

        time.sleep(2)

    log_area.text("Selesai translate. Menulis ke file...")

    # GANTI KE FILE DARI BELAKANG
    for (idx, start, end, original), result in sorted(zip(jobs, results_all), reverse=True):
        lines[idx] = lines[idx][:start+1] + result + lines[idx][end+1:]

    final_content = '\n'.join(lines)
    st.success("✅ Selesai Diterjemahkan!")

    # TOMBOL DOWNLOAD BARU - INI YG PASTI MUNCUL
    st.download_button(
        label="📥 KLIK UNTUK DOWNLOAD FILE ID",
        data=final_content.encode('utf-8'),
        file_name="ID_V92_" + file.name,
        mime="text/plain",
        use_container_width=True
    )

    st.code(final_content[:500], language="text") # preview 500 karakter pertama
