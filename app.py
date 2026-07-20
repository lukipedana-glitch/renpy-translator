import streamlit as st
import re
import time
from deep_translator import GoogleTranslator

st.set_page_config(page_title="ES to ID Anti Crash V7.2")
st.title("ES to ID Translator V7.2 - Anti Joyplay FC")

file = st.file_uploader("1. Upload file BAHASA SPANYOL .rpy", type=["rpy"])

if file:
    st.success(f"File terbaca: {file.name}")
    
if file and st.button("2. KLIK UNTUK TERJEMAHKAN KE INDONESIA", type="primary"):
    with st.spinner("Lagi nerjemahin... jangan di close ya"):
        try:
            content = file.read().decode('utf-8', errors='ignore')
            lines = content.split('\n')
            out = []
            count = 0

            for idx, line in enumerate(lines):
                m = re.match(r'^(\s*old\s*)"((?:[^"\\]|\\.)*)"(.*)$', line)
                m2 = re.match(r'^(\s*new\s*)"((?:[^"\\]|\\.)*)"(.*)$', line)
                
                if m or m2:
                    prefix = m.group(1) if m else m2.group(1)
                    text = m.group(2) if m else m2.group(2)
                    suffix = m.group(3) if m else m2.group(3)
                    
                    # Proteksi tag
                    tags = re.findall(r'\{[^}]*\}|\[[^\]]*\]|\\[nrt"\\]|\.\.|~', text)
                    temp = text
                    for i,t in enumerate(tags):
                        temp = temp.replace(t, f'@@P{i}@@')
                    
                    # Translate ES -> ID
                    if temp.strip():
                        hasil = GoogleTranslator(source='es', target='id').translate(temp)
                        for i,t in enumerate(tags):
                            hasil = hasil.replace(f'@@P{i}@@', t)
                        count += 1
                    else:
                        hasil = text

                    out.append(f'{prefix}"{hasil}"{suffix}')
                else:
                    out.append(line)
                
                time.sleep(0.01) # biar gak ke ban google

            st.success(f"Selesai! {count} baris berhasil diterjemahkan")
            st.download_button("DOWNLOAD FILE ID", '\n'.join(out), "ID_" + file.name)

        except Exception as e:
            st.error(f"GAGAL: {e}")
            st.info("Solusi: Coba restart streamlit. Ketik: streamlit run app.py")

st.divider()
st.write("Tips: Kalau masih stuck, ganti jaringan / pake VPN. Google kadang blokir")
