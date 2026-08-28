import streamlit as st
import requests
from concurrent.futures import ThreadPoolExecutor

# Page Config
st.set_page_config(page_title="Al Kafi Arabic Dictionary", page_icon="", layout="centered")

# Custom CSS for Arabic & Bangla Fonts + Minimal Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Hind+Siliguri:wght@400;600;700&display=swap');
    
    html, body, [class*="css"], .stMarkdown, p, div, span, input {
        font-family: 'Hind Siliguri', sans-serif !important;
    }
    
    .arabic-title {
        font-family: 'Amiri', serif !important;
        font-size: 2.8rem;
        font-weight: 700;
        direction: rtl;
        text-align: right;
        margin-top: 10px;
        margin-bottom: 5px;
        color: #0d6efd;
    }

    .arabic-text {
        font-family: 'Amiri', serif !important;
        font-size: 1.4rem;
        direction: rtl;
    }

    .main-title {
        text-align: center;
        font-weight: 700;
        color: #007bff;
        margin-bottom: 10px;
    }

    .pos-text {
        font-style: italic;
        color: #aaaaaa;
        font-size: 1.05rem;
        margin-bottom: 15px;
    }
    
    .meaning-box {
        background-color: rgba(13, 110, 253, 0.08);
        border-left: 4px solid #0d6efd;
        padding: 12px 16px;
        border-radius: 6px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    
    .footer {
        text-align: center;
        margin-top: 50px;
        padding-top: 15px;
        border-top: 1px solid rgba(128, 128, 128, 0.2);
        font-size: 0.85em;
        opacity: 0.85;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>Al Kafi Arabic Dictionary</h1>", unsafe_allow_html=True)

# Reliable Multi-API Translation Fetcher
def fetch_translation(word, target_lang='bn'):
    # Primary API: MyMemory Translation API
    try:
        url = f"https://api.mymemory.translated.net/get?q={word}&langpair=ar|{target_lang}"
        r = requests.get(url, timeout=3.0)
        if r.status_code == 200:
            data = r.json()
            translated_text = data.get('responseData', {}).get('translatedText', '')
            if translated_text and not translated_text.startswith("QUERY LENGTH"):
                return translated_text
    except:
        pass

    # Fallback API: Google GTX Endpoint
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=ar&tl={target_lang}&dt=t&q={word}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=3.0)
        if r.status_code == 200:
            res = r.json()
            return res[0][0][0]
    except:
        pass

    return ""

@st.cache_data(ttl=86400, show_spinner=False)
def get_arabic_details(word):
    with ThreadPoolExecutor() as executor:
        f_bn = executor.submit(fetch_translation, word, 'bn')
        f_en = executor.submit(fetch_translation, word, 'en')
        return f_bn.result(), f_en.result()

# Search Bar Input
user_input = st.text_input("Search Arabic Word", placeholder="Type or paste Arabic word (e.g., الحمد, سلام, كتاب)...")

if user_input:
    word = user_input.strip()
    bangla_meaning, english_trans = get_arabic_details(word)

    if bangla_meaning:
        # Header Display
        st.markdown(f"<div class='arabic-title'>{word}</div>", unsafe_allow_html=True)
        st.markdown("<div class='pos-text'>اسم / فعل</div>", unsafe_allow_html=True)

        # Bangla Meaning Display
        st.markdown(f"<div class='meaning-box'><b>বাংলা অর্থ:</b> {bangla_meaning}</div>", unsafe_allow_html=True)

        # English Meaning Reference
        if english_trans:
            st.markdown(f"**English Meaning:** *\"{english_trans.capitalize()}\"*")

        st.markdown("---")
        st.markdown(f"**Example Sentence (مثال):** <span class='arabic-text'>هذا مثال لاستخدام كلمة ({word})</span>", unsafe_allow_html=True)
    else:
        st.error("শব্দটি অনলাইন অভিধানে পাওয়া যায়নি। দয়া করে ইন্টারনেট সংযোগ অথবা সঠিক আরবি শব্দ চেক করুন।")

# Footer Section
st.markdown("""
    <div class="footer">
        <p>Copyright by <b>Al Kafi Dictionary</b></p>
        <p>Designed & deployed by <b>Al Kafi</b></p>
        <p><a href="https://facebook.com/alkafiofficial" target="_blank">Connect on Facebook: Al Kafi</a></p>
    </div>
""", unsafe_allow_html=True)