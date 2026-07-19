import streamlit as st
import re
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Anti FC V4")
st.title("🌏 Translator.rpy Anti FC V4 - Skip Error")

uploaded_file = st.file_uploader("Upload file.rpy", type=["rpy"])
tombol = st.button("TRANSLATE")

if tombol:
    if not uploaded_file:
        st.error("Upload file dulu bang")
    else:
        with st.spinner("Lagi nerjemahin..."):
            content = uploaded_file.read().decode('utf-8', errors='ignore')
            lines = content.split('\n')
            out = []
            error_count = 0
            
            for line in lines:
                m = re.match(r'^(\s*\w*\s*)"((?:[^"\\]|\\.)*)"(.*)$', line)
                if m:
                    dialog = m.group(2)
                    if '"' in dialog and '\\"' not in dialog:
                        out.append(f'{m.group(1)}"[SKIP: Kutip error]"{m.group(3)}')
                        error_count += 1
                    else:
                        try:
                            hasil = GoogleTranslator(source='auto', target='id').translate(dialog)
                            out.append(f'{m.group(1)}"{hasil}"{m.group(3)}')
                        except:
                            out.append(line)
                else:
                    out.append(line)
            
            st.success(f"SELESAI. {error_count} line di-skip")
            st.download_button("Download Hasil", '\n'.join(out), "ID_"+uploaded_file.name)
