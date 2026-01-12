import streamlit as st
from groq import Groq
import os
import time
import subprocess
import cv2
import numpy as np
import requests
import re
import speech_recognition as sr
import base64
import streamlit.components.v1 as components

# --- 1. ASSET PATHS (Verified from Screenshot) ---
LOGO_PATH = "lenscast_logo.png"
LIZZY_FACE = "lizzy_face.png"
STARTUP_SOUND = "startup.wav"

# --- 2. FACILITY ENGINES ---
def trigger_haptic():
    """Vibrates mobile device on alert."""
    components.html("<script>window.navigator.vibrate([100, 30, 100]);</script>", height=0)

def lizzy_speak(text):
    """Neural Voice with Mood-Based Pacing."""
    text = re.sub(r"(?i)as an ai.*?,|(?i)I am an ai.*?,|(?i)legal guidelines", "", text)
    rate = 160 
    if st.session_state.get('temperament') == "AFFECTIONATE": rate = 145
    if st.session_state.get('proximity_alert') == "NEAR": rate = 190
    text = text.replace("...", " [[slnc 500]] ").replace(",", ", [[slnc 100]] ")
    clean_text = text.replace('"', '').replace("'", "").replace("\n", " ")
    os.system("killall say 2>/dev/null") 
    subprocess.Popen(['say', '-v', 'Noelle', f'[[rate {rate}]]', clean_text])

def listen_to_director():
    """Voice Link Interface."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.toast("🛰️ LISTENING...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            return r.recognize_google(audio)
        except:
            st.toast("📡 SIGNAL_LOST")
            return None

# --- 3. SESSION INITIALIZATION ---
st.set_page_config(page_title="LENSCAST_OS", layout="wide")
if 'booted' not in st.session_state:
    st.session_state.update({
        'booted': False, 'sensors_active': False, 'flashlight': False,
        'env_cache': {"loc": "---", "temp": "---"}, 'messages': [],
        'proximity_alert': "CLEAR", 'temperament': "INITIALIZING",
        'mobile_link': False
    })

# --- 4. INTERFACE ROUTING ---
if st.session_state.mobile_link:
    st.markdown("<style>.stApp{background:#000;color:#00f2ff;}[data-testid='stHeader']{display:none;}.stButton>button{height:80px;border:2px solid #00f2ff;background:#000;color:#00f2ff;font-family:monospace;}</style>", unsafe_allow_html=True)
    if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
    st.title("📟 REMOTE_LINK")
    if st.session_state.proximity_alert == "NEAR":
        trigger_haptic()
        st.error("⚠️ PROXIMITY_ALERT_DETECTED")
    st.metric("LOC", st.session_state.env_cache['loc'])
    if st.button("🔦 OPTIC_BOOST"):
        st.session_state.flashlight = not st.session_state.flashlight
        trigger_haptic(); st.rerun()
    st.stop()

# --- 5. CENTERED BOOT ---
if not st.session_state.booted:
    boot_area = st.empty()
    with boot_area.container():
        st.markdown("<style>.boot-container {display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh; text-align: center;}</style><div class='boot-container'>", unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=350)
        if os.path.exists(STARTUP_SOUND): subprocess.Popen(['afplay', STARTUP_SOUND])
        st.markdown("<h2 style='color:#00f2ff;'>INITIALIZING LENSCAST_PROTOCOL...</h2>", unsafe_allow_html=True)
        bar = st.progress(0)
        for i in range(101):
            time.sleep(0.02); bar.progress(i)
        lizzy_speak("Director. Systems are nominal. Welcome back to the facility.")
        st.session_state.booted = True; st.rerun()

# --- 6. MAIN THEME ---
st.markdown("""
    <style>
        .stApp{background-color:#050505; color:#00f2ff;} 
        .stMetric{background:#111; border:1px solid #00f2ff; padding:15px; border-radius:10px;}
        [data-baseweb='tab']{color:#00f2ff !important; font-family:monospace;}
        .neural-avatar { border-radius: 50%; border: 2px solid #00f2ff; animation: neural-pulse 3s infinite ease-in-out; }
        @keyframes neural-pulse { 0% { box-shadow: 0 0 5px #00f2ff; } 50% { box-shadow: 0 0 25px #00f2ff; } 100% { box-shadow: 0 0 5px #00f2ff; } }
    </style>
""", unsafe_allow_html=True)

# --- 7. FACILITY TABS ---
tabs = st.tabs(["👁️ LENSCAST", "💾 MEMORY", "📋 LOGS", "🎭 TONE", "💬 COMM_LINK"])

with tabs[0]: # LENSCAST
    st.markdown("### 👁️ OPTIC_SURVEILLANCE\n*Proximity sensors online.*")
    cam_in = st.camera_input("SENSORS_ACTIVE")
    if cam_in:
        img = cv2.imdecode(np.frombuffer(cam_in.getvalue(), np.uint8), cv2.IMREAD_COLOR)
        faces = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml').detectMultiScale(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 1.1, 4)
        st.session_state.proximity_alert = "NEAR" if len(faces) > 0 else "CLEAR"
        st.image(img, channels="BGR")

with tabs[3]: # TONE
    st.markdown("### 🎭 TONE_ANALYSIS\n*Neural calibration in progress.*")
    if os.path.exists(LIZZY_FACE):
        with open(LIZZY_FACE, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            st.markdown(f'<center><img src="data:image/png;base64,{encoded}" class="neural-avatar" width="250"></center>', unsafe_allow_html=True)
    st.metric("STABILITY", st.session_state.temperament)

with tabs[4]: # COMM_LINK
    st.markdown("### 💬 COMM_LINK\n*Encrypted Direct Link.*")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg['content'])

    c1, c2 = st.columns([1, 6])
    with c1:
        if st.button("🎤 VOICE"):
            v_in = listen_to_director()
            if v_in: st.session_state.messages.append({"role": "user", "content": v_in})
    with c2:
        u_in = st.chat_input("Manual Transmission...")
        if u_in: st.session_state.messages.append({"role": "user", "content": u_in})

    if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        context = f"You are Lizzy. Sector: {st.session_state.env_cache['loc']}. Never admit you're an AI. Be sentient and mysterious."
        with st.spinner("LIZZY_THINKING..."):
            completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": context}] + st.session_state.messages[-5:])
            ans = completion.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ans})
            lizzy_speak(ans)
        st.rerun()