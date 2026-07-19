import streamlit as st
from deep_translator import GoogleTranslator
import google.generativeai as genai
from openai import OpenAI
import re, time

st.set_page_config(page_title="RenPy Translator 3in1", layout="centered")
st.title("🌏 Translator .rpy Anti FC")
st.caption("Pilih AI sesuai kebutuhan. Hasil langsung download")

uploaded_file = st.file_uploader("1. Upload file.rpy kamu", type=["rpy"])

col1, col2, col3 = st.columns(3)
with col1:
    use_google = st.button("Google Translate\nGRATIS")
with col2:
    gemini_key = st.text_input("Gemini API Key", type="password")
    use_gemini = st.button("Gemini 1.5\nGRATIS")
with col3:
    openai_key = st.text_input("OpenAI API Key", type="password")
    use_gpt = st.button("ChatGPT\nBAYAR")

def protect_and_clean(text):
    tags = re.findall(r'\{.*?\}', text)
    for i, tag in enumerate(tags): text = text.replace(tag, f'@@TAG{i}@@')
    text = text.replace('"', "'").replace('%', ' persen').replace('\\', '/')
    for i, tag in enumerate(tags): text = text.replace(f'@@TAG{i}@@', tag)
    return text

def make_it_casual(text):
    kamus =
