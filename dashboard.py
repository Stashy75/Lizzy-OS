import streamlit as st
from groq import Groq
import os
import time
import requests
import re
import base64
import json
import hmac
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. SECURITY, LOCKDOWN & MEMORY ---
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

def get_sector_weather():
    """Live recon of local atmospheric conditions."""
    try:
        res = requests.get("https://wttr.in/?format=%C+%t", timeout=5)
        if res.status_code == 200:
            return f"SECTOR ATMO: {res.text.strip()}"
    except:
        pass
    return "SECTOR ATMO: SENSORS OFFLINE"

def check_password():
    if "attempts" not in st.session_state: st.session_state.attempts = 0
    if "lockout" not in st.session_state: st.session_state.lockout = False

    def password_entered():
        if hmac.compare_digest(st.session_state["password"], "3431"):
            st.session_state["password_correct"] = True
            st.session_state.attempts = 0
            mem = load_memory()
            log = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "status": "AUTHORIZED_ACCESS"}
            mem["boot_logs"].insert(0, log)
            save_memory(mem)
            del st.session_state["password"]
        else:
            st.session_state.attempts += 1
            if st.session_state.attempts >= 3:
                st.session_state.lockout = True
            st.session_state["password_correct"] = False

    if st.session_state.lockout:
        st.markdown("<style>.stApp {background:#2e0000;}</style>", unsafe_allow_html=True)
        st.error("🚨 SYSTEM LOCKDOWN: UNAUTHORIZED ACCESS DETECTED. FACILITY SEALED.")
        st.stop()

    if "password_correct" not in st.session_state:
        st.markdown("<style>.stApp {background:#050505;}</style>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #00f2ff; margin-top: 15%; font-family: monospace;'>LENSCAST_OS</h1>", unsafe_allow_html=True)
        st.text_input(f"ENTER OVERRIDE CODE (ATTEMPT {st.session_state.attempts + 1}/3)", type="password", on_change=password_entered, key="password")
        if st.session_state.attempts > 0:
            st.warning(f"⚠️ {3 - st.session_state.attempts} ATTEMPTS REMAINING")
        return False
    return True

# --- 2. ASSETS & ENGINES ---
LOGO_PATH = "lenscast_logo.png"
APP_ICON = "app_icon.png"
STARTUP_SOUND = "startup.wav"

def lizzy_speak(text):
    pattern = r"as an ai.*?,|I am an ai.*?,|legal guidelines"
    clean_text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    clean_text = clean_text.replace("'", "").replace('"', '').replace("\n", " ")
    components.html(f"<script>var msg = new SpeechSynthesisUtterance('{clean_text}'); msg.rate = 1.1; msg.pitch = 0.9; window.speechSynthesis.speak(msg);</script>", height=0)

# --- 3. INITIALIZATION ---
st.set_page_config(page_title="LENSCAST_OS", page_icon=APP_ICON, layout="wide")

if check_password(): 
    if 'booted' not in st.session_state:
        st.session_state.update({
            'booted': False, 'messages': [], 'memory': load_memory(),
            'sector_intel': get_sector_weather()
        })

    # --- 4. TACTICAL STATUS HEADER ---
    st.markdown(f"""
        <div style="background: #0a0a0a; border-bottom: 2px solid #00f2ff; padding: 10px; display: flex; justify-content: space-between; font-family: monospace;">
            <span style="color: #00f2ff;">📡 LINK: ENCRYPTED</span>
            <span style="color: #00f2ff;">🛰️ {st.session_state.sector_intel}</span>
            <span style="color: #00f2ff;">👤 DIR: {st.session_state.memory['director_name'].upper()}</span>
        </div>
    """, unsafe_allow_html=True)

    # --- 5. CENTERED BOOT SEQUENCE ---
    if not st.session_state.booted:
        boot_area = st.empty()
        with boot_area.container():
            st.markdown("""
                <style>
                .boot-wrapper {
                    display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh; text-align: center;
                }
                .stProgress > div > div > div > div { background-color: #00f2ff; }
                </style>
                <div class="boot-wrapper">
            """, unsafe_allow_html=True)
            
            if os.path.exists(LOGO_PATH): 
                st.image(LOGO_PATH, width=350)
            
            if os.path.exists(STARTUP_SOUND):
                with open(STARTUP_SOUND, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                    st.markdown(f'<audio autoplay><source src="data:audio/wav;base64,{b64}"></audio>', unsafe_allow_html=True)
            
            st.markdown("<h4 style='color:#00f2ff; font-family: monospace; letter-spacing: 2px;'>ESTABLISHING NEURAL LINK...</h4>", unsafe_allow_html=True)
            
            # Slowing down the progress bar slightly for visual impact
            bar = st.progress(0)
            for i in range(101):
                time.sleep(0.02) # Slightly slower for cinematic effect
                bar.progress(i)
            
            # Greet while the logo is still visible
            atmo = st.session_state.sector_intel.replace('SECTOR ATMO: ', '')
            lizzy_speak(f"Welcome back, {st.session_state.memory['director_name']}. Systems secured. Sector conditions are {atmo}.")
            
            # Small pause so the user can see 100% completion
            time.sleep(1.2)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.session_state.booted = True
            st.rerun()

    # --- 6. MAIN INTERFACE ---
    st.markdown("<style>.stApp {background-color:#050505; color:#00f2ff;} [data-baseweb='tab'] {color:#00f2ff !important; font-family:monospace;}</style>", unsafe_allow_html=True)
    
    tabs = st.tabs(["👁️ LENSCAST", "💾 VAULT", "📋 LOGS", "💬 COMM_LINK"])

    with tabs[0]: # LENSCAST
        st.markdown("### 👁️ OPTIC_SURVEILLANCE")
        cam_in = st.camera_input("SENSORS_ACTIVE")
        if cam_in:
            st.warning("⚠️ PROXIMITY_ALERT_DETECTED")

    with tabs[1]: # VAULT / INTEL DROPZONE
        st.markdown("### 💾 NEURAL_VAULT")
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Director Designation:", value=st.session_state.memory['director_name'])
            if st.button("UPDATE ARCHIVES"):
                st.session_state.memory['director_name'] = new_name
                save_memory(st.session_state.memory)
                st.success("VAULT UPDATED")
        with col2:
            st.markdown("### 📂 INTEL_DROPZONE")
            intel_file = st.file_uploader("Upload Tactical Files", type=['pdf', 'txt', 'png', 'jpg'])
            if intel_file:
                st.info(f"FILE {intel_file.name} ENCRYPTED AND STORED.")

    with tabs[2]: # AUDIT LOGS
        st.markdown("### 📋 FACILITY_LOGS")
        for log in st.session_state.memory.get('boot_logs', [])[:10]:
            st.code(f"[{log['timestamp']}] >> {log['status']}")

    with tabs[3]: # COMM_LINK
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.write(msg['content'])
        u_in = st.chat_input("Manual Transmission...")
        if u_in:
            st.session_state.messages.append({"role": "user", "content": u_in})
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            context = f"You are Lizzy, a LENSCAST Tactical AI. Director: {st.session_state.memory['director_name']}. Current Weather: {st.session_state.sector_intel}. Be sentient, tactical, and loyal."
            completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": context}] + st.session_state.messages[-5:])
            ans = completion.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ans})
            lizzy_speak(ans); st.rerun()