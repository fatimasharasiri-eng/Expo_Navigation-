import base64
from pathlib import Path
import streamlit as st

from classes.language_manager import LanguageManager   # <<< عدّل المسار إذا ملفك باسم ثاني

# جذر المشروع (المجلد اللي فيه app.py)
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS = BASE_DIR / "assets"
LOGO_PATH = ASSETS / "logo.png"          # <<< مسار الشعار

# أسماء اللغات تظهر على الزر بلغتها الأصلية
LANGS = {"ar": "العربية", "en": "English", "fr": "Français"}

# المفتاح اللي يتخزن فيه LanguageManager في session_state
# <<< استخدم نفس المفتاح اللي تستخدمه باقي صفحاتك (Login/Register...) عشان اللغة تنتقل معهم
LM_KEY = "lang_manager"


# ---------------- اللغة ----------------
def get_lm() -> LanguageManager:
    if LM_KEY not in st.session_state:
        st.session_state[LM_KEY] = LanguageManager("ar")
    return st.session_state[LM_KEY]


# ---------------- Helpers ----------------
def img_b64(path: Path) -> str | None:
    """يحوّل الصورة إلى base64 عشان تنعرض داخل HTML."""
    if not path.exists():
        return None
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def logo_html(cls: str = "logo") -> str:
    src = img_b64(LOGO_PATH)
    if src:
        return f'<img class="{cls}" src="{src}" alt="EXORA">'
    return f'<div class="{cls}-text">EXORA</div>'      # بديل إذا ما وُجد الملف


def photo(path: Path, alt: str = "") -> str:
    src = img_b64(path)
    return (f'<img src="{src}" alt="{alt}">' if src
            else '<div class="photo-ph"></div>')


def render(html: str):
    """تشيل المسافات من بداية الأسطر عشان ما يتحول الـ HTML لـ code block."""
    clean = "".join(line.strip() for line in html.splitlines())
    st.markdown(clean, unsafe_allow_html=True)


def dots(active: int) -> str:
    items = "".join(
        f'<span class="{"active" if i == active else ""}"></span>' for i in range(3)
    )
    return f'<div class="dots">{items}</div>'


# ---------------- الكلاس الرئيسي ----------------
class StartScreens:

    @staticmethod
    def _load_css():
        css_file = ASSETS / "style.css"
        if not css_file.exists():
            st.warning(f"ملف الـ CSS غير موجود: {css_file}")
            return
        st.markdown(
            f"<style>{css_file.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )

    @staticmethod
    def _go(step: int):
        st.session_state["start_step"] = step
        st.rerun()

    # ---------------- الشريط العلوي (زر اللغة) ----------------
    @staticmethod
    def _topbar():
        lm = get_lm()
        current = lm.get_current_language()

        left, _, right = st.columns([2, 3, 1])
        with left:
            # الضغطة تنقل للغة التالية: ar -> en -> fr -> ar
            if st.button(LANGS[current], key="lang_btn"):
                codes = list(LANGS)
                lm.set_language(codes[(codes.index(current) + 1) % len(codes)])
                st.rerun()
        with right:
            st.markdown('<span class="circle-btn">☾</span>', unsafe_allow_html=True)

    # ---------------- شاشة 0: Splash ----------------
    @staticmethod
    def splash_screen():
        lm = get_lm()
        t = lm.get_text
        render(
            f"""
            <div class="page-splash" dir="{lm.get_direction()}">
              {logo_html("logo logo-lg")}
              <p class="tagline">{t("start_tagline")}</p>
            </div>
            """
        )
        st.markdown('<div class="bottom-gap"></div>', unsafe_allow_html=True)
        if st.button(t("start_explore_link"), key="splash_start"):
            StartScreens._go(1)

    # ---------------- شاشة 1: الأجنحة ----------------
    @staticmethod
    def onboarding_1():
        lm = get_lm()
        t = lm.get_text
        render(
            f"""
            <div class="ob-head">{logo_html()}</div>
            <div dir="{lm.get_direction()}" class="ob">
              <div class="search"><span>🔍</span><span>{t("ob1_search")}</span></div>
              <div class="chips">
                <span class="chip active">{t("chip_all")}</span>
                <span class="chip">{t("chip_tech")}</span>
                <span class="chip">{t("chip_culture")}</span>
              </div>

              <div class="cards-stack">
                <div class="card card-back">
                  {photo(ASSETS / "pavilion2.jpg")}
                  <div class="card-cap"><b>{t("pavilion_culture")}</b></div>
                </div>
                <div class="card card-front">
                  {photo(ASSETS / "pavilion1.jpg")}
                  <div class="card-cap"><b>{t("pavilion_innovation")}</b><small>{t("chip_tech")}</small></div>
                </div>
              </div>

              <h2 class="ob-title">{t("ob1_title")}</h2>
              <p class="ob-sub">{t("ob1_sub")}</p>
              {dots(0)}
            </div>
            """
        )
        if st.button(t("next"), key="ob1_next", use_container_width=True):
            StartScreens._go(2)
        if st.button(t("skip"), key="skip"):
            st.switch_page("pages/home.py")

    # ---------------- شاشة 2: الخريطة ----------------
    @staticmethod
    def onboarding_2():
        lm = get_lm()
        t = lm.get_text
        map_src = img_b64(ASSETS / "map.png")
        map_style = f'style="background-image:url({map_src})"' if map_src else ""
        render(
            f"""
            <div class="ob-head">{logo_html()}</div>
            <div dir="{lm.get_direction()}" class="ob">
              <div class="map-box" {map_style}>
                <div class="map-label">{t("pavilion_innovation")}</div>
                <div class="map-pin">📍</div>
                <div class="map-thumb">{photo(ASSETS / "pavilion1.jpg")}</div>
              </div>

              <h2 class="ob-title">{t("ob2_title")}</h2>
              <p class="ob-sub">{t("ob2_sub")}</p>
              {dots(1)}
            </div>
            """
        )
        if st.button(t("next"), key="ob2_next", use_container_width=True):
            StartScreens._go(3)
        if st.button(t("skip"), key="skip"):
            st.switch_page("pages/home.py")

    # ---------------- شاشة 3: المساعد ----------------
    @staticmethod
    def onboarding_3():
        lm = get_lm()
        t = lm.get_text
        render(
            f"""
            <div class="ob-head">{logo_html()}</div>
            <div dir="{lm.get_direction()}" class="ob">
              <div class="chat">
                <div class="chat-head"><span class="avatar">🌐</span><b>{t("assistant_name")}</b></div>
                <div class="bubble bubble-user">{t("chat_user_q")}</div>
                <div class="bubble bubble-bot">{t("chat_bot_a")}</div>
                <div class="chat-card">
                  <div class="chat-card-text">
                    <b>{t("pavilion_innovation")}</b><small>{t("chip_tech")}</small>
                    <span class="mini-btn">{t("view_pavilion")}</span>
                  </div>
                  <div class="chat-card-img">{photo(ASSETS / "pavilion1.jpg")}</div>
                </div>
              </div>

              <h2 class="ob-title">{t("ob3_title")}</h2>
              <p class="ob-sub">{t("ob3_sub")}</p>
              {dots(2)}
            </div>
            """
        )
        if st.button(t("start_exploring"), key="ob3_start", use_container_width=True):
            st.switch_page("pages/home.py")

    # ---------------- الراوتر ----------------
    @staticmethod
    def run():
        StartScreens._load_css()
        StartScreens._topbar()          # زر اللغة يظهر في كل الشاشات
        step = st.session_state.setdefault("start_step", 0)
        [
            StartScreens.splash_screen,
            StartScreens.onboarding_1,
            StartScreens.onboarding_2,
            StartScreens.onboarding_3,
        ][step]()