import streamlit as st, re
from deep_translator import GoogleTranslator

st.set_page_config(page_title="RenPy Translator V6", layout="wide")
st.title("🌏 RenPy Translator V6 - Anti FC Pro")
st.caption("Translate.rpy aman. Tag {sc=3} {i} {color} gak bakal rusak lagi")

col1, col2 = st.columns([2,1])

with col1:
    file = st.file_uploader("📂 Upload file.rpy kamu", type=["rpy"])
with col2:
    lang_map = {"id": "Bahasa Indonesia", "es": "Español", "en": "English", "jp": "日本語"}
    lang = st.selectbox("🌐 Translate ke
