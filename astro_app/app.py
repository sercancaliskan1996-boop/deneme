import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, date
from geopy.geocoders import Nominatim
import math

# =========================
# DATABASE
# =========================
conn = sqlite3.connect('astro.db', check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    premium INTEGER DEFAULT 0
)
''')
conn.commit()

# =========================
# SECURITY
# =========================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =========================
# AUTH
# =========================
def register(username, password):
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?,?)",
                  (username, hash_password(password)))
        conn.commit()
        return True
    except:
        return False

def login(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    return c.fetchone()

# =========================
# GEO
# =========================
def get_coordinates(city):
    geolocator = Nominatim(user_agent="astro_app")
    loc = geolocator.geocode(city)
    if loc:
        return loc.latitude, loc.longitude
    return None, None

# =========================
# UTIL
# =========================
def day_of_year(d, m, y):
    return (date(y, m, d) - date(y, 1, 1)).days + 1

# =========================
# ZODIAC
# =========================
def zodiac_sign(lon):
    signs = [
        "Koç","Boğa","İkizler","Yengeç","Aslan","Başak",
        "Terazi","Akrep","Yay","Oğlak","Kova","Balık"
    ]
    index = int((lon % 360) / 30)
    return signs[index]

# =========================
# PRODUCTION ASTRO ENGINE (NO EPHEM)
# =========================
def get_planets(day, month, year):
    doy = day_of_year(day, month, year)

    # --- simplified astronomical cycles ---

    # Sun (year cycle)
    sun_lon = (doy / 365.25) * 360

    # Moon (29.53 day cycle)
    moon_lon = (doy % 29.53) / 29.53 * 360

    # Mercury (88 days)
    mercury_lon = (doy % 88) / 88 * 360

    # Venus (225 days)
    venus_lon = (doy % 225) / 225 * 360

    # Mars (687 days)
    mars_lon = (doy % 687) / 687 * 360

    # Jupiter (11.8 years approx)
    jupiter_lon = (doy % 4332) / 4332 * 360

    # Saturn (29.4 years approx)
    saturn_lon = (doy % 10759) / 10759 * 360

    return {
        "Sun": zodiac_sign(sun_lon),
        "Moon": zodiac_sign(moon_lon),
        "Mercury": zodiac_sign(mercury_lon),
        "Venus": zodiac_sign(venus_lon),
        "Mars": zodiac_sign(mars_lon),
        "Jupiter": zodiac_sign(jupiter_lon),
        "Saturn": zodiac_sign(saturn_lon),
        "Ascendant": zodiac_sign((sun_lon + moon_lon) % 360)
    }

# =========================
# DAILY HOROSCOPE
# =========================
def daily_horoscope(planets):
    return f"""
☀ Güneş: {planets['Sun']}
🌙 Ay: {planets['Moon']}
☿ Merkür: {planets['Mercury']}
♀ Venüs: {planets['Venus']}
♂ Mars: {planets['Mars']}
♃ Jüpiter: {planets['Jupiter']}
♄ Satürn: {planets['Saturn']}
🌅 Yükselen: {planets['Ascendant']}

🔮 Bugün enerjin Güneş ve Ay kombinasyonuna göre şekilleniyor.
İletişim (Merkür) ve ilişkiler (Venüs) önemli.
"""

# =========================
# AI COMMENT (SIMPLIFIED)
# =========================
def ai_comment(planets):
    return f"""
☀ {planets['Sun']} burcu güçlü bir karakter yapısı gösterir.
🌙 {planets['Moon']} duygusal derinlik verir.
♀ {planets['Venus']} aşk enerjini belirler.

Genel olarak dönüşüm ve farkındalık sürecindesin.
"""

# =========================
# UI
# =========================
st.title("🔮 Astro Pro V6 - Production Engine (No External Astro Lib)")

menu = st.sidebar.selectbox("Menü", ["Kayıt","Giriş","Uygulama"])

# =========================
# REGISTER
# =========================
if menu == "Kayıt":
    u = st.text_input("Kullanıcı")
    p = st.text_input("Şifre", type="password")

    if st.button("Kayıt Ol"):
        if register(u,p):
            st.success("Kayıt başarılı")
        else:
            st.error("Hata")

# =========================
# LOGIN
# =========================
elif menu == "Giriş":
    u = st.text_input("Kullanıcı")
    p = st.text_input("Şifre", type="password")

    if st.button("Giriş"):
        user = login(u,p)
        if user:
            st.session_state['user'] = user
            st.success("Giriş başarılı")
        else:
            st.error("Hatalı giriş")

# =========================
# APP
# =========================
elif menu == "Uygulama":

    if "user" not in st.session_state:
        st.warning("Önce giriş yap")
    else:
        user = st.session_state['user']

        st.subheader(f"Hoş geldin {user[1]}")

        col1,col2,col3 = st.columns(3)

        with col1:
            day = st.number_input("Gün",1,31)
        with col2:
            month = st.number_input("Ay",1,12)
        with col3:
            year = st.number_input("Yıl",1900,2026)

        city = st.text_input("Doğum Şehri")

        if st.button("Doğum Haritası Oluştur"):

            lat, lon = get_coordinates(city)

            if not lat:
                st.error("Şehir bulunamadı")
            else:

                planets = get_planets(day, month, year)

                st.subheader("🪐 Gezegenler")
                for k,v in planets.items():
                    st.write(f"{k}: {v}")

                st.subheader("📅 Günlük Yorum")
                st.write(daily_horoscope(planets))

                st.subheader("🧠 AI Yorum")
                st.write(ai_comment(planets))

                if user[3] == 0:
                    st.warning("Premium: gelişmiş transit + açı sistemi kilitli")
                else:
                    st.success("Premium aktif - V7 (aspect engine) hazır olacak")
