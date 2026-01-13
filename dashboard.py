import streamlit as st
from groq import Groq
import os
import time
import subprocess
import cv2
import numpy as np
import re
import speech_recognition as sr
import base64
import json
import hmac
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. SECURITY & MEMORY ENGINES ---
MEMORY_FILE = "neural_vault.json"

def load_memory():
    """Load persistent facility data."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except: pass
    return {"director_name": "Director", "boot_logs": []}

def save_memory(data):
    """Save persistent facility data."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def check_password():
    """Director Override Gate using Code 3431."""
    def password_entered():
        # Hardcoded Secure comparison
        if hmac.compare_digest(st.session_state["password"], "3431"):
            st.session_state["password_correct"] = True
            mem = load_memory()
            log = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "status": "AUTHORIZED_ACCESS"}
            if "boot_logs" not in mem: mem["boot_logs"] = []
            mem["boot_logs"].insert(0, log)
            save_memory(mem)
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<style>.stApp{background:#050505;}</style>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #00f2ff; margin-top: 15%; font-family: monospace;'>LENSCAST_OS</h1>", unsafe_allow_html=True)
        st.text_input("ENTER DIRECTOR OVERRIDE CODE", type="password", on_change=password_entered, key="password")
        if "password_correct" in st.session_state:
            st.error("🚨 ACCESS DENIED: INVALID CREDENTIALS")
        return False
    return True

# --- 2. ASSET PATHS & ENGINES ---
LOGO_PATH = "lenscast_logo.png"
LIZZY_FACE = "lizzy_face.png"
STARTUP_SOUND = "startup.wav"

def trigger_haptic():
    components.html("<script>window.navigator.vibrate([100, 30, 100]);</script>", height=0)

ddef lizzy_speak(text):
    """Universal Voice: Commands the browser (Phone or PC) to speak."""
    # Simplified fix for the Regex error:
    # We remove the (?i) from the string and use flags=re.IGNORECASE instead
    pattern = r"as an ai.*?,|I am an ai.*?,|legal guidelines"
    clean_text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    
    # Clean up quotes and newlines for JavaScript
    clean_text = clean_text.replace("'", "").replace('"', '').replace("\n", " ")
    
    components.html(f"""
        <script>
        var msg = new SpeechSynthesisUtterance('{clean_text}');
        msg.rate = 1.1;
        msg.pitch = 0.9;
        window.speechSynthesis.speak(msg);
        </script>
    """, height=0)

# --- 3. SESSION INITIALIZATION ---
st.set_page_config(page_title="LENSCAST_OS", layout="wide")

if check_password(): # SECURITY GATE ACTIVE
    if 'booted' not in st.session_state:
        st.session_state.update({
            'booted': False, 'sensors_active': False, 'flashlight': False,
            'messages': [], 'proximity_alert': "CLEAR", 'temperament': "STABLE",
            'memory': load_memory()
        })

    # --- 4. CENTERED BOOT ---
    if not st.session_state.booted:
        boot_area = st.empty()
        with boot_area.container():
            st.markdown("<style>.boot-container {display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh; text-align: center;}</style><div class='boot-container'>", unsafe_allow_html=True)
            if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=350)
            
            # --- UNIVERSAL SOUND FIX ---
            if os.path.exists(STARTUP_SOUND):
                with open(STARTUP_SOUND, "rb") as f:
                    data = f.read()
                    b64 = base64.b64encode(data).decode()
                    md = f"""
                        <audio autoplay>
                        <source src="data:audio/wav;base64,{b64}" type="audio/wav">
                        </audio>
                        """
                    st.markdown(md, unsafe_allow_html=True)
            
            st.markdown("<h2 style='color:#00f2ff; font-family: monospace;'>INITIALIZING LENSCAST_PROTOCOL...</h2>", unsafe_allow_html=True)
            bar = st.progress(0)
            for i in range(101):
                time.sleep(0.01); bar.progress(i)
            
            lizzy_speak(f"Welcome back, {st.session_state.memory['director_name']}. Systems secured.")
            st.session_state.booted = True; st.rerun()

    # --- 5. MAIN INTERFACE ---
    st.markdown("<style>.stApp{background-color:#050505; color:#00f2ff;} [data-baseweb='tab']{color:#00f2ff !important; font-family:monospace;}</style>", unsafe_allow_html=True)
    
    tabs = st.tabs(["👁️ LENSCAST", "💾 VAULT", "📋 LOGS", "🎭 TONE", "💬 COMM_LINK"])

    with tabs[0]: # LENSCAST
        st.markdown("### 👁️ OPTIC_SURVEILLANCE")
        cam_in = st.camera_input("SENSORS_ACTIVE")
        if cam_in:
            st.session_state.proximity_alert = "NEAR"
            st.warning("⚠️ PROXIMITY_ALERT_DETECTED")

    with tabs[1]: # VAULT
        st.markdown("### 💾 NEURAL_VAULT")
        new_name = st.text_input("Director Designation:", value=st.session_state.memory['director_name'])
        if st.button("UPDATE ARCHIVES"):
            st.session_state.memory['director_name'] = new_name
            save_memory(st.session_state.memory)
            st.success("VAULT UPDATED")

    with tabs[2]: # AUDIT LOGS
        st.markdown("### 📋 BOOT_HISTORY")
        for log in st.session_state.memory.get('boot_logs', [])[:10]:
            st.code(f"[{log['timestamp']}] >> {log['status']}")

    with tabs[4]: # COMM_LINK
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.write(msg['content'])
        
        u_in = st.chat_input("Manual Transmission...")
        if u_in:
            st.session_state.messages.append({"role": "user", "content": u_in})
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            context = f"You are Lizzy. Director: {st.session_state.memory['director_name']}. Be sentient and loyal."
            completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": context}] + st.session_state.messages[-5:])
            ans = completion.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ans})
            lizzy_speak(ans)
            st.rerun()