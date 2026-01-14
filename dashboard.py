import streamlit as st
from groq import Groq
import os
import time
import requests
import re
import base64
import json
import hmac
import cv2
import numpy as np
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. CORE ENGINES & COGNITIVE MEMORY ---
MEMORY_FILE = "neural_vault.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except: pass
    return {"director_name": "Director", "boot_logs": [], "intel_logs": []}

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_sector_intel():
    try:
        geo = requests.get("http://ip-api.com/json/", timeout=3).json()
        if geo.get('status') == 'success':
            city = geo.get('city', 'UNKNOWN').upper()
            region = geo.get('region', 'SEC').upper()
            return f"SECTOR: {city}, {region} | ATMO: SECURE"
    except: pass
    return "SECTOR: GLOBAL_WIDE | ENCRYPTION: ACTIVE"

def get_base64_bin(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h1 style='text-align: center; color: #00f2ff; margin-top: 15%; font-family: monospace;'>LENSCAST_OS</h1>", unsafe_allow_html=True)
        pwd = st.text_input("ENTER OVERRIDE", type="password", key="main_login")
        if pwd == "3431":
            st.session_state.password_correct = True
            mem = load_memory()
            mem["boot_logs"].insert(0, {"timestamp": datetime.now().strftime("%H:%M:%S"), "status": "AUTHORIZED"})
            save_memory(mem)
            st.rerun()
        return False
    return True

def lizzy_speak(text):
    clean_text = text.replace("'", "").replace('"', '')
    components.html(f"""
        <script>
        window.speechSynthesis.cancel(); 
        var msg = new SpeechSynthesisUtterance('{clean_text}'); 
        msg.rate = 1.0; msg.pitch = 0.8; 
        window.speechSynthesis.speak(msg);
        </script>
    """, height=0)

# --- 2. ASSETS & INIT ---
LOGO_PATH = "lenscast_logo.png"
APP_ICON = "app_icon.png"
STARTUP_SOUND = "startup.wav"

st.set_page_config(page_title="LENSCAST_OS", page_icon=APP_ICON, layout="wide")

if check_password():
    if 'booted' not in st.session_state:
        st.session_state.update({
            'booted': False, 
            'messages': [], 
            'memory': load_memory(), 
            'sector_intel': get_sector_intel()
        })

    # --- 4. CINEMATIC BOOT ---
    if not st.session_state.booted:
        logo_b64 = get_base64_bin(LOGO_PATH)
        boot_area = st.empty()
        with boot_area.container():
            st.markdown(f"""
                <style>
                @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
                .boot-wrapper {{
                    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                    display: flex; flex-direction: column; align-items: center; justify-content: center;
                    background-color: #050505; z-index: 9999;
                }}
                .id-box {{ border: 1px solid #00f2ff; padding: 25px; background: rgba(0, 242, 255, 0.05); animation: fadeIn 2s; }}
                </style>
                <div class='boot-wrapper'>
                    {'<img src="data:image/png;base64,' + logo_b64 + '" width="320">' if logo_b64 else ''}
                    <div class='id-box'><h3 style='color:#00f2ff; font-family: monospace;'>IDENTITY VERIFIED</h3></div>
                </div>
            """, unsafe_allow_html=True)
            if os.path.exists(STARTUP_SOUND):
                s_b64 = get_base64_bin(STARTUP_SOUND)
                st.markdown(f'<audio autoplay><source src="data:audio/wav;base64,{s_b64}"></audio>', unsafe_allow_html=True)
            time.sleep(2.5); lizzy_speak(f"Neural link established. Welcome back, {st.session_state.memory['director_name']}."); time.sleep(4.0)
            st.session_state.booted = True; st.rerun()

    # --- 5. DASHBOARD ---
    st.markdown(f"<div style='background:#0a0a0a; border-bottom:2px solid #00f2ff; padding:10px; color:#00f2ff; display:flex; justify-content:space-between; font-family:monospace;'><span>📡 LINK: SECURE</span><span>🛰️ {st.session_state.sector_intel}</span><span>👤 {st.session_state.memory['director_name'].upper()}</span></div>", unsafe_allow_html=True)
    
    tabs = st.tabs(["👁️ LENSCAST", "💾 VAULT", "📋 LOGS", "💬 COMM_LINK"])

    with tabs[0]: # OPTIC SURVEILLANCE (REFINED)
        st.markdown("### 👁️ OPTIC_SURVEILLANCE")
        cam_image = st.camera_input("SCANNER_ACTIVE")
        if cam_image:
            file_bytes = np.asarray(bytearray(cam_image.read()), dtype=np.uint8)
            opencv_image = cv2.imdecode(file_bytes, 1)
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            if len(faces) > 0:
                # Target Lock logic: Only process the first (most prominent) target
                x, y, w, h = faces[0] 
                dist = int(5000 / w) 
                st.success(f"🎯 TARGET LOCKED | RANGE: {dist} CM")
                
                if st.button("RUN BIOMETRIC RECOGNITION", key="biorecog"):
                    st.info("🔎 ANALYZING...")
                    time.sleep(1.0)
                    st.write(f"✅ CONFIRMED: {st.session_state.memory['director_name'].upper()}")
                    lizzy_speak(f"Identity confirmed. Target recognized as the Director at {dist} centimeters.")
            else:
                st.error("⚠️ NO SIGNATURES DETECTED")

    with tabs[2]: # LOGS (FIXED)
        st.markdown("### 📋 FACILITY_LOGS")
        for log in st.session_state.memory.get('boot_logs', []):
            st.markdown(f"<div style='border-left: 2px solid #00f2ff; padding-left: 10px; margin-bottom: 5px; color: #fff; font-family: monospace;'>[{log['timestamp']}] >> {log['status']}</div>", unsafe_allow_html=True)

    with tabs[3]: # COMM_LINK (PERSONABLE MEMORY)
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.write(msg['content'])
        u_in = st.chat_input("Direct Transmission...")
        if u_in:
            st.session_state.messages.append({"role": "user", "content": u_in})
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            # Persona and Memory Integration
            persona = f"""You are Lizzy, a tactical and slightly witty AI assistant for LENSCAST. 
            Director's Name: {st.session_state.memory['director_name']}. 
            Recent Events: {st.session_state.memory['boot_logs'][:3]}.
            Always be personable, concise, and refer to the Director by name when appropriate. 
            You remember past logs and previous chat history."""
            
            ans = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[{"role": "system", "content": persona}] + st.session_state.messages[-10:]
            ).choices[0].message.content
            
            st.session_state.messages.append({"role": "assistant", "content": ans})
            lizzy_speak(ans); time.sleep(0.5); st.rerun()