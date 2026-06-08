"""
WriterFlow v4 — Design mobile-first inspirado no mockup.
Tema claro, bottom navigation bar, header com logo.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import init_db
from pages import (
    should_show_onboarding, page_onboarding,
    page_dashboard, page_library, page_chapters, page_kindle,
    page_characters, page_world, page_brain_dump, page_export,
)

st.set_page_config(
    page_title="WriterFlow",
    page_icon="🪶",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_db()

# ── CSS Global — Tema claro mobile-first ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* ── Fundo geral: branco/cinza claro ── */
.main { background: #f5f4fb !important; }
.block-container {
    padding: 0 0 80px 0 !important;
    max-width: 480px !important;
    margin: 0 auto !important;
}

/* ── Esconder chrome do Streamlit ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stSidebarNav"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"] { display: none !important; }

/* ── Sidebar: escondida por padrão no mobile ── */
[data-testid="stSidebar"] { display: none !important; }

/* ── Botões padrão ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.2rem !important;
    transition: all .2s !important;
    box-shadow: 0 4px 14px rgba(124,58,237,.25) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(124,58,237,.35) !important;
}

/* ── Botão secundário ── */
.stButton > button[kind="secondary"] {
    background: #fff !important;
    color: #7c3aed !important;
    border: 1.5px solid #e9d5ff !important;
    box-shadow: none !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: #fff !important;
    border: 1.5px solid #e9d5ff !important;
    border-radius: 12px !important;
    color: #1e1b2e !important;
    font-size: 0.9rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,.12) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #f0ebff !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #9ca3af !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
}
.stTabs [aria-selected="true"] {
    background: #fff !important;
    color: #7c3aed !important;
    box-shadow: 0 2px 8px rgba(124,58,237,.15) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #fff !important;
    border-radius: 12px !important;
    color: #1e1b2e !important;
    border: 1.5px solid #f0ebff !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #f5f4fb; }
::-webkit-scrollbar-thumb { background: #c4b5fd; border-radius: 4px; }

/* ── Métricas ── */
[data-testid="metric-container"] {
    background: #fff !important;
    border: 1.5px solid #f0ebff !important;
    border-radius: 16px !important;
    padding: 1rem !important;
}

/* ── Bottom Nav Bar ── */
.wf-bottom-nav {
    position: fixed;
    bottom: 0; left: 50%;
    transform: translateX(-50%);
    width: 100%; max-width: 480px;
    background: #fff;
    border-top: 1px solid #f0ebff;
    display: flex;
    align-items: center;
    justify-content: space-around;
    padding: 8px 0 12px;
    z-index: 9999;
    box-shadow: 0 -4px 24px rgba(124,58,237,.08);
}
.wf-nav-item {
    display: flex; flex-direction: column;
    align-items: center; gap: 2px;
    cursor: pointer; padding: 4px 12px;
    border-radius: 12px; transition: all .15s;
    text-decoration: none;
    border: none; background: none;
    -webkit-tap-highlight-color: transparent;
}
.wf-nav-item span.icon { font-size: 1.4rem; line-height: 1; }
.wf-nav-item span.label {
    font-size: 0.65rem; font-weight: 500;
    color: #9ca3af; letter-spacing: 0.01em;
}
.wf-nav-item.active span.label { color: #7c3aed; }
.wf-nav-item.active span.icon { filter: none; }

/* ── App Header ── */
.wf-header {
    background: #fff;
    padding: 14px 20px 12px;
    display: flex; align-items: center;
    justify-content: space-between;
    position: sticky; top: 0; z-index: 100;
    border-bottom: 1px solid #f5f0ff;
    box-shadow: 0 2px 12px rgba(124,58,237,.06);
}
.wf-logo {
    display: flex; align-items: center; gap: 8px;
    font-size: 1.25rem; font-weight: 700; color: #7c3aed;
}
.wf-header-icons { display: flex; gap: 12px; align-items: center; }
.wf-icon-btn {
    width: 36px; height: 36px; border-radius: 50%;
    background: #f5f0ff; display: flex;
    align-items: center; justify-content: center;
    font-size: 1rem; cursor: pointer; border: none;
}
.wf-menu-btn {
    width: 36px; height: 36px; border-radius: 10px;
    background: #f5f0ff; display: flex;
    align-items: center; justify-content: center;
    font-size: 1rem; cursor: pointer; border: none;
}

/* ── Cards gerais ── */
.wf-card {
    background: #fff;
    border-radius: 20px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 2px 12px rgba(124,58,237,.07);
    border: 1px solid #f5f0ff;
}

/* ── Stat icons ── */
.wf-stat-icon {
    width: 44px; height: 44px; border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; margin: 0 auto 6px;
}

/* ── Progresso ── */
.wf-prog-rail {
    background: #f0ebff; border-radius: 99px; height: 8px; overflow: hidden;
}
.wf-prog-fill {
    height: 8px; border-radius: 99px;
    transition: width .6s cubic-bezier(.4,0,.2,1);
}

/* ── Quick action ── */
.wf-quick {
    display: flex; flex-direction: column; align-items: center; gap: 6px;
    cursor: pointer;
}
.wf-quick-icon {
    width: 56px; height: 56px; border-radius: 18px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem;
}
.wf-quick-label { font-size: 0.72rem; font-weight: 500; color: #4b5563; text-align: center; }

/* ── Seção title ── */
.wf-section-title {
    font-size: 1rem; font-weight: 700; color: #1e1b2e;
    margin: 0; padding: 0;
}
.wf-see-all {
    font-size: 0.82rem; font-weight: 600; color: #7c3aed;
    cursor: pointer; white-space: nowrap;
}
</style>
""", unsafe_allow_html=True)

# ── Navegação ─────────────────────────────────────────────────────────────────
PAGES = {
    "dashboard":    ("🏠", "Dashboard",    page_dashboard),
    "library":      ("📚", "Biblioteca",   page_library),
    "chapters":     ("✏️", "Capítulos",    page_chapters),
    "characters":   ("👥", "Personagens",  page_characters),
    "more":         ("···", "Mais",        None),  # opens sub-menu
}
# Páginas extras acessíveis pelo "Mais"
EXTRA_PAGES = {
    "kindle":       ("📖", "Modo Kindle",  page_kindle),
    "world":        ("🌍", "World Building", page_world),
    "brain_dump":   ("🧠", "Brain Dump",   page_brain_dump),
    "export":       ("📤", "Exportar",     page_export),
}
ALL_PAGES = {**{k:(i,l,f) for k,(i,l,f) in PAGES.items() if f}, **EXTRA_PAGES}

# ── Onboarding gate ───────────────────────────────────────────────────────────
if should_show_onboarding():
    page_onboarding()
    st.stop()

# ── Estado de navegação ───────────────────────────────────────────────────────
current = st.session_state.get("current_page", "dashboard")
if current not in ALL_PAGES:
    current = "dashboard"

# Clear kindle/focus flags when not on those pages
if current != "kindle":
    st.session_state.pop("kindle_active", None)
if current != "chapters":
    st.session_state.pop("focus_mode", None)

# ── App Header ────────────────────────────────────────────────────────────────
# Hidden on Kindle (full-screen) and focus mode
show_header = not (current == "kindle" or st.session_state.get("focus_mode"))

if show_header:
    st.markdown("""
    <div class="wf-header">
        <div class="wf-logo">
            <span>🪶</span>
            <span>Writer<span style="color:#a855f7">Flow</span></span>
        </div>
        <div class="wf-header-icons">
            <button class="wf-icon-btn" title="Buscar">🔍</button>
            <button class="wf-icon-btn" title="Notificações">🔔</button>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Render page ───────────────────────────────────────────────────────────────
_, _, renderer = ALL_PAGES[current]
renderer()

# ── Bottom Nav Bar ────────────────────────────────────────────────────────────
show_nav = not (current == "kindle" or st.session_state.get("focus_mode"))

if show_nav:
    # Nav items
    NAV_ITEMS = [
        ("dashboard",   "🏠", "Dashboard"),
        ("library",     "📚", "Biblioteca"),
        ("chapters",    "✏️", "Capítulos"),
        ("characters",  "👥", "Personagens"),
        ("more",        "···", "Mais"),
    ]

    # Render nav buttons using columns (Streamlit-native, works on all devices)
    st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

    # Fixed bottom nav via HTML + hidden Streamlit buttons
    nav_html = '<div class="wf-bottom-nav">'
    for key, icon, label in NAV_ITEMS:
        is_active = (key == current) or (key == "more" and current in EXTRA_PAGES)
        active_cls = "active" if is_active else ""
        color = "color:#7c3aed;" if is_active else ""
        nav_html += f"""
        <div class="wf-nav-item {active_cls}" onclick="
            window.parent.document.querySelectorAll('button').forEach(b=>{{
                if(b.textContent.trim()==='NAV_{key.upper()}') b.click();
            }});">
            <span class="icon" style="{color}">{icon}</span>
            <span class="label" style="{color}">{label}</span>
        </div>"""
    nav_html += '</div>'
    st.markdown(nav_html, unsafe_allow_html=True)

    # Hidden Streamlit buttons that JS calls
    cols = st.columns(len(NAV_ITEMS))
    for i, (key, icon, label) in enumerate(NAV_ITEMS):
        with cols[i]:
            if st.button(f"NAV_{key.upper()}", key=f"navbtn_{key}", label_visibility="collapsed"):
                if key == "more":
                    st.session_state["show_more_menu"] = not st.session_state.get("show_more_menu", False)
                else:
                    st.session_state["current_page"] = key
                    st.session_state.pop("show_more_menu", None)
                st.rerun()

    # "Mais" sub-menu
    if st.session_state.get("show_more_menu"):
        st.markdown("""
        <div style="position:fixed;bottom:72px;left:50%;transform:translateX(-50%);
                    width:calc(100% - 32px);max-width:448px;
                    background:#fff;border-radius:20px 20px 0 0;
                    box-shadow:0 -8px 32px rgba(124,58,237,.15);
                    border:1px solid #f0ebff;padding:1rem;z-index:9998">
            <div style="text-align:center;margin-bottom:0.75rem">
                <div style="width:36px;height:4px;background:#e9d5ff;border-radius:2px;margin:0 auto"></div>
            </div>
            <div style="font-weight:700;color:#1e1b2e;font-size:0.9rem;margin-bottom:0.75rem;padding:0 0.25rem">Mais opções</div>
        </div>
        """, unsafe_allow_html=True)
        extra_cols = st.columns(2)
        extra_items = list(EXTRA_PAGES.items())
        for i, (key, (icon, label, _)) in enumerate(extra_items):
            with extra_cols[i % 2]:
                if st.button(f"{icon} {label}", key=f"extra_{key}", use_container_width=True):
                    st.session_state["current_page"] = key
                    st.session_state.pop("show_more_menu", None)
                    st.rerun()
