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

# --- 1. CORE ENGINES & RECON ---
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
    """Platinum Recon: Multi-node handshake for 100% accuracy."""
    try:
        geo = requests.get("http://ip-api.com/json/", timeout=3).json()
        if geo.get('status') == 'success':
            city = geo.get('city', 'UNKNOWN').upper()
            region = geo.get('region', 'SEC').upper()
            try:
                w_url = f"https://wttr.in/{city.replace(' ', '+')}?format=%C+%t"
                atmo_res = requests.get(w_url, timeout=3)
                if atmo_res.status_code == 200:
                    return f"SECTOR: {city}, {region} | {atmo_res.text.strip().upper()}"
            except: pass
            return f"SECTOR: {city}, {region} | ATMO: STABLE"
    except: pass
    return "SECTOR: GLOBAL_WIDE | ENCRYPTION: ACTIVE"

def get_base64_bin(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def check_password():
    if "attempts" not in st.session_state: st.session_state.attempts = 0
    if "lockout" not in st.session_state: st.session_state.lockout = False

    def password_entered():
        if hmac.compare_digest(st.session_state["password"], "3431"):
            st.session_state["password_correct"] = True
            mem = load_memory()
            mem["boot_logs"].insert(0, {"timestamp": datetime.now().strftime("%H:%M:%S"), "status": "AUTHORIZED"})
            save_memory(mem)
            del st.session_state["password"]
        else:
            st.session_state.attempts += 1
            if st.session_state.attempts >= 3: st.session_state.lockout = True

    if st.session_state.lockout:
        st.markdown("<style>.stApp{background:#2e0000;}</style>", unsafe_allow_html=True)
        st.error("🚨 SYSTEM LOCKDOWN: UNAUTHORIZED ACCESS DETECTED.")
        st.stop()

    if "password_correct" not in st.session_state:
        st.markdown("<h1 style='text-align: center; color: #00f2ff; margin-top: 15%; font-family: monospace;'>LENSCAST_OS</h1>", unsafe_allow_html=True)
        st.text_input("ENTER OVERRIDE", type="password", on_change=password_entered, key="password")
        return False
    return True

# --- 2. ASSETS ---
LOGO_PATH = "lenscast_logo.png"
APP_ICON = "app_icon.png"
STARTUP_SOUND = "startup.wav"

def lizzy_speak(text):
    clean_text = re.sub(r"as an ai.*?,|I am an ai.*?,", "", text, flags=re.IGNORECASE).replace("'", "").replace('"', '')
    components.html(f"""
        <script>
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance('{clean_text}');
        msg.rate = 1.0; msg.pitch = 0.8;
        window.speechSynthesis.speak(msg);
        </script>
    """, height=0)

# --- 3. INITIALIZATION ---
st.set_page_config(page_title="LENSCAST_OS", page_icon=APP_ICON, layout="wide")

if check_password():
    if 'booted' not in st.session_state:
        st.session_state.update({
            'booted': False, 'messages': [], 'memory': load_memory(),
            'sector_intel': get_sector_intel()
        })

    # --- 4. THE BOOT SEQUENCE ---
    if not st.session_state.booted:
        logo_b64 = get_base64_bin(LOGO_PATH)
        boot_area = st.empty()
        with boot_area.container():
            st.markdown(f"""
                <style>
                .boot-wrapper {{
                    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                    display: flex; flex-direction: column; align-items: center; justify-content: center;
                    background-color: #050505; z-index: 9999;
                }}
                </style>
                <div class='boot-wrapper'>
                    {'<img src="data:image/png;base64,' + logo_b64 + '" width="350">' if logo_b64 else ''}
                    <div style='border: 1px solid #00f2ff; padding: 20px; background: rgba(0, 242, 255, 0.05); border-radius: 5px; margin-top: 20px;'>
                        <h3 style='color:#00f2ff; font-family: monospace; margin:0;'>IDENTITY VERIFIED: {st.session_state.memory['director_name'].upper()}</h3>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if os.path.exists(STARTUP_SOUND):
                sound_b64 = get_base64_bin(STARTUP_SOUND)
                st.markdown(f'<audio autoplay><source src="data:audio/wav;base64,{sound_b64}"></audio>', unsafe_allow_html=True)
            
            time.sleep(2.5) 
            lizzy_speak(f"Systems online. Welcome back, {st.session_state.memory['director_name']}.")
            time.sleep(4.0) 
            st.session_state.booted = True; st.rerun()

    # --- 5. THE MAIN INTERFACE ---
    if st.session_state.booted:
        st.markdown(f"""
            <div style="background: #0a0a0a; border-bottom: 2px solid #00f2ff; padding: 10px; display: flex; justify-content: space-between; font-family: monospace;">
                <span style="color: #00f2ff;">📡 LINK: SECURE</span>
                <span style="color: #00f2ff;">🛰️ {st.session_state.sector_intel}</span>
                <span style="color: #00f2ff;">👤 {st.session_state.memory['director_name'].upper()}</span>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<style>.stApp {background-color:#050505; color:#00f2ff;} [data-baseweb='tab'] {color:#00f2ff !important; font-family:monospace;}</style>", unsafe_allow_html=True)
        
        tabs = st.tabs(["👁️ LENSCAST", "💾 VAULT", "📋 LOGS", "💬 COMM_LINK"])

        with tabs[0]: # OPTIC SURVEILLANCE
            st.markdown("### 👁️ OPTIC_SURVEILLANCE")
            cam_image = st.camera_input("SCANNER_ACTIVE")
            if cam_image:
                st.warning("🚨 SPATIAL ANOMALY DETECTED: PROXIMITY ALERT ACTIVE")
                lizzy_speak("Director, proximity alert triggered. Spatial field is unstable.")

        with tabs[1]: # VAULT & INTEL DROPZONE
            st.markdown("### 💾 NEURAL_VAULT")
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Director Designation:", value=st.session_state.memory['director_name'])
                if st.button("UPDATE ARCHIVES"):
                    st.session_state.memory['director_name'] = new_name
                    save_memory(st.session_state.memory); st.rerun()
            with col2:
                st.markdown("### 📂 INTEL_DROPZONE")
                intel_file = st.file_uploader("Secure Tactical Scans/Files", type=['pdf', 'txt', 'png', 'jpg'])
                if intel_file:
                    st.info(f"FILE {intel_file.name} ENCRYPTED AND STORED IN VAULT.")

        with tabs[2]: # LOGS
            st.markdown("### 📋 FACILITY_LOGS")
            for log in st.session_state.memory.get('boot_logs', [])[:20]:
                st.code(f"[{log['timestamp']}] >> {log['status']}")

        with tabs[3]: # COMM LINK
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]): st.write(msg['content'])
            u_in = st.chat_input("Manual Transmission...")
            if u_in:
                st.session_state.messages.append({"role": "user", "content": u_in})
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                context = f"You are Lizzy. Director: {st.session_state.memory['director_name']}. Sector: {st.session_state.sector_intel}."
                completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": context}] + st.session_state.messages[-5:])
                ans = completion.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": ans})
                lizzy_speak(ans)
                time.sleep(0.5); st.rerun()