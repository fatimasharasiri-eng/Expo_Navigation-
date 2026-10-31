"""EXORA – main Streamlit app.

Run with:   python -m streamlit run streamapp.py

All the page logic comes from the files your team wrote (log_in, account, ai,
map, ar, home). They are combined here as one app so the new design (splash,
onboarding, floating navigation bar) can sit around them. The classes in
./classes are used exactly as written.

Flow:
  splash -> onb1 -> onb2 -> onb3 -> home (guest)  or  welcome -> login / signup
  signup -> verify_email -> account_created -> home
  login -> forgot -> reset_code -> reset_new -> reset_done -> login
  home <-> map / ar / account   (floating bar)      home -> chat (assistant orb)
"""
import base64
import html
import secrets
import time
from pathlib import Path

import streamlit as st
from PIL import Image
import math
from classes.authentication import Authentication
from classes.language_manager import LanguageManager
from ui_text import EXTRA, MESSAGE_KEYS

BASE = Path(__file__).parent
IMG = BASE / "images"

st.set_page_config(
    page_title="EXORA",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------------------------------------------------
# Where the buttons lead (change these to re-wire the flow)
# ----------------------------------------------------------------------
AFTER_SPLASH = "onb1"
AFTER_ONBOARDING = "welcome"        # "ابدأ الاستكشاف" on the last onboarding screen
AFTER_LOGIN = "home"
SKIP_TARGET = "welcome"          # "تخطي" on onboarding

AUTH_PAGES = ("welcome", "login", "signup", "verify_email", "account_created",
              "forgot", "reset_code", "reset_new", "reset_done")
FLOW_PAGES = ("splash", "onb1", "onb2", "onb3") + AUTH_PAGES
DOCK_PAGES = ("home", "map", "ar", "account", "pavilion")

LANGUAGES = {"العربية 🇸🇦": "ar", "English 🇬🇧": "en", "Français 🇫🇷": "fr"}
CODE_LIFETIME = 300  # seconds a sign-up verification code stays valid

# ----------------------------------------------------------------------
# Session state (same names the original files use)
# ----------------------------------------------------------------------
for _key, _default in {
    "page": "splash",
    "language": "ar",
    "logged_in": False,
    "current_user": None,
    "messages": [],
    "onb_chip": "all",
}.items():
    st.session_state.setdefault(_key, _default)


@st.cache_resource
def get_auth() -> Authentication:
    """One Authentication object shared by every visitor (kept while the server runs)."""
    return Authentication()


auth = get_auth()
st.session_state.auth = auth   # account.py reads st.session_state.auth

language = LanguageManager(st.session_state.language)


def t(key: str, **values) -> str:
    """Translate: LanguageManager first, then ui_text.EXTRA, then English."""
    text = language.get_text(key)
    if text == key:
        lang_code = language.get_current_language()
        text = EXTRA.get(lang_code, {}).get(key) or EXTRA["en"].get(key, key)
    return text.format(**values) if values else text


def tm(message: str) -> str:
    """Translate an English message returned by the Authentication class."""
    return t(MESSAGE_KEYS.get(message, message))


def is_rtl() -> bool:
    return language.get_direction() == "rtl"


# ----------------------------------------------------------------------
# Assets + CSS
# ----------------------------------------------------------------------
# Fallback texts: used only if ui_text.py on this computer is an older copy without these keys.
_FALLBACK = {'ar': {'greet_name': 'أهلاً بك، {name}', 'greet_guest': 'أهلاً بك', 'chat_tagline': 'مساعدك الذكي متعدد اللغات للمعرض', 'chat_assistant': 'مساعد إكسورا', 'chat_hello1': 'أهلًا بك 👋', 'chat_hello2': 'أنا مساعدك الذكي في المعرض.', 'chat_how': 'كيف أقدر أساعدك اليوم؟', 'chat_s1': 'اكتشاف الأجنحة', 'chat_s2': 'الوصول إلى وجهتك', 'chat_s3': 'استكشاف مسارات المعرض', 'chat_s4': 'الإجابة بعدة لغات', 'chat_input': 'اكتب رسالتك لإكسورا...', 'chat_menu_clear': 'مسح المحادثة', 'find_route_map': 'البحث عن أفضل مسار', 'map_hint': 'اختر نقطة الانطلاق والوجهة لعرض المسار.', 'map_crowd_label': 'الازدحام على المسار', 'occupancy_rate': 'نسبة الإشغال', 'map_section': 'الخريطة والمسار المقترح', 'ar_page_title': 'التوجيه بالواقع المعزز', 'ar_page_sub': 'حدّد نقطة البداية والوجهة للبحث عن المسار.', 'ar_start_label': 'نقطة البداية', 'ar_start_ph': 'اختر نقطة البداية', 'ar_goal_ph': 'اختر الوجهة', 'ar_route_title': 'المسار المقترح', 'ar_found': 'تم العثور على مسار', 'ar_total': 'المسافة الكلية: {d} متر', 'ar_details': 'عرض تفاصيل المسار', 'ar_next_stop': 'المحطة التالية', 'ar_away': 'تبعد {d} أمتار', 'ar_cam_title': 'ابدأ التوجيه عبر الكاميرا', 'ar_cam_text': 'اتبع الأسهم للوصول إلى وجهتك', 'ar_cam_btn': 'ابدأ التوجيه بالواقع المعزز', 'pav_innovation': 'جناح الابتكار', 'pav_culture': 'جناح الثقافة', 'pav_art': 'الفن التفاعلي', 'pav_innovation_meta': 'تقنية · تجارب تفاعلية', 'pav_art_meta': 'فن · تجارب غامرة', 'pav_about_title': 'عن الجناح', 'pav_innovation_about': 'مساحة تعرض أحدث التقنيات والابتكارات، حيث يستطيع الزوار تجربة الشاشات التفاعلية والعروض الضوئية بأنفسهم.', 'pav_art_about': 'جناح يجمع الفن والتقنية في تجارب غامرة تتفاعل مع حركتك وتنقلك بين الألوان والأصوات والأضواء.', 'pav_innovation_h1': 'شاشات وعروض تفاعلية', 'pav_innovation_h2': 'ستائر ضوئية وتجارب غامرة', 'pav_innovation_h3': 'مناسب لجميع الأعمار', 'pav_art_h1': 'أعمال فنية تتفاعل معك', 'pav_art_h2': 'إضاءة وصوت وحركة', 'pav_art_h3': 'مناسب لجميع الأعمار', 'pav_show_map': 'اعرض على الخريطة', 'pav_open_ar': 'ابدأ الملاحة بالواقع المعزز', 'pav_highlights': 'أبرز ما ستجده'}, 'en': {'greet_name': 'Welcome, {name}', 'greet_guest': 'Welcome', 'chat_tagline': 'Your multilingual Expo assistant', 'chat_assistant': 'EXORA Assistant', 'chat_hello1': 'Welcome 👋', 'chat_hello2': "I'm your smart assistant at the Expo.", 'chat_how': 'How can I help you today?', 'chat_s1': 'Discover pavilions', 'chat_s2': 'Get to your destination', 'chat_s3': 'Explore Expo routes', 'chat_s4': 'Answers in many languages', 'chat_input': 'Message EXORA...', 'chat_menu_clear': 'Clear chat', 'find_route_map': 'Find best route', 'map_hint': 'Choose a starting point and destination to see the route.', 'map_crowd_label': 'Crowd on route', 'occupancy_rate': 'Occupancy', 'map_section': 'Map and suggested route', 'ar_page_title': 'AR Navigation', 'ar_page_sub': 'Choose a starting point and destination to find a route.', 'ar_start_label': 'Starting point', 'ar_start_ph': 'Choose starting point', 'ar_goal_ph': 'Choose destination', 'ar_route_title': 'Suggested route', 'ar_found': 'Route found', 'ar_total': 'Total distance: {d} m', 'ar_details': 'View route details', 'ar_next_stop': 'Next stop', 'ar_away': '{d} meters away', 'ar_cam_title': 'Start camera guidance', 'ar_cam_text': 'Follow the arrows to reach your destination', 'ar_cam_btn': 'Start AR guidance', 'pav_innovation': 'Innovation Pavilion', 'pav_culture': 'Culture Pavilion', 'pav_art': 'Interactive Art', 'pav_innovation_meta': 'Tech · Interactive experiences', 'pav_art_meta': 'Art · Immersive experiences', 'pav_about_title': 'About the pavilion', 'pav_innovation_about': 'A space showcasing the latest technology and innovation, where visitors can try interactive screens and light installations themselves.', 'pav_art_about': 'A pavilion that blends art and technology into immersive experiences that react to your movement through colour, sound and light.', 'pav_innovation_h1': 'Interactive screens and shows', 'pav_innovation_h2': 'Light curtains and immersive displays', 'pav_innovation_h3': 'Suitable for all ages', 'pav_art_h1': 'Artworks that react to you', 'pav_art_h2': 'Light, sound and motion', 'pav_art_h3': 'Suitable for all ages', 'pav_show_map': 'Show on map', 'pav_open_ar': 'Start AR navigation', 'pav_highlights': 'What you will find'}, 'fr': {'greet_name': 'Bienvenue, {name}', 'greet_guest': 'Bienvenue', 'chat_tagline': "Votre assistant multilingue de l'exposition", 'chat_assistant': 'Assistant EXORA', 'chat_hello1': 'Bienvenue 👋', 'chat_hello2': "Je suis votre assistant intelligent à l'exposition.", 'chat_how': "Comment puis-je vous aider aujourd'hui ?", 'chat_s1': 'Découvrir les pavillons', 'chat_s2': 'Rejoindre votre destination', 'chat_s3': 'Explorer les parcours', 'chat_s4': 'Réponses en plusieurs langues', 'chat_input': 'Écrivez à EXORA...', 'chat_menu_clear': 'Effacer la conversation', 'find_route_map': 'Trouver le meilleur itinéraire', 'map_hint': "Choisissez un départ et une destination pour afficher l'itinéraire.", 'map_crowd_label': "Affluence sur l'itinéraire", 'occupancy_rate': "Taux d'occupation", 'map_section': 'Carte et itinéraire proposé', 'ar_page_title': 'Guidage en réalité augmentée', 'ar_page_sub': 'Choisissez un départ et une destination pour trouver un itinéraire.', 'ar_start_label': 'Point de départ', 'ar_start_ph': 'Choisir le départ', 'ar_goal_ph': 'Choisir la destination', 'ar_route_title': 'Itinéraire proposé', 'ar_found': 'Itinéraire trouvé', 'ar_total': 'Distance totale : {d} m', 'ar_details': 'Voir les détails', 'ar_next_stop': 'Prochaine étape', 'ar_away': 'à {d} mètres', 'ar_cam_title': 'Démarrer le guidage par caméra', 'ar_cam_text': "Suivez les flèches jusqu'à votre destination", 'ar_cam_btn': 'Démarrer le guidage AR', 'pav_innovation': "Pavillon de l'innovation", 'pav_culture': 'Pavillon de la culture', 'pav_art': 'Art interactif', 'pav_innovation_meta': 'Tech · Expériences interactives', 'pav_art_meta': 'Art · Expériences immersives', 'pav_about_title': 'À propos du pavillon', 'pav_innovation_about': 'Un espace présentant les dernières technologies et innovations, où les visiteurs peuvent essayer eux-mêmes écrans interactifs et installations lumineuses.', 'pav_art_about': 'Un pavillon qui mêle art et technologie dans des expériences immersives qui réagissent à vos mouvements, entre couleurs, sons et lumières.', 'pav_innovation_h1': 'Écrans et démonstrations interactifs', 'pav_innovation_h2': 'Rideaux lumineux et expériences immersives', 'pav_innovation_h3': 'Pour tous les âges', 'pav_art_h1': 'Œuvres qui réagissent à vous', 'pav_art_h2': 'Lumière, son et mouvement', 'pav_art_h3': 'Pour tous les âges', 'pav_show_map': 'Voir sur la carte', 'pav_open_ar': 'Lancer la navigation AR', 'pav_highlights': 'À découvrir'}}
for _lang, _texts in _FALLBACK.items():
    for _k, _v in _texts.items():
        EXTRA.setdefault(_lang, {}).setdefault(_k, _v)


IMAGES = {
    "flower": "flower.jpg",
    "innovation": "innovation.jpg",
    "art": "interactive-art.jpg",
    "orb": "assistant-orb.jpg",
    "ar-banner": "../assets/ar-banner.jpg",
    "culture": "culture.jpg",
}


@st.cache_data
def data_uri(path: str) -> str:
    p = Path(path)
    mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def logo_html(name: str = "logo.png") -> str:
    return f'<div class="brand"><img src="{data_uri(str(IMG / name))}" alt="EXORA"></div>'


def inject_css(page: str) -> None:
    css = (BASE / "exora.css").read_text(encoding="utf-8")
    variables = ":root{" + "".join(
        f'--img-{name}:url("{data_uri(str(IMG / file))}");'
        for name, file in IMAGES.items()
        if (IMG / file).exists()
    ) + f"--dir:{language.get_direction()};}}"
    st.markdown(f"<style>{css}\n{variables}</style>", unsafe_allow_html=True)
    # one class per page so the stylesheet can target each screen
    st.markdown(
        f"<style>.stApp{{--page:'{page}';}}</style>"
        f'<div class="page-marker page-{page}"></div>',
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------
def go(page: str) -> None:
    st.session_state.page = page


def flash(message: str) -> None:
    st.session_state.flash = message


def set_language(widget_key: str) -> None:
    st.session_state.language = LANGUAGES[st.session_state[widget_key]]


def language_selector(widget_key: str, collapsed: bool = False) -> None:
    labels = list(LANGUAGES)
    current = next(k for k, v in LANGUAGES.items() if v == st.session_state.language)
    st.selectbox(
        "Language / اللغة / Langue",
        labels,
        index=labels.index(current),
        key=widget_key,
        label_visibility="collapsed" if collapsed else "visible",
        on_change=set_language,
        args=(widget_key,),
    )


def language_button() -> None:
    """Language drop-down pinned to the top corner of the screen (welcome + login)."""
    with st.container(key="lang_box"):
        language_selector("auth_language", collapsed=True)


def cycle_language() -> None:
    order = list(LANGUAGES.values())
    st.session_state.language = order[(order.index(st.session_state.language) + 1) % len(order)]


def language_pill() -> None:
    """Round pill (globe + name of the next language) that switches the language."""
    order = list(LANGUAGES.values())
    nxt = order[(order.index(st.session_state.language) + 1) % len(order)]
    name = next(k for k, v in LANGUAGES.items() if v == nxt).split(" ")[0]
    st.button(name, key="lang_pill", icon=":material/language:", on_click=cycle_language)


def top_row(start: str | None = None, target: str | None = None, on_click=None, args=()) -> None:
    """Top row of the new screens: back arrow / skip / logo on the start side, language pill on the end side."""
    with st.container(key="top_row"):
        start_col, end_col = st.columns(2, vertical_alignment="center")
        with start_col:
            if start == "back":
                st.button(back_arrow(), key="back_btn", on_click=on_click or go, args=args if on_click else (target,))
            elif start == "skip":
                st.button(t("skip"), key="onb_skip", on_click=go, args=(target,))
            elif start == "logo":
                st.markdown(logo_html(), unsafe_allow_html=True)
        with end_col:
            language_pill()


def num(value) -> str:
    """Numbers: Arabic-Indic digits when the language is Arabic."""
    text = f"{float(value):g}"
    return text.translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")) if st.session_state.language == "ar" else text


def current_name() -> str | None:
    if st.session_state.get("logged_in") and st.session_state.get("current_user"):
        user = auth.users.get(st.session_state.current_user, {})
        return user.get("name") or st.session_state.current_user
    return None


def new_code() -> str:
    return "".join(secrets.choice("0123456789") for _ in range(6))


def back_arrow() -> str:
    return "›" if is_rtl() else "‹"


def forward_arrow() -> str:
    return "←" if is_rtl() else "→"


def topbar(back_to: str | None = None, show_logo: bool = True, lang_button: bool = False) -> None:
    """Back button (start side) + centred logo. Used by every auth screen."""
    back_col, logo_col, end_col = st.columns([1, 3, 1], vertical_alignment="center")
    with back_col:
        if back_to:
            st.button(back_arrow(), key="back_btn", on_click=go, args=(back_to,))
    with logo_col:
        if show_logo:
            st.markdown(logo_html(), unsafe_allow_html=True)
    with end_col:
        if lang_button:
            language_button()


def screen_title(title: str, subtitle: str = "", strong: str = "") -> None:
    extra = f"<strong dir='ltr'>{html.escape(strong)}</strong>" if strong else ""
    st.markdown(
        f'<h1 class="title">{title}</h1><p class="subtitle">{subtitle}{extra}</p>',
        unsafe_allow_html=True,
    )


def start_verification(username: str) -> None:
    """Open the e-mail verification step for a freshly registered user."""
    user = auth.users[username]
    st.session_state.verify = {
        "username": username,
        "email": user["email"],
        "code": new_code(),
        "expiry": time.time() + CODE_LIFETIME,
    }
    st.session_state.page = "verify_email"


def cancel_signup() -> None:
    """Go back to the sign-up form and free the half-finished account."""
    pending = st.session_state.pop("verify", None)
    if pending:
        user = auth.users.get(pending["username"])
        if user and not user.get("verified", True):
            del auth.users[pending["username"]]
    st.session_state.page = "signup"


# ======================================================================
# 1. Splash
# ======================================================================
def render_splash() -> None:
    with st.container(key="splash_lang"):
        language_selector("splash_language", collapsed=True)

    st.markdown(
        '<div class="splash"><div class="ring ring--1"></div>'
        '<div class="ring ring--2"></div><div class="ring ring--3"></div>'
        f'<div class="splash__center"><img class="splash__logo" src="{data_uri(str(IMG / "logo.png"))}" alt="EXORA">'
        f'<p class="splash__tagline">{t("splash_tagline")}</p></div></div>',
        unsafe_allow_html=True,
    )
    with st.container(key="splash_bottom"):
        st.markdown('<div class="splash__dash"></div>', unsafe_allow_html=True)
        st.button(f'{t("start_exploring")}  {forward_arrow()}', key="start",
                  on_click=go, args=(AFTER_SPLASH,))


# ======================================================================
# 2. Onboarding (3 screens)
# ======================================================================
PAVILION_CARDS = [  # (title key, meta key, image, tag)
    ("pav_innovation", "meta_tech", "innovation", "tech"),
    ("pav_culture", "meta_culture", "art", "culture"),
]


def set_chip(chip: str) -> None:
    st.session_state.onb_chip = chip


def visual_pavilions() -> None:
    st.markdown(
        '<div class="pcards2">'
        '<div class="pcard2 pcard2--front"><div class="pcard2__img pcard2__img--innovation"></div>'
        f'<div class="pcard2__title">{t("pav_innovation")}</div><div class="pcard2__meta">{t("meta_tech")}</div></div>'
        '<div class="pcard2 pcard2--back"><div class="pcard2__img pcard2__img--culture"></div>'
        f'<div class="pcard2__title">{t("pav_culture")}</div></div></div>',
        unsafe_allow_html=True,
    )


def visual_map() -> None:
    blocks = "".join(
        f'<i class="map-block" style="{s}"></i>' for s in (
            "left:6%;top:8%", "left:40%;top:30%;width:14%", "left:10%;top:36%;width:15%;height:8%",
            "left:70%;top:60%", "left:44%;top:68%;width:20%", "left:74%;top:6%;width:20%;height:9%")
    ) + "".join(
        f'<i class="map-dot" style="{s}"></i>' for s in (
            "left:18%;top:62%", "left:60%;top:12%", "left:86%;top:42%"))
    st.markdown(
        f'<div class="map-card"><div class="map-card__roads">{blocks}</div>'
        '<svg class="map-route" viewBox="0 0 400 330" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M200 70 C 270 90, 280 140, 240 170 S 150 210, 215 270"/>'
        '<circle class="start" cx="215" cy="270" r="11"/>'
        '<path class="pin" d="M200 40a16 16 0 0 1 16 16c0 12-16 30-16 30s-16-18-16-30a16 16 0 0 1 16-16z"/>'
        '<circle cx="200" cy="56" r="6" fill="#fff"/></svg>'
        f'<span class="map-label">{t("pav_innovation")}</span>'
        '<div class="ar-thumb"><span class="ar-thumb__badge">AR</span>'
        '<div class="ar-thumb__chevrons"><svg width="54" height="54" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M6 11l6-6 6 6M6 19l6-6 6 6"/></svg></div></div></div>',
        unsafe_allow_html=True,
    )


def visual_chat() -> None:
    st.markdown(
        '<div class="chat-card">'
        f'<div class="chat-head"><span class="orb"></span>{t("assistant_name")}</div>'
        f'<div class="bubble bubble--user">{t("sample_question")}</div>'
        f'<div class="bubble bubble--bot">{t("sample_answer")}</div>'
        '<div class="mini-card"><div class="mini-card__img"></div><div class="mini-card__body">'
        f'<div class="mini-card__title">{t("pav_innovation")}</div>'
        f'<div class="mini-card__meta">{t("meta_tech")}</div>'
        f'<div class="btn btn--tonal btn--small">{t("view_pavilion")}</div></div></div></div>',
        unsafe_allow_html=True,
    )


ONBOARDING = {
    "onb1": dict(visual=visual_pavilions, title="onb1_title", text="onb1_text",
                 primary="next", primary_to="onb2", prev=None),
    "onb2": dict(visual=visual_map, title="onb2_title", text="onb2_text",
                 primary="next", primary_to="onb3", prev="onb1"),
    "onb3": dict(visual=visual_chat, title="onb3_title", text="onb3_text",
                 primary="start_explore_btn", primary_to=AFTER_ONBOARDING, prev="onb2"),
}


def render_onboarding(page: str) -> None:
    data = ONBOARDING[page]
    index = list(ONBOARDING).index(page)

    top_row("skip" if page != "onb3" else None, SKIP_TARGET)
    st.markdown(logo_html(), unsafe_allow_html=True)
    data["visual"]()

    dots = "".join(f'<span class="dot{" dot--on" if i == index else ""}"></span>' for i in range(len(ONBOARDING)))
    st.markdown(
        f'<div class="onb__text"><h1 class="onb__title">{t(data["title"])}</h1>'
        f'<p class="onb__desc">{t(data["text"])}</p><div class="dots">{dots}</div></div>',
        unsafe_allow_html=True,
    )
    st.button(t(data["primary"]), key="onb_next", type="primary", on_click=go, args=(data["primary_to"],))
    if data["prev"]:
        st.button(t("previous"), key="onb_prev", on_click=go, args=(data["prev"],))


# ======================================================================
# 3. Welcome + authentication (logic from log_in.py)
# ======================================================================
GOOGLE_SVG = (
    '<svg width="22" height="22" viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 '
    '9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 '
    '9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 '
    '5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99'
    '-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>'
    '<path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22'
    '-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>'
)
APPLE_SVG = (
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="#1a1535"><path d="M12.152 6.896c-.948 0-2.415-1.078-3.96'
    '-1.04-2.04.027-3.91 1.183-4.961 3.014-2.117 3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 '
    '1.52-.065 2.09-.987 3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636'
    '-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324'
    '-4.39-2.376-2-.156-3.675 1.09-4.61 1.09zM15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 '
    '1.818-.78.896-1.454 2.338-1.273 3.714 1.338.104 2.715-.688 3.559-1.701"/></svg>'
)


def social_row(label_key: str = "or") -> None:
    """Google / Apple are pictures only (no sign-in behind them)."""
    st.markdown(
        f'<div class="divider">{t(label_key)}</div>'
        f'<div class="social" aria-hidden="true"><div class="social__btn">{GOOGLE_SVG}<span>Google</span></div>'
        f'<div class="social__btn">{APPLE_SVG}<span>Apple</span></div></div>',
        unsafe_allow_html=True,
    )


def guest_button() -> None:
    st.button(f'{t("continue_guest")}  {forward_arrow()}', key="guest", on_click=go, args=("home",))


def render_welcome() -> None:
    with st.container(key="auth_card"):
        topbar(back_to="onb3", lang_button=True)
        screen_title(t("welcome_title"), t("welcome_sub"))
        st.button(t("login"), key="welcome_login", on_click=go, args=("login",))
        st.button(t("register"), key="welcome_signup", on_click=go, args=("signup",))
        st.button(t("guest_enter"), key="guest", on_click=go, args=("home",))


def render_login() -> None:
    with st.container(key="auth_card"):
        topbar(back_to="welcome", lang_button=True)
        screen_title(t("login_title"), t("login_sub"))

        with st.form("login_form", border=False):
            username = st.text_input(t("username"), key="login_username", placeholder=t("username_ph"))
            password = st.text_input(t("password"), type="password", key="login_password",
                                     placeholder="••••••••")
            st.markdown('<div class="form-gap"></div>', unsafe_allow_html=True)
            submitted = st.form_submit_button(t("login"), type="primary", key="login_submit")
        st.button(t("forgot_password"), key="forgot_link", on_click=go, args=("forgot",))

        if submitted:
            username = username.strip()
            if auth.login(username, password):
                user = auth.users[username]
                if user.get("verified", True) is False:      # registered but never confirmed
                    start_verification(username)
                    flash(t("verify_first"))
                else:
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    flash(t("welcome_user", name=user.get("name", username)))
                    st.session_state.page = AFTER_LOGIN
                st.rerun()
            else:
                st.error(t("invalid_credentials"))
        st.button(t("no_account"), key="to_signup", on_click=go, args=("signup",))
        guest_button()


def render_signup() -> None:
    with st.container(key="auth_card"):
        topbar(back_to="welcome")
        screen_title(t("signup_title"), t("signup_sub"))

        with st.form("signup_form", border=False):
            name = st.text_input(t("name"), key="signup_name", placeholder=t("name_ph"))
            email = st.text_input(t("email"), key="signup_email", placeholder="name@example.com")
            username = st.text_input(t("username"), key="signup_username",
                                     placeholder=t("choose_username_ph"))
            password = st.text_input(t("password"), type="password", key="signup_password",
                                     placeholder=t("password_ph"))
            st.markdown(f'<div class="field__hint">{t("password_hint")}</div><div class="form-gap"></div>',
                        unsafe_allow_html=True)
            submitted = st.form_submit_button(t("signup_btn"), type="primary", key="signup_submit")

        if submitted:
            email, username, name = email.strip(), username.strip(), name.strip()
            if not name:
                st.warning(t("enter_name"))
            else:
                ok, message = auth.sign_up(email, username, password)
                if ok:
                    auth.users[username]["name"] = name
                    auth.users[username]["verified"] = False
                    start_verification(username)
                    st.rerun()
                elif message in ("Invalid email", "Username already exists", "Email already registered"):
                    st.error(tm(message))
                else:
                    st.warning(tm(message))
        st.button(t("have_account_login"), key="to_login", on_click=go, args=("login",))
        guest_button()


def render_verify_email() -> None:
    pending = st.session_state.get("verify")
    if not pending:
        st.session_state.page = "signup"
        st.rerun()

    with st.container(key="auth_card"):
        st.button(back_arrow(), key="back_btn", on_click=cancel_signup)
        st.markdown(logo_html(), unsafe_allow_html=True)
        screen_title(t("verify_email_title"), t("verify_email_sub"), strong=pending["email"])

        # No e-mail service is connected yet, so the code is shown here (same idea as the demo code).
        st.info(f'{t("demo_code")}: **{pending["code"]}**')

        with st.form("verify_form", border=False):
            code = st.text_input(t("verification_code"), key="verify_code", max_chars=6,
                                 placeholder="— — — — — —", label_visibility="collapsed")
            st.markdown(f'<p class="otp__hint">{t("code_hint")}</p>', unsafe_allow_html=True)
            submitted = st.form_submit_button(t("confirm_email"), type="primary", key="verify_submit")

        if submitted:
            if time.time() > pending["expiry"]:
                st.error(t("code_expired"))
            elif code.strip() != pending["code"]:
                st.error(t("invalid_code"))
            else:
                username = pending["username"]
                auth.users[username]["verified"] = True
                st.session_state.logged_in = True
                st.session_state.current_user = username
                st.session_state.pop("verify", None)
                st.session_state.page = "account_created"
                st.rerun()

        if st.button(t("resend_code"), key="resend_verify"):
            pending["code"], pending["expiry"] = new_code(), time.time() + CODE_LIFETIME
            st.toast(t("code_resent"))
            st.rerun()
        st.button(t("change_email"), key="change_email_verify", on_click=cancel_signup)


def render_account_created() -> None:
    with st.container(key="auth_card"):
        st.markdown(logo_html(), unsafe_allow_html=True)
        screen_title(t("created_title"), t("created_sub"))
        st.markdown('<div class="success-badge">✓</div>', unsafe_allow_html=True)
        st.button(t("start_explore_btn"), key="created_start", type="primary", on_click=go, args=(AFTER_LOGIN,))


# ---- forgot password (3 steps: e-mail -> code -> new password) ----------
def render_forgot() -> None:
    with st.container(key="auth_card"):
        topbar(back_to="login")
        screen_title(t("forgot_title"), t("forgot_sub"))

        with st.form("forgot_form", border=False):
            email = st.text_input(t("email"), key="forgot_email_input", placeholder="name@example.com")
            st.markdown(f'<div class="field__hint">{t("forgot_hint")}</div><div class="form-gap"></div>',
                        unsafe_allow_html=True)
            submitted = st.form_submit_button(t("send_code"), type="primary", key="forgot_submit")
        st.button(t("back_to_login"), key="back_login", on_click=go, args=("login",))

        if submitted:
            email = email.strip()
            success, code = auth.generate_reset_code(email)
            if success:
                st.session_state.reset_email = email
                st.session_state.reset_demo_code = code
                st.session_state.page = "reset_code"
                st.rerun()
            else:
                st.error(t("email_not_found"))


def render_reset_code() -> None:
    email = st.session_state.get("reset_email")
    if not email:
        st.session_state.page = "forgot"
        st.rerun()

    with st.container(key="auth_card"):
        topbar(back_to="forgot")
        screen_title(t("code_title"), t("code_sub"), strong=email)
        st.info(f'{t("demo_code")}: **{st.session_state.get("reset_demo_code", "")}**')

        with st.form("code_form", border=False):
            code = st.text_input(t("verification_code"), key="reset_code_input", max_chars=6,
                                 placeholder="— — — — — —", label_visibility="collapsed")
            st.markdown(f'<p class="otp__hint">{t("code_hint")}</p>', unsafe_allow_html=True)
            submitted = st.form_submit_button(t("verify"), type="primary", key="code_submit")

        if submitted:
            saved = auth.reset_codes.get(email)
            if not saved:
                st.error(t("no_reset_request"))
            elif time.time() > saved["expiry"]:
                st.error(t("code_expired"))
            elif saved["code"] != code.strip():
                st.error(t("invalid_code"))
            else:
                st.session_state.reset_verified_code = code.strip()
                st.session_state.page = "reset_new"
                st.rerun()

        if st.button(t("resend_code"), key="resend_reset"):
            success, new = auth.generate_reset_code(email)
            if success:
                st.session_state.reset_demo_code = new
                st.toast(t("code_resent"))
                st.rerun()
        st.button(t("change_email"), key="change_email_reset", on_click=go, args=("forgot",))


def render_reset_new() -> None:
    email = st.session_state.get("reset_email")
    code = st.session_state.get("reset_verified_code")
    if not email or not code:
        st.session_state.page = "forgot"
        st.rerun()

    with st.container(key="auth_card"):
        topbar(back_to="reset_code")
        screen_title(t("newpw_title"), t("newpw_sub"))

        with st.form("newpw_form", border=False):
            new_password = st.text_input(t("new_password"), type="password", key="reset_new_password",
                                         placeholder="••••••••")
            st.markdown(f'<div class="field__hint">{t("password_hint")}</div>', unsafe_allow_html=True)
            confirm = st.text_input(t("confirm_password"), type="password", key="reset_confirm_password",
                                    placeholder="••••••••")
            st.markdown('<div class="form-gap"></div>', unsafe_allow_html=True)
            submitted = st.form_submit_button(t("save_password"), type="primary", key="newpw_submit")

        if submitted:
            if new_password != confirm:
                st.error(t("passwords_mismatch"))
            else:
                success, message = auth.reset_password(email, code, new_password)
                if success:
                    for k in ("reset_email", "reset_demo_code", "reset_verified_code"):
                        st.session_state.pop(k, None)
                    st.session_state.page = "reset_done"
                    st.rerun()
                else:
                    (st.warning if message.startswith("Password must") else st.error)(tm(message))


def render_reset_done() -> None:
    with st.container(key="auth_card"):
        st.markdown(logo_html(), unsafe_allow_html=True)
        screen_title(t("pwchanged_title"), t("pwchanged_sub"))
        st.markdown('<div class="success-badge">✓</div>', unsafe_allow_html=True)
        st.button(t("pwchanged_btn"), key="reset_done_btn", type="primary", on_click=go, args=("login",))


# ======================================================================
# 4. Home (new design) + floating navigation
# ======================================================================
WINGS = [  # (title key, meta key, image)
    ("pav_innovation", "pav_innovation_meta", "innovation"),
    ("pav_art", "pav_art_meta", "art"),
]


def render_dock(page: str) -> None:
    """Floating bar: home / map / AR, plus the separate account button."""
    with st.container(key="dock"):
        with st.container(key="dock_bar"):
            for key, icon, label in (("home", ":material/home:", t("nav_home")),
                                     ("map", ":material/map:", t("nav_map")),
                                     ("ar", ":material/view_in_ar:", t("nav_ar"))):
                st.button(label, key=f"dock_{key}", icon=icon, on_click=go, args=(key,),
                          type="primary" if ("home" if page == "pavilion" else page) == key else "secondary")
        st.button(t("nav_account"), key="dock_account", icon=":material/person:", on_click=go,
                  args=("account",), type="primary" if page == "account" else "secondary")


def open_pavilion(name: str) -> None:
    st.session_state.pavilion = name
    st.session_state.page = "pavilion"


def render_pavilion() -> None:
    name = st.session_state.get("pavilion", "innovation")
    if name not in ("innovation", "art"):
        name = "innovation"
    title, meta, img = next(w for w in WINGS if w[2] == name)

    # open the page at the top (Streamlit keeps the scroll position of the previous page)
    import streamlit.components.v1 as components
    components.html(
        "<script>const m=window.parent.document.querySelector('[data-testid=\"stMain\"]');"
        "if(m){m.scrollTo(0,0);} window.parent.scrollTo(0,0);</script>", height=0)

    with st.container(key="pavilion_card"):
        back_col, logo_col, _end = st.columns([1, 3, 1], vertical_alignment="center")
        with back_col:
            st.button(back_arrow(), key="back_btn", on_click=go, args=("home",))
        with logo_col:
            st.markdown(logo_html(), unsafe_allow_html=True)
        st.markdown(
            f'<h1 class="pavilion__title">{t(title)}</h1><p class="pavilion__meta">{t(meta)}</p>'
            f'<h2 class="pavilion__h">{t("pav_about_title")}</h2>'
            f'<p class="pavilion__about">{t(f"pav_{name}_about")}</p>'
            f'<h2 class="pavilion__h">{t("pav_highlights")}</h2>'
            '<ul class="pavilion__list">'
            + "".join(f'<li>{t(f"pav_{name}_h{i}")}</li>' for i in (1, 2, 3)) + "</ul>",
            unsafe_allow_html=True)
        map_col, ar_col = st.columns(2, gap="small")
        with map_col:
            st.button(t("pav_show_map"), key="pav_map", on_click=go, args=("map",), use_container_width=True)
        with ar_col:
            st.button(t("pav_open_ar"), key="pav_ar", type="primary", on_click=go, args=("ar",),
                      use_container_width=True)


def render_home() -> None:
    top_row("logo")
    name = current_name()
    greeting = t("greet_name", name=html.escape(name)) if name else t("greet_guest")
    st.markdown(f'<h1 class="home-title">{greeting}</h1><p class="home-sub">{t("home_sub")}</p>',
                unsafe_allow_html=True)
    query = st.text_input("search", key="search", placeholder=t("search_ph"), label_visibility="collapsed")

    with st.container(key="ar_banner"):
        text_col, img_col = st.columns([1.1, 1], gap="small")
        with text_col:
            st.markdown(f'<h2 class="ar-banner__title">{t("ar_banner_title")}</h2>'
                        f'<p class="ar-banner__desc">{t("ar_banner_text")}</p>', unsafe_allow_html=True)
            st.button(f'{t("choose_destination_btn")} {forward_arrow()}', key="ar_cta",
                      on_click=go, args=("ar",))
        with img_col:
            st.markdown('<div class="ar-banner__img"></div>', unsafe_allow_html=True)

    head_col, link_col = st.columns([3, 1], vertical_alignment="center")
    with head_col:
        st.markdown(f'<h2 class="section-head__title">{t("explore_pavilions")}</h2>', unsafe_allow_html=True)
    with link_col:
        st.button(f'{t("view_all")} ›' if is_rtl() else f'{t("view_all")} ›', key="view_all",
                  on_click=go, args=("map",))

    q = query.strip().lower()
    shown = [w for w in WINGS if not q or q in t(w[0]).lower() or q in t(w[1]).lower()]
    if not shown:
        st.markdown(f'<p class="empty">{t("no_results")}</p>', unsafe_allow_html=True)
    else:
        cols = st.columns(2, gap="large")
        for col, (title, meta, img) in zip(cols, shown):
            with col, st.container(key=f"wing_{img}"):
                st.markdown(
                    f'<div class="wing-card__img wing-card__img--{img}"></div>'
                    f'<h3 class="wing-card__title">{t(title)}</h3><p class="wing-card__meta">{t(meta)}</p>',
                    unsafe_allow_html=True)
                st.button(f'{t("discover_experience")} ‹' if is_rtl() else f'{t("discover_experience")} ›',
                          key=f"wing_btn_{img}", type="primary", on_click=open_pavilion, args=(img,))

    with st.container(key="assistant"):
        st.button(t("open_assistant"), key="orb", on_click=go, args=("chat",))
        st.markdown(f'<div class="assistant__bubble">{t("assistant_bubble")}</div>', unsafe_allow_html=True)


# ======================================================================
# 5. Chat (logic from ai.py)
# ======================================================================
def load_avatar():
    own = BASE / "assets" / "exora.jpg"
    return Image.open(own if own.exists() else IMG / "assistant-orb.jpg")


def send_suggestion(text: str) -> None:
    st.session_state.pending_prompt = text


def clear_chat_history() -> None:
    st.session_state.messages = []


def render_chat() -> None:
    from classes.chatbot import get_response

    assistant_avatar = load_avatar()
    pending = st.session_state.pop("pending_prompt", None)

    top_row("back", "home")
    with st.container(key="chat_head"):
        title_col, menu_col = st.columns([5, 1], vertical_alignment="center")
        with title_col:
            st.markdown(f'<div class="chat-title"><span class="chat-title__orb"></span>'
                        f'<h1>{t("chat_assistant")}</h1></div>', unsafe_allow_html=True)
        with menu_col:
            with st.container(key="chat_menu"):
                with st.popover("", icon=":material/more_horiz:"):
                    st.button(t("chat_menu_clear"), key="clear_chat", on_click=clear_chat_history)
    st.markdown(f'<p class="chat-tagline">{t("chat_tagline")}</p>', unsafe_allow_html=True)

    if not st.session_state.messages and not pending:
        st.markdown(
            '<div class="chat-welcome"><span class="chat-welcome__orb"></span><div class="chat-welcome__bubble">'
            f'<strong>{t("chat_hello1")}</strong><p>{t("chat_hello2")}</p></div></div>'
            f'<p class="chat-how">{t("chat_how")}</p>', unsafe_allow_html=True)
        with st.container(key="chat_sugg"):
            chevron = ":material/chevron_left:" if is_rtl() else ":material/chevron_right:"
            for i in (1, 2, 3, 4):
                st.button(t(f"chat_s{i}"), key=f"sugg_{i}", icon=chevron,
                          on_click=send_suggestion, args=(t(f"chat_s{i}"),))

    for message in st.session_state.messages:
        avatar = assistant_avatar if message["role"] == "assistant" else "user"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    typed = st.chat_input(t("chat_input"))
    user_input = pending or typed
    if user_input:
        with st.chat_message("user", avatar="user"):
            st.markdown(user_input)

        history = st.session_state.messages.copy()
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("assistant", avatar=assistant_avatar):
            with st.spinner(t("chat_thinking")):
                try:
                    answer = get_response(user_input, history)
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(t("chat_error"))
                    st.caption(f'{t("chat_error_details")}: {e}')


# ======================================================================
# 6. Map (logic from map.py)
# ======================================================================
def _is_phone() -> bool:
    import re
    try:
        ua = st.context.headers.get("User-Agent", "")
    except Exception:
        return False
    return bool(re.search(r"iPhone|iPod|Android.*Mobile|Mobile", ua)) and "iPad" not in ua


_PHONE_LABELS = {
    "SAUDI ARABIA PAVILION": "SAUDI", "JAPAN PAVILION": "JAPAN", "FRANCE PAVILION": "FRANCE",
    "MAIN ENTRANCE": "ENTRY", "MAIN EXIT": "EXIT", "ENTRANCE": "IN", "EXIT": "OUT",
    "Information Desk": "Info", "Restroom": "WC", "Water Station": "Water", "First Aid": "Aid",
    "DESTINATION": "GOAL", "Low crowd": "Low", "Medium crowd": "Medium", "High crowd": "High",
    "Recommended route": "Route",
}


def _short_label(text: str) -> str:
    import re
    inner = re.sub(r"</?b>", "", text)
    bold = text.startswith("<b>")
    if inner in _PHONE_LABELS:
        out = _PHONE_LABELS[inner]
    else:
        m = re.fullmatch(r"(SAUDI|JAPAN|FRANCE) 0(\d)", inner)
        if m:
            out = m.group(1)[0] + m.group(2)
        elif inner.startswith("Recommended route distance:"):
            out = inner.replace("Recommended route distance:", "Route distance:")
            return "<b>Route distance:</b>" + out.split("Route distance:")[1]
        else:
            return text
    return f"<b>{out}</b>" if bold else out


def _map_chart_for_screen(original):
    """Make the map fit the screen. Done here so classes/MapManager.py stays untouched.
    Laptop: fill the width (no square lock) and use larger text.
    Phone: fit the whole map on the screen using short labels."""
    def chart(fig, *args, **kwargs):
        phone = _is_phone()
        fig.update_layout(yaxis=dict(scaleanchor=None, scaleratio=None))
        for ann in fig.layout.annotations:
            size = (ann.font.size if ann.font and ann.font.size else 10)
            if phone:
                ann.text = _short_label(ann.text or "")
                ann.font.size = max(8, round(size * 0.95))
            else:
                ann.font.size = round(size * 1.3)
        fig.update_layout(height=640 if phone else 760,
                          margin=dict(l=4 if phone else 15, r=4 if phone else 15, t=30, b=10))
        return original(fig, *args, **kwargs)
    return chart


def render_map() -> None:
    try:
        from classes.corridor_crowd import CrowdManager
        from classes.Route_Manager import RouteManager
        from classes.MapManager import MapManager
    except ImportError as e:
        st.error(t("missing_classes", name=str(e)))
        return

    try:
        crowd_manager = CrowdManager()
        route_manager = RouteManager(crowd_manager)
    except FileNotFoundError as e:
        st.error(t("missing_data", name=e.filename or str(e)))
        return
    route_manager.build_graph()
    map_manager = MapManager(crowd_manager, route_manager)

    top_row()
    st.markdown(f'<h1 class="title title--start">{t("map_title")}</h1>', unsafe_allow_html=True)

    scenario = st.selectbox(t("crowd_scenario"), list(crowd_manager.SCENARIOS.keys()))
    crowd_manager.set_crowd_scenario(scenario)

    locations = list(route_manager.graph.nodes)
    start = st.selectbox(t("start_label"), locations)
    destination = st.selectbox(t("destination_label"), [n for n in locations if n != start])

    clicked = st.button(t("find_route_map"), key="map_find", type="primary")
    if not clicked:
        st.markdown(f'<p class="map-hint">{t("map_hint")}</p>', unsafe_allow_html=True)
        return

    route_result = route_manager.find_route(start, destination)
    if not route_result.get("route"):
        st.warning(route_result.get("message", t("no_route")))
        return

    route = route_result["route"]
    crowd_rates = [crowd_manager.get_crowd_rate(route[i], route[i + 1]) for i in range(len(route) - 1)]
    if crowd_rates:
        average_crowd = (sum(crowd_rates) / len(crowd_rates)) * 100
        if average_crowd < 40:
            level, tone = t("crowd_low"), "low"
        elif average_crowd < 75:
            level, tone = t("crowd_medium"), "medium"
        else:
            level, tone = t("crowd_high"), "high"
        st.markdown(
            f'<div class="crowd-card"><p class="crowd-card__label">{t("map_crowd_label")}</p>'
            f'<div class="crowd-card__row"><span class="crowd-card__level crowd-card__level--{tone}">{level}</span>'
            f'<span class="crowd-card__pct"><strong>{round(average_crowd, 1)}%</strong>'
            f'<small>{t("occupancy_rate")}</small></span></div></div>', unsafe_allow_html=True)

    st.markdown(f'<h2 class="map-section">{t("map_section")}</h2>', unsafe_allow_html=True)
    with st.container(key="map_card"):
        _orig_chart = st.plotly_chart
        st.plotly_chart = _map_chart_for_screen(_orig_chart)
        try:
            map_manager.render(route_result=route_result, start=start, destination=destination)
        finally:
            st.plotly_chart = _orig_chart

    lines = [f'<p><strong>{t("recommended_route")}:</strong> ' + " → ".join(route_result["route"]) + "</p>",
             f'<p>{t("route_cost")}: {num(route_result["total_cost"])}</p>']
    if route_result.get("distance") is not None:
        lines.append(f'<p>{t("route_distance")}: {num(route_result["distance"])} {t("meters")}</p>')
    st.markdown('<div class="map-info">' + "".join(lines) + "</div>", unsafe_allow_html=True)


# ======================================================================
# 7. AR navigation (logic from ar.py)
# ======================================================================
def _ar_buttons_on_screen(html_code: str) -> str:
    """Restyle the page of classes/ar_manger.py to the design (done here so the class stays untouched):
    the title, the info card and the status texts are hidden, and the camera screen becomes one dark card
    with icon, title, text and the Start button; the Stop button sits on top of the camera picture."""
    import re
    start = re.search(r'<button id="startButton">(.*?)</button>', html_code, re.S)
    stop = re.search(r'<button id="stopButton"[^>]*>.*?</button>', html_code, re.S)
    if not start or not stop:
        return html_code
    html_code = html_code.replace(start.group(0), "").replace(stop.group(0), "")
    new_start = f'<button id="startButton">{html.escape(t("ar_cam_btn"))}</button>'
    icon = ('<div class="camera-icon"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#fff" '
            'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h3l1.5-2h7L17 8h3a1 '
            '1 0 0 1 1 1v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"/><circle cx="12" cy="13" r="3.5"/></svg></div>')
    html_code = re.sub(r'<div class="camera-icon">.*?</div>', icon, html_code, count=1, flags=re.S)
    html_code = re.sub(r'(<div[^>]*>\s*)Camera is ready(\s*</div>)',
                       lambda m: f'{m.group(1)}<b>{html.escape(t("ar_cam_title"))}</b>{m.group(2)}', html_code, count=1)
    html_code = re.sub(r'Press Start AR Navigation(\s*</div>)',
                       lambda m: f'{html.escape(t("ar_cam_text"))}{m.group(1)}{new_start}', html_code, count=1)
    html_code = html_code.replace(
        '<div class="guidance" id="guidance">', stop.group(0) + '<div class="guidance" id="guidance">', 1)
    css = ("<style>"
           "html,body{background:transparent !important}"
           f"body{{padding:0;direction:{language.get_direction()}}}"
           ".header,.subtitle,.info-card,.state-icon,.state-title,.state-message{display:none !important}"
           ".state-card{background:transparent;border:0;padding:0;margin-top:6px;box-shadow:none}"
           ".status{color:#6b6880;font-size:13px}"
           ".camera-container{height:auto;background:#26244a;border-radius:16px}"
           "video{height:430px}"
           ".placeholder{position:static;inset:auto;padding:22px 18px;gap:8px}"
           ".placeholder b{font-size:18px}"
           ".placeholder button{width:100%;max-width:none;margin:10px 0 0;padding:14px;border-radius:14px;"
           "background:#6f58d9;font-size:15px}"
           ".camera-container .stop-button{position:absolute;top:14px;right:14px;width:auto;margin:0;"
           "z-index:5;padding:10px 18px;background:#6f58d9}"
           "</style></head>")
    return html_code.replace("</head>", css, 1)


def leave_ar_route() -> None:
    for key in ("ar_route", "ar_start", "ar_destination", "ar_total_cost", "ar_camera"):
        st.session_state.pop(key, None)
MAP_NORTH_OFFSET = 0   # معايرة الشمال بالدرجات


def bearing_between(graph, a, b) -> float:
    """Compass bearing (0 = north, clockwise) from node a to node b."""
    lat1 = math.radians(graph.nodes[a]["latitude"])
    lon1 = math.radians(graph.nodes[a]["longitude"])
    lat2 = math.radians(graph.nodes[b]["latitude"])
    lon2 = math.radians(graph.nodes[b]["longitude"])

    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = (math.cos(lat1) * math.sin(lat2)
         - math.sin(lat1) * math.cos(lat2) * math.cos(dlon))
    return (math.degrees(math.atan2(x, y)) + 360) % 360

def render_ar() -> None:
    try:
        from classes.ar_manger import ARManager
        from classes.corridor_crowd import CrowdManager
        from classes.Route_Manager import RouteManager
    except ImportError as e:
        st.error(t("missing_classes", name=str(e)))
        return

    try:
        crowd_manager = CrowdManager()
        route_manager = RouteManager(crowd_manager)
    except FileNotFoundError as e:
        st.error(t("missing_data", name=e.filename or str(e)))
        return

    if route_manager.graph.number_of_nodes() == 0:
        route_manager.build_graph()
    if route_manager.graph.number_of_nodes() == 0:
        st.error(t("no_locations"))
        return

    graph = route_manager.graph
    location_ids = list(graph.nodes)
    name_of = lambda i: graph.nodes[i]["name"]  # noqa: E731

    # ---------------- screen 1: choose start + destination ----------------
    if "ar_route" not in st.session_state:
        top_row()
        st.markdown(f'<h1 class="title title--start">{t("ar_page_title")}</h1>'
                    f'<p class="subtitle subtitle--start">{t("ar_page_sub")}</p>', unsafe_allow_html=True)
        
        current_location = st.query_params.get("at")
        with st.container(key="ar_form"):
            start = st.selectbox(t("ar_start_label"), location_ids, key="ar_start_sel", format_func=name_of,
                                 index=location_ids.index(current_location) if current_location in location_ids else None,
                                 placeholder=t("ar_start_ph"))
            goal = st.selectbox(t("destination_label"), [i for i in location_ids if i != start],
                                key="ar_goal_sel", format_func=name_of, index=None, placeholder=t("ar_goal_ph"))
            clicked = st.button(t("find_route"), key="ar_find", type="primary",
                                disabled=start is None or goal is None)
        if clicked:
            result = route_manager.find_route(start, goal)
            if not result.get("route"):
                st.error(result.get("message", t("no_route")))
            else:
                st.session_state["ar_route"] = result["route"]
                st.session_state["ar_total_cost"] = result.get("total_cost")
                st.session_state["ar_destination"] = goal
                st.session_state["ar_start"] = start
                st.rerun()
        return

    # ---------------- screen 2: route found ----------------
    path = st.session_state["ar_route"]
    start, goal = st.session_state["ar_start"], st.session_state["ar_destination"]

    top_row("back", on_click=leave_ar_route, args=())
    st.markdown(f'<h1 class="title title--start">{t("ar_route_title")}</h1>', unsafe_allow_html=True)

    route_distance = 0.0
    for i in range(len(path) - 1):
        edge = graph[path[i]][path[i + 1]]
        route_distance += float(edge.get("distance", edge.get("distance_m", 0)))

    with st.container(key="ar_route_card"):
        st.markdown(
            f'<p class="ar-found">✓ {t("ar_found")}</p>'
            f'<p class="ar-lbl">{t("ar_start_label")}</p><p class="ar-val">{html.escape(str(name_of(start)))}</p>'
            f'<p class="ar-lbl">{t("destination_label")}</p><p class="ar-val">{html.escape(str(name_of(goal)))}</p>'
            f'<p class="ar-total">{t("ar_total", d=num(route_distance))}</p>', unsafe_allow_html=True)
        with st.expander(t("ar_details")):
            st.write(" → ".join(name_of(i) for i in path))
            cost = st.session_state.get("ar_total_cost")
            if cost is not None:
                st.caption(f'{t("total_route_cost")}: {num(cost)}')

    if len(path) <= 1:
        st.success(t("arrived"))
        return

    next_id = path[1]
    edge = graph[path[0]][next_id]
    next_distance = edge.get("distance", edge.get("distance_m", 0))

    import streamlit.components.v1 as components
    _orig_html = components.html
    components.html = lambda h, **kw: _orig_html(_ar_buttons_on_screen(h), **kw)
    try:
        ARManager().camera_view(
            target_bearing=bearing_between(graph, path[0], next_id),
            next_name=graph.nodes[next_id]["name"],
            next_distance=next_distance,
            destination=graph.nodes[goal]["name"],
            north_offset=MAP_NORTH_OFFSET,
        )
    finally:
        components.html = _orig_html


# ======================================================================
# 8. Account (logic from account.py)
# ======================================================================
# ======================================================================
# 8. Account (new design) -> replaces logout_callback + render_account in streamapp.py
#    Everything is in this one block: no change to exora.css is needed.
# ======================================================================

_ACC_TEXTS = {
    "ar": {"acc_language": "اللغة", "acc_edit_name": "تعديل الاسم",
           "acc_save": "حفظ", "acc_name_saved": "تم تحديث الاسم"},
    "en": {"acc_language": "Language", "acc_edit_name": "Edit name",
           "acc_save": "Save", "acc_name_saved": "Name updated"},
    "fr": {"acc_language": "Langue", "acc_edit_name": "Modifier le nom",
           "acc_save": "Enregistrer", "acc_name_saved": "Nom mis à jour"},
}
for _lang, _texts in _ACC_TEXTS.items():
    for _k, _v in _texts.items():
        EXTRA.setdefault(_lang, {}).setdefault(_k, _v)

AVATAR_SVG = (
    '<svg width="46" height="46" viewBox="0 0 24 24" fill="none" stroke="#6f58d9" stroke-width="1.7" '
    'stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/>'
    '<path d="M4 20c0-4 3.6-6 8-6s8 2 8 6"/></svg>'
)

ACCOUNT_CSS = """
<style>
.acc2-avatar{width:92px;height:92px;margin:6px auto 10px;border-radius:50%;background:#ebe5fb;
  border:2px solid #ddd3f7;display:flex;align-items:center;justify-content:center}
.st-key-acc2_name{flex-direction:row !important;justify-content:center;align-items:center;
  gap:4px !important;margin-bottom:14px}
.st-key-acc2_name > div{width:auto !important}
.acc2-name{font-size:18px;font-weight:800;color:#1a1535}
.st-key-acc2_name button{background:transparent !important;border:0 !important;box-shadow:none !important;
  color:#6f58d9 !important;min-height:0 !important;padding:4px !important}
.st-key-acc2_info{background:#fff;border:1px solid #ebe8f3;border-radius:20px;padding:16px 18px;
  box-shadow:0 6px 20px rgba(111,88,217,.08);margin-bottom:8px}
.acc2-card-title{font-size:16px;font-weight:800;color:#1a1535;margin:0 0 8px;padding:0}
.acc2-row{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:14px 0;
  border-top:1px solid #efedf5;font-size:14px}
.acc2-row span{color:#1a1535;font-weight:700;font-size:13px}
.acc2-row b{color:#6b6880;font-weight:500;overflow-wrap:anywhere}
.acc2-h{font-size:16px;font-weight:800;color:#1a1535;margin:18px 0 8px;padding:0}
.st-key-acc2_settings{background:#fff;border:1px solid #ebe8f3;border-radius:20px;padding:4px 10px;
  box-shadow:0 6px 20px rgba(111,88,217,.08);gap:0 !important}
.st-key-acc2_settings [data-testid="stPopover"]{width:100%}
.st-key-acc2_settings [data-testid="stPopover"] > div{width:100%}
.st-key-acc2_settings button{width:100%;background:transparent !important;border:0 !important;
  box-shadow:none !important;color:#1a1535 !important;font-weight:700;justify-content:space-between;
  padding:16px 6px !important;min-height:0 !important}
.st-key-acc2_settings [data-testid="stPopover"]:not(:last-child) button{
  border-bottom:1px solid #efedf5 !important;border-radius:0 !important}
.st-key-acc2_settings button svg{color:#6f58d9}
.st-key-logout_btn{display:flex;justify-content:center;margin-top:22px}
.st-key-logout_btn button{background:transparent !important;border:0 !important;box-shadow:none !important;
  color:#6b6880 !important;font-weight:600}
</style>
"""


def logout_callback() -> None:
    st.session_state.logged_in = False
    st.session_state.current_user = None
    flash(t("logged_out"))
    st.session_state.page = "login"


def save_name() -> None:
    new_name = st.session_state.get("acc_name_input", "").strip()
    username = st.session_state.current_user
    if new_name and username:
        st.session_state.auth.users[username]["name"] = new_name
        flash(t("acc_name_saved"))


def render_account() -> None:
    st.markdown(ACCOUNT_CSS, unsafe_allow_html=True)

    with st.container(key="account_card"):
        with st.container(key="top_row"):
            title_col, lang_col = st.columns(2, vertical_alignment="center")
            with title_col:
                st.markdown(f'<h1 class="title title--start">{t("account")}</h1>', unsafe_allow_html=True)
            with lang_col:
                language_pill()

        current_lang_name = next(k for k, v in LANGUAGES.items()
                                 if v == st.session_state.language).split(" ")[0]

        # ---------------- guest ----------------
        if not st.session_state.logged_in:
            st.markdown(f'<div class="acc2-avatar">{AVATAR_SVG}</div>', unsafe_allow_html=True)
            st.warning(t("login_required"))
            st.button(t("login"), key="account_login", type="primary", on_click=go, args=("login",))
            st.markdown(f'<h2 class="acc2-h">{t("settings")}</h2>', unsafe_allow_html=True)
            with st.container(key="acc2_settings"):
                with st.popover(f'{t("acc_language")}  ·  {current_lang_name}', icon=":material/language:"):
                    language_selector("account_language")
            return

        username = st.session_state.current_user
        user = st.session_state.auth.users[username]
        display_name = user.get("name", username)

        # ---------------- avatar + name (+ edit) ----------------
        st.markdown(f'<div class="acc2-avatar">{AVATAR_SVG}</div>', unsafe_allow_html=True)
        with st.container(key="acc2_name"):
            st.markdown(f'<span class="acc2-name" dir="auto">{html.escape(str(display_name))}</span>',
                        unsafe_allow_html=True)
            with st.popover("", icon=":material/edit:"):
                st.text_input(t("acc_edit_name"), value=display_name, key="acc_name_input")
                st.button(t("acc_save"), key="acc_name_save", type="primary", on_click=save_name)

        # ---------------- account information card ----------------
        with st.container(key="acc2_info"):
            st.markdown(
                f'<h2 class="acc2-card-title">{t("account_information")}</h2>'
                f'<div class="acc2-row"><span>{t("username")}</span>'
                f'<b dir="auto">{html.escape(str(user["username"]))}</b></div>'
                f'<div class="acc2-row"><span>{t("email")}</span>'
                f'<b dir="ltr">{html.escape(str(user["email"]))}</b></div>',
                unsafe_allow_html=True)

        # ---------------- settings card ----------------
        st.markdown(f'<h2 class="acc2-h">{t("settings")}</h2>', unsafe_allow_html=True)
        with st.container(key="acc2_settings"):
            with st.popover(f'{t("acc_language")}  ·  {current_lang_name}', icon=":material/language:"):
                language_selector("account_language")

            with st.popover(t("change_password"), icon=":material/lock:"):
                old_password = st.text_input(t("current_password"), type="password", key="old_password")
                new_password = st.text_input(t("new_password"), type="password", key="new_password",
                                             placeholder=t("password_hint"))
                if st.button(t("update_password"), key="update_pw", type="primary"):
                    if not st.session_state.auth.login(username, old_password):
                        st.error(t("incorrect_current_password"))
                    elif len(new_password) < 8:
                        st.error(t("password_length"))
                    else:
                        user["password"] = new_password
                        st.success(t("password_updated"))

        # ---------------- logout ----------------
        st.button(t("logout"), key="logout_btn", on_click=logout_callback)

# ======================================================================
# Router
# ======================================================================
page = st.session_state.page
inject_css(page)

message = st.session_state.pop("flash", None)
if message:
    st.toast(message)

# The floating bar is fixed on screen, so it is drawn first: if a page calls
# st.stop()/st.rerun() the bar is still there.
if page in DOCK_PAGES:
    render_dock(page)

if page == "splash":
    with st.container(key="splash_page"):
        render_splash()
elif page in ONBOARDING:
    with st.container(key="onb_page"):
        render_onboarding(page)
elif page == "welcome":
    render_welcome()
elif page == "login":
    render_login()
elif page == "signup":
    render_signup()
elif page == "verify_email":
    render_verify_email()
elif page == "account_created":
    render_account_created()
elif page == "forgot":
    render_forgot()
elif page == "reset_code":
    render_reset_code()
elif page == "reset_new":
    render_reset_new()
elif page == "reset_done":
    render_reset_done()
elif page == "home":
    render_home()
elif page == "pavilion":
    render_pavilion()
elif page == "chat":
    render_chat()
elif page == "map":
    render_map()
elif page == "ar":
    render_ar()
elif page == "account":
    render_account()
else:
    st.session_state.page = "splash"
    st.rerun()