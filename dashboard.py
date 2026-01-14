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

# --- 1. ENHANCED SECTOR RECON (100% RELIABILITY) ---
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
    """Platinum Recon: Multi-node handshake with data cleaning."""
    try:
        # Step 1: High-speed IP handshake
        geo = requests.get("http://ip-api.com/json/", timeout=3).json()
        if geo.get('status') == 'success':
            city = geo.get('city', 'UNKNOWN').upper()
            region = geo.get('region', 'SEC').upper()
            
            # Step 2: Multi-attempt Weather probe
            # Attempting weather for the specific city coordinates
            try:
                w_url = f"https://wttr.in/{city.replace(' ', '+')}?format=%C+%t"
                atmo_res = requests.get(w_url, timeout=3)
                if atmo_res.status_code == 200 and "Unknown" not in atmo_res.text:
                    atmo = atmo_res.text.strip().upper()
                    return f"SECTOR: {city}, {region} | {atmo}"
            except: pass
            
            return f"SECTOR: {city}, {region} | ATMO: ONLINE"
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

# --- 2. ASSET CONSTANTS ---
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

    # --- 4. THE BOOT SEQUENCE (POLISHED) ---
    if not st.session_state.booted:
        logo_b64 = get_base64_bin(LOGO_PATH)
        boot_area = st.empty()
        with boot_area.container():
            st.markdown(f"""
                <style>
                @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
                .boot-wrapper {{
                    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                    display: flex; flex-direction: column; align-items: center; justify-content: center;
                    background-color: #050505; z-index: 9999;
                }}
                .id-box {{
                    border: 1px solid #00f2ff; padding: 25px; background: rgba(0, 242, 255, 0.05); 
                    border-radius: 8px; margin-top: 30px; animation: fadeIn 1.5s ease-out;
                    box-shadow: 0 0 15px rgba(0, 242, 255, 0.1);
                }}
                </style>
                <div class='boot-wrapper'>
                    {'<img src="data:image/png;base64,' + logo_b64 + '" width="320">' if logo_b64 else ''}
                    <div class='id-box'>
                        <h3 style='color:#00f2ff; font-family: monospace; margin:0; letter-spacing: 2px;'>IDENTITY VERIFIED</h3>
                        <p style='color:#fff; font-family: monospace; margin-top:10px; opacity:0.8;'>ACCESS GRANTED: {st.session_state.memory['director_name'].upper()}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if os.path.exists(STARTUP_SOUND):
                sound_b64 = get_base64_bin(STARTUP_SOUND)
                st.markdown(f'<audio autoplay><source src="data:audio/wav;base64,{sound_b64}"></audio>', unsafe_allow_html=True)
            
            time.sleep(2.5) 
            lizzy_speak(f"Systems synchronized. Welcome back, {st.session_state.memory['director_name']}.")
            time.sleep(4.0) 
            st.session_state.booted = True; st.rerun()

    # --- 5. MAIN INTERFACE ---
    if st.session_state.booted:
        st.markdown(f"""
            <div style="background: #0a0a0a; border-bottom: 2px solid #00f2ff; padding: 12px; display: flex; justify-content: space-between; font-family: monospace; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">
                <span style="color: #00f2ff; font-weight: bold;">📡 LINK: SECURE</span>
                <span style="color: #00f2ff;">🛰️ {st.session_state.sector_intel}</span>
                <span style="color: #00f2ff; opacity: 0.8;">👤 {st.session_state.memory['director_name'].upper()}</span>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<style>.stApp {background-color:#050505; color:#00f2ff;} [data-baseweb='tab'] {color:#00f2ff !important; font-family:monospace; font-size: 14px;}</style>", unsafe_allow_html=True)
        tabs = st.tabs(["👁️ LENSCAST", "💾 VAULT", "📋 LOGS", "💬 COMM_LINK"])

        with tabs[2]: # LOGS
            st.markdown("### 📋 FACILITY_LOGS")
            for log in st.session_state.memory.get('boot_logs', [])[:20]:
                st.markdown(f"<div style='border-left: 2px solid #00f2ff; padding-left: 10px; margin-bottom: 5px; font-family: monospace; font-size: 13px; color: #aaa;'>[{log['timestamp']}] >> {log['status']}</div>", unsafe_allow_html=True)

        with tabs[3]: # COMM_LINK
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]): st.write(msg['content'])
            u_in = st.chat_input("Manual Transmission...")
            if u_in:
                st.session_state.messages.append({"role": "user", "content": u_in})
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                context = f"You are Lizzy, the Tactical AI. Director: {st.session_state.memory['director_name']}. Sector: {st.session_state.sector_intel}."
                completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": context}] + st.session_state.messages[-5:])
                ans = completion.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": ans})
                lizzy_speak(ans); time.sleep(0.5); st.rerun()