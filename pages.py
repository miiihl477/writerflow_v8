"""
WriterFlow — Todas as páginas v3.1
Melhorias: streak, heatmap, quote diária, tempo de leitura, metas por capítulo,
marcadores de cena, filtro de personagens por papel, pin em brain dump,
bookmarks no Kindle, ordenação da biblioteca, estatísticas avançadas.
"""
import streamlit as st
import markdown2
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta, date
from core import (
    book_create, book_update, book_touch,
    book_soft_delete, book_restore, book_hard_delete,
    book_get, book_list, book_list_lw, book_list_deleted, book_genres,
    book_recalc_wc, book_stats,
    ch_create, ch_get, ch_list, ch_list_lw, ch_list_deleted,
    ch_get_wc, ch_save, ch_update, ch_reorder, ch_stats_for_book,
    ch_soft_delete, ch_restore, ch_hard_delete,
    char_create, char_list, char_get, char_update, char_soft_delete,
    char_search, char_roles,
    loc_create, loc_list, loc_update, loc_soft_delete, loc_search,
    fac_create, fac_list, fac_update, fac_soft_delete,
    ev_create, ev_list, ev_update, ev_soft_delete,
    bd_create, bd_list, bd_update, bd_soft_delete, bd_tags, bd_toggle_pin,
    goal_save, goal_active, sess_log, sess_today, sess_month, sess_30days,
    sess_heatmap, sess_best_day, sess_total_minutes,
    setting_get, setting_set, kindle_pos_get, kindle_pos_save,
    bookmark_add, bookmark_list, bookmark_delete,
    img_process, img_b64, count_words, reading_time, writing_time,
    export_pdf, export_docx, export_epub, daily_quote,
)

GENRES   = ["Ficção Científica","Fantasia","Romance","Thriller","Terror","Mistério",
            "Aventura","Drama","Histórico","Autobiografia","Não-ficção","Poesia",
            "Conto","Infantil","Jovem Adulto","Outro"]
STATUSES = ["Planejamento","Escrita","Revisão","Publicado"]
STATUS_COLOR = {"Planejamento":"#6366f1","Escrita":"#06b6d4","Revisão":"#f59e0b","Publicado":"#10b981"}
STATUS_ICON  = {"Planejamento":"📋","Escrita":"✍️","Revisão":"🔍","Publicado":"✅"}
ROLES = ["Protagonista","Antagonista","Coadjuvante","Mentor","Comic Relief",
         "Interesse Romântico","Vilão","Aliado","Neutro","Outro"]

def badge(status):
    c = STATUS_COLOR.get(status, "#64748b"); icon = STATUS_ICON.get(status, "")
    return (f'<span style="background:{c}18;color:{c};border:1px solid {c}44;'
            f'padding:3px 10px;border-radius:20px;font-size:0.72rem;font-weight:600">'
            f'{icon} {status}</span>')

def hdr(title, sub=""):
    st.markdown(
        f'<div style="font-size:1.4rem;font-weight:700;color:#1e1b2e;'
        f'margin:1rem 0 0.1rem;padding:0 0.25rem">{title}</div>',
        unsafe_allow_html=True)
    if sub:
        st.markdown(
            f'<div style="color:#9ca3af;font-size:0.85rem;margin-bottom:1rem;'
            f'padding:0 0.25rem">{sub}</div>',
            unsafe_allow_html=True)

def card_wrap(content_html, padding="1rem"):
    return (f'<div style="background:#fff;border-radius:16px;padding:{padding};'
            f'margin-bottom:0.6rem;box-shadow:0 2px 10px rgba(124,58,237,.06);'
            f'border:1px solid #f5f0ff">{content_html}</div>')

def stat_box(value, label, color="#7c3aed", icon=""):
    return (f'<div style="background:#fff;border:1px solid #f5f0ff;border-radius:14px;'
            f'padding:0.85rem;text-align:center;box-shadow:0 2px 8px rgba(124,58,237,.06)">'
            f'<div style="font-size:1.6rem;font-weight:700;color:{color}">{icon} {value}</div>'
            f'<div style="font-size:0.7rem;color:#9ca3af;text-transform:uppercase;'
            f'letter-spacing:0.08em;margin-top:2px">{label}</div></div>')

def progress_bar(pct, color="#7c3aed", label=""):
    p = min(100, max(0, pct))
    bar = (f'<div style="background:#f0ebff;border-radius:99px;height:8px;overflow:hidden;margin-bottom:4px">'
           f'<div style="width:{p}%;height:8px;background:{color};border-radius:99px"></div></div>')
    txt = f'<div style="font-size:0.7rem;color:#9ca3af">{p}%{" · "+label if label else ""}</div>'
    return bar + txt

# ══════════════════════════════════════════════════════
# ONBOARDING
# ══════════════════════════════════════════════════════

def should_show_onboarding():
    if st.session_state.get("onboarding_done"): return False
    return len(book_list_lw()) == 0

def page_onboarding():
    st.markdown("""<div style="background:linear-gradient(135deg,#7c3aed,#a855f7,#6366f1);border-radius:0 0 32px 32px;padding:3rem 2rem 2.5rem;text-align:center;margin-bottom:1.5rem">
        <div style="font-size:3.5rem;margin-bottom:0.75rem">🪶</div>
        <h1 style="font-size:2rem;font-weight:800;color:#fff;margin-bottom:0.5rem">Bem-vinda ao WriterFlow</h1>
        <p style="color:rgba(255,255,255,0.85);font-size:0.95rem;max-width:380px;margin:0 auto">Sua plataforma para organizar, escrever e publicar histórias.</p>
    </div>""", unsafe_allow_html=True)
    feats = [("📚","Biblioteca","Organize livros com capas e status"),("✍️","Editor","Markdown, preview e auto-save"),
             ("📖","Kindle","Leia como num e-reader real"),("👥","Personagens","Fotos, idades e relacionamentos"),
             ("🌍","World Building","Locais, facções e cronologia"),("🧠","Brain Dump","Fixe ideias rapidamente"),
             ("📤","Exportação","PDF, DOCX e EPUB com capa"),("📊","Dashboard","Streak, metas e heatmap")]
    cols = st.columns(4)
    for i,(icon,name,desc) in enumerate(feats):
        with cols[i%4]:
            st.markdown(f'<div style="background:#13131f;border:1px solid #1e1e3f;border-radius:10px;padding:1.1rem;text-align:center;margin-bottom:0.75rem;min-height:120px"><div style="font-size:1.8rem">{icon}</div><div style="color:#7c3aed;font-weight:700;font-size:0.85rem;margin:0.3rem 0">{name}</div><div style="color:#9ca3af;font-size:0.75rem;line-height:1.4">{desc}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1,c2 = st.columns([2,1])
    with c1:
        if st.button("🚀 Criar livro de exemplo e explorar", use_container_width=True, type="primary"):
            _create_sample()
    with c2:
        if st.button("Começar do zero →", use_container_width=True):
            st.session_state["onboarding_done"]=True; st.session_state["current_page"]="📚 Biblioteca"
            st.session_state["show_new_book"]=True; st.rerun()

def _create_sample():
    with st.spinner("Criando livro de exemplo…"):
        bid = book_create("A Floresta dos Espelhos","Elena recebe uma carta assinada por sua avó — que morreu sete anos atrás.","Fantasia","Escrita")
        caps = [
            ("Prólogo — O Chamado","## O Chamado\n\nA carta chegou numa manhã de chuva fina. Elena a leu três vezes.\n\n> *Quando o silêncio falar mais alto que as palavras, siga o rio para o norte.*\n\nAlgumas mensagens não pedem resposta imediata. Pedem que você as deixe fermentar."),
            ("Capítulo 1 — A Floresta","## A Floresta\n\nO rio começava atrás do mercado velho. A floresta era densa, mas não opressiva.\n\n- As sombras se moviam de maneira estranha\n- Os sons chegavam com leve atraso\n- O cheiro era de terra molhada e pedra aquecida\n\n**\"Você demorou\"**, disse o reflexo."),
            ("Capítulo 2 — O Guardião","## O Guardião\n\nO velho estava sentado numa raiz exposta, talhando madeira.\n\n**\"Sabia que você viria\"**, disse ele. **\"A floresta me avisou.\"**\n\nSeus olhos eram de uma cor indefinida — entre cinza e verde."),
        ]
        for i,(title,content) in enumerate(caps):
            cid = ch_create(bid,title); ch_save(cid,content,bid)
            if i==0: ch_update(cid,scene_marker="Abertura")
            if i==2: ch_update(cid,word_goal=800)
        char_create(bid,"Elena","Protagonista","Jovem de 26 anos que recebe carta misteriosa.",notes="Nasceu durante eclipse solar",age="26")
        char_create(bid,"O Guardião","Mentor","Velho que guarda os segredos da floresta.",notes="Pode ter mais de 100 anos",age="?")
        loc_create(bid,"Floresta dos Espelhos","Árvores com casca prateada que refletem versões alternativas dos visitantes.","Norte do mercado velho")
        ev_create(bid,"Chegada da Carta","Elena recebe a carta da avó falecida","Manhã de chuva")
        ev_create(bid,"Entrada na Floresta","Elena segue o mapa até a floresta","Fim de tarde")
        bd_create("Twist: Elena é reencarnação da avó!",bid,"plot-twist,revelação")
        bd_create("A floresta pode ser metáfora da memória familiar.",bid,"worldbuilding,metáfora")
        bd_create("Cena pendente: Elena encontra diário da avó numa árvore espelho.",bid,"cena,pendente")
        goal_save(1000,"daily"); goal_save(30000,"monthly")
        book_touch(bid)
    st.session_state["onboarding_done"]=True; st.session_state["selected_book_id"]=bid
    st.session_state["current_page"]="📚 Biblioteca"; st.rerun()

# ══════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════

def page_dashboard():
    from core import book_list_lw, ch_list_lw, char_list
    import datetime as _dt

    stats        = book_stats()
    words_today  = sess_today()
    daily_data   = sess_30days()
    goals        = goal_active()
    daily_goal   = next((g["target_words"] for g in goals if g["period"]=="daily"), 1000)
    monthly_goal = next((g["target_words"] for g in goals if g["period"]=="monthly"), 30000)
    daily_pct    = min(100, int(words_today / daily_goal * 100)) if daily_goal else 0
    streak       = stats.get("streak", 0)
    quote, author = daily_quote()
    books        = book_list_lw()

    # ── Boas-vindas ──────────────────────────────────────────────────────────
    hour     = _dt.datetime.now().hour
    greeting = "Bom dia" if hour < 12 else ("Boa tarde" if hour < 18 else "Boa noite")
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#7c3aed 0%,#a855f7 60%,#6366f1 100%);
                border-radius:0 0 28px 28px;padding:1.5rem 1.25rem 2rem;
                margin:0 0 1rem;position:relative;overflow:hidden;min-height:110px">
        <div style="position:absolute;right:-10px;top:-10px;font-size:6rem;opacity:0.12">&#128218;</div>
        <div style="font-size:0.8rem;color:rgba(255,255,255,0.7);font-weight:500;margin-bottom:4px">{greeting}!</div>
        <div style="font-size:1.35rem;font-weight:700;color:#fff;margin-bottom:4px">
            Bem-vinda de volta, Escritora! &#10024;</div>
        <div style="font-size:0.85rem;color:rgba(255,255,255,0.8)">
            Aqui est&#225; um resumo do seu universo liter&#225;rio.</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats ────────────────────────────────────────────────────────────────
    all_chars = []
    for b in books:
        all_chars.extend(char_list(b["id"]))

    stat_items = [
        ("&#128214;", "#ede9ff", "#7c3aed", str(stats["total_books"]),    "Livros",       "Em andamento"),
        ("&#9998;",   "#e0f9f4", "#0d9488", str(stats["total_chapters"]), "Cap&#237;tulos", "Escritos"),
        ("&#128101;", "#fce7f3", "#db2777", str(len(all_chars)),          "Personagens",  "Cadastrados"),
        ("&#127919;", "#ede9ff", "#7c3aed", str(stats["total_words"]),   "Palavras",     "Escritas"),
        ("&#128293;", "#fff7ed", "#ea580c", str(streak),                  "Dias",         "Em sequ&#234;ncia"),
    ]
    cols = st.columns(5)
    for i, (icon, bg, color, val, label, sub) in enumerate(stat_items):
        with cols[i]:
            st.markdown(f"""
            <div style="background:#fff;border-radius:16px;padding:0.75rem 0.25rem;
                        text-align:center;box-shadow:0 2px 10px rgba(124,58,237,.07);
                        border:1px solid #f5f0ff;margin-bottom:0.5rem">
                <div style="background:{bg};width:36px;height:36px;border-radius:10px;
                            display:flex;align-items:center;justify-content:center;
                            font-size:1rem;margin:0 auto 4px">{icon}</div>
                <div style="font-size:0.95rem;font-weight:700;color:#1e1b2e;line-height:1">{val}</div>
                <div style="font-size:0.58rem;font-weight:600;color:#374151;margin-top:1px">{label}</div>
                <div style="font-size:0.55rem;color:#9ca3af">{sub}</div>
            </div>""", unsafe_allow_html=True)

    # ── Livro ativo ──────────────────────────────────────────────────────────
    sel_bid     = st.session_state.get("selected_book_id")
    active_book = book_get(sel_bid) if sel_bid else None
    if not active_book and books:
        active_book = book_get(books[0]["id"])

    if active_book:
        bid     = active_book["id"]
        chs     = ch_list_lw(bid)
        last_ch = chs[-1]["title"] if chs else "Nenhum cap&#237;tulo"
        last_n  = len(chs)
        cover_html = ""
        if active_book.get("cover_image"):
            cover_html = (
                '<img src="' + img_b64(active_book["cover_image"]) + '"'
                ' style="position:absolute;right:0;top:0;height:100%;width:110px;'
                'object-fit:cover;border-radius:0 24px 24px 0;opacity:0.3">'
            )
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#5b21b6 0%,#7c3aed 60%,#6366f1 100%);
                    border-radius:24px;padding:1.3rem 1.25rem 1.1rem;
                    margin:0 0 0.75rem;position:relative;overflow:hidden;min-height:150px">
            {cover_html}
            <div style="position:relative;z-index:1">
                <div style="font-size:0.68rem;color:rgba(255,255,255,0.65);font-weight:500;
                            text-transform:uppercase;letter-spacing:0.08em;margin-bottom:3px">Livro atual</div>
                <div style="font-size:1.5rem;font-weight:800;color:#fff;margin-bottom:10px;
                            line-height:1.15">{active_book['title']}</div>
                <div style="font-size:0.68rem;color:rgba(255,255,255,0.65);margin-bottom:2px">Cap&#237;tulo atual</div>
                <div style="font-size:0.88rem;font-weight:600;color:#fff;margin-bottom:10px">
                    {last_n}. {last_ch}</div>
                <div style="font-size:0.68rem;color:rgba(255,255,255,0.65);margin-bottom:5px">
                    Meta di&#225;ria &nbsp; {words_today:,} / {daily_goal:,} palavras</div>
                <div style="background:rgba(255,255,255,0.2);border-radius:99px;height:7px;overflow:hidden">
                    <div style="width:{daily_pct}%;height:7px;
                                background:linear-gradient(90deg,#34d399,#06b6d4);
                                border-radius:99px"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("&#9998; Continuar escrevendo", key="continue_writing", use_container_width=True):
            st.session_state["selected_book_id"] = bid
            st.session_state["current_page"]     = "chapters"
            st.rerun()

    # ── Progresso dos livros ──────────────────────────────────────────────────
    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown('<p style="font-size:1rem;font-weight:700;color:#1e1b2e;margin:0.5rem 0 0.6rem">Progresso dos seus livros</p>', unsafe_allow_html=True)
    with c2:
        if st.button("Ver todos", key="see_all", type="secondary"):
            st.session_state["current_page"] = "library"; st.rerun()

    bar_colors = ["#7c3aed", "#0d9488", "#6366f1", "#db2777", "#ea580c"]
    for i, bk in enumerate(books[:5]):
        pct  = min(100, int(bk.get("word_count", 0) / max(monthly_goal, 1) * 100))
        bc   = bar_colors[i % len(bar_colors)]
        wcs  = f"{bk.get('word_count', 0):,}".replace(",", ".")
        if bk.get("cover_image"):
            cov = '<img src="' + img_b64(bk["cover_image"]) + '" style="width:44px;height:62px;object-fit:cover;border-radius:8px">'
        else:
            cov = f'<div style="width:44px;height:62px;border-radius:8px;background:{bc}22;display:flex;align-items:center;justify-content:center;font-size:1.2rem">&#128214;</div>'
        genre = bk.get("genre", "") or "—"
        st.markdown(f"""
        <div style="background:#fff;border-radius:16px;padding:0.85rem 0.9rem;
                    margin-bottom:0.55rem;box-shadow:0 2px 10px rgba(124,58,237,.05);
                    border:1px solid #f5f0ff;display:flex;align-items:center;gap:0.7rem">
            {cov}
            <div style="flex:1;min-width:0">
                <div style="font-weight:700;color:#1e1b2e;font-size:0.88rem;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{bk['title']}</div>
                <div style="font-size:0.72rem;color:#9ca3af;margin-bottom:5px">{genre}</div>
                <div style="background:#f5f0ff;border-radius:99px;height:6px;overflow:hidden;margin-bottom:3px">
                    <div style="width:{pct}%;height:6px;background:{bc};border-radius:99px"></div>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.7rem">
                    <span style="color:#9ca3af">{wcs} palavras</span>
                    <span style="color:{bc};font-weight:700">{pct}%</span>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Acesso r&#225;pido ────────────────────────────────────────────────────────────
    st.markdown('<p style="font-size:1rem;font-weight:700;color:#1e1b2e;margin:0.75rem 0 0.6rem">Acesso r&#225;pido</p>', unsafe_allow_html=True)
    quick = [
        ("&#9998;",   "#ede9ff", "Novo\nCap&#237;tulo",   "chapters"),
        ("&#128101;", "#e0f9f4", "Novo\nPersonagem",      "characters"),
        ("&#127758;", "#fff7ed", "World\nBuilding",       "world"),
        ("&#129504;", "#fce7f3", "Brain\nDump",           "brain_dump"),
        ("&#128214;", "#ede9ff", "Modo\nKindle",          "kindle"),
    ]
    qcols = st.columns(5)
    for i, (icon, bg, label, target) in enumerate(quick):
        with qcols[i]:
            st.markdown(f"""
            <div style="text-align:center">
                <div style="background:{bg};width:50px;height:50px;border-radius:16px;
                            display:flex;align-items:center;justify-content:center;
                            font-size:1.25rem;margin:0 auto 4px">{icon}</div>
                <div style="font-size:0.6rem;font-weight:500;color:#4b5563;line-height:1.3">{label}</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"QK_{i}", key=f"qk_{target}", label_visibility="collapsed"):
                st.session_state["current_page"] = target; st.rerun()

    # ── Metas ─────────────────────────────────────────────────────────────────
    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)
    st.markdown('<p style="font-size:1rem;font-weight:700;color:#1e1b2e;margin:0.5rem 0 0.6rem">Metas de hoje</p>', unsafe_allow_html=True)
    monthly_pct = min(100, int(sess_month() / monthly_goal * 100)) if monthly_goal else 0
    for label, cur, total, pct, color in [
        ("&#9889; Di&#225;ria", words_today, daily_goal, daily_pct, "#7c3aed"),
        ("&#128197; Mensal",    sess_month(), monthly_goal, monthly_pct, "#0d9488"),
    ]:
        st.markdown(f"""
        <div style="background:#fff;border-radius:16px;padding:0.9rem 1rem;
                    margin-bottom:0.5rem;box-shadow:0 2px 10px rgba(124,58,237,.05);
                    border:1px solid #f5f0ff">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px">
                <span style="font-weight:600;color:#1e1b2e;font-size:0.88rem">{label}</span>
                <span style="color:{color};font-size:0.85rem;font-weight:700">{cur:,}/{total:,}</span>
            </div>
            <div style="background:#f5f0ff;border-radius:99px;height:8px;overflow:hidden;margin-bottom:3px">
                <div style="width:{pct}%;height:8px;background:{color};border-radius:99px"></div>
            </div>
            <div style="font-size:0.7rem;color:#9ca3af">{pct}%</div>
        </div>""", unsafe_allow_html=True)

    with st.expander("&#9881;&#65039; Configurar metas"):
        with st.form("goals_form"):
            nd = st.number_input("Meta diaria (palavras)", value=daily_goal, min_value=100, step=100)
            nm = st.number_input("Meta mensal (palavras)", value=monthly_goal, min_value=1000, step=1000)
            if st.form_submit_button("Salvar"):
                goal_save(nd, "daily"); goal_save(nm, "monthly"); st.rerun()

    with st.expander("&#43; Registrar sessao de escrita"):
        with st.form("sess_form"):
            w = st.number_input("Palavras escritas", min_value=0, step=50)
            m = st.number_input("Minutos escrevendo", min_value=0, step=5)
            if st.form_submit_button("Registrar") and w > 0:
                sess_log(w, minutes=m); st.rerun()

    # ── Quote ─────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#ede9ff,#fce7f3);border-radius:16px;
                padding:1rem 1.1rem;margin:0.5rem 0 1rem;border:1px solid #e9d5ff">
        <div style="font-size:0.72rem;color:#7c3aed;font-weight:600;margin-bottom:3px">&#128156; Cita&#231;&#227;o do dia</div>
        <div style="font-style:italic;color:#374151;font-size:0.83rem;line-height:1.5">"{quote}"</div>
        <div style="font-size:0.72rem;color:#9ca3af;margin-top:3px">&#8212; {author}</div>
    </div>
    """, unsafe_allow_html=True)


def page_library():
    hdr("📚 Biblioteca","Todos os seus livros")
    tab_books,tab_trash=st.tabs(["📚 Livros","🗑️ Lixeira"])
    with tab_books: _lib_books()
    with tab_trash: _lib_trash()

def _lib_books():
    c1,c2,c3,c4,c5=st.columns([3,2,2,2,1])
    with c1: query=st.text_input("🔍","",placeholder="Buscar…",label_visibility="collapsed")
    with c2: gf=st.selectbox("g",["Todos"]+book_genres(),label_visibility="collapsed")
    with c3: sf=st.selectbox("s",["Todos"]+STATUSES,label_visibility="collapsed")
    with c4:
        sort=st.selectbox("Ordenar",["Atualizado","Aberto recentemente","Título","Criado"],label_visibility="collapsed")
        sort_map={"Atualizado":"updated","Aberto recentemente":"opened","Título":"title","Criado":"created"}
    with c5:
        if st.button("✚ Novo",use_container_width=True):
            st.session_state["show_new_book"]=True; st.session_state.pop("show_edit_book",None)

    if st.session_state.get("show_new_book"):
        with st.expander("📖 Novo Livro",expanded=True):
            with st.form("nb"):
                ca,cb=st.columns([1,2])
                with ca: cf=st.file_uploader("Capa",type=["jpg","jpeg","png","webp"])
                with cb:
                    t=st.text_input("Título *"); syn=st.text_area("Sinopse",height=90)
                    cg,cs=st.columns(2)
                    with cg: g=st.selectbox("Gênero",[""]+GENRES)
                    with cs: s=st.selectbox("Status",STATUSES)
                s1,s2=st.columns(2)
                with s1: ok=st.form_submit_button("💾 Criar",use_container_width=True)
                with s2:
                    if st.form_submit_button("❌ Cancelar",use_container_width=True):
                        st.session_state["show_new_book"]=False; st.rerun()
                if ok:
                    if not t.strip(): st.error("Título obrigatório.")
                    else:
                        img,mime=(img_process(cf) if cf else (None,"image/jpeg"))
                        book_create(t.strip(),syn,g,s,img,mime)
                        st.session_state["show_new_book"]=False; st.rerun()

    eid=st.session_state.get("show_edit_book")
    if eid:
        bk=book_get(eid)
        if bk: _lib_edit(bk)

    books=book_list(query,None if gf=="Todos" else gf,None if sf=="Todos" else sf,sort_map.get(sort,"updated"))
    if not books:
        st.markdown('<div style="text-align:center;padding:4rem;color:#64748b"><div style="font-size:4rem">📚</div><h3 style="color:#7c3aed">Nenhum livro encontrado</h3></div>',unsafe_allow_html=True)
        return
    for i in range(0,len(books),4):
        cols=st.columns(4)
        for j,bk in enumerate(books[i:i+4]):
            with cols[j]: _lib_card(bk)

def _lib_card(bk):
    bid=bk["id"]; is_edit=st.session_state.get("show_edit_book")==bid
    if bk.get("cover_image"):
        cover=f'<img src="{img_b64(bk["cover_image"])}" style="width:100%;aspect-ratio:2/3;object-fit:cover;border-radius:8px;border:1px solid #2a2a4a">'
    else:
        color=STATUS_COLOR.get(bk.get("status",""),"#1e1b4b")
        cover=f'<div style="width:100%;aspect-ratio:2/3;background:linear-gradient(135deg,{color}44,{color}22);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:3rem;border:1px solid {color}33">📖</div>'
    bdr="border-color:#6366f1!important;" if is_edit else ""
    wc=f"{bk.get('word_count',0):,}".replace(",",".")
    chs=ch_list_lw(bid)
    st.markdown(
        f'<div style="background:#fff;border:1px solid #f5f0ff;border-radius:18px;'
        f'padding:1rem;margin-bottom:0.5rem;box-shadow:0 2px 10px rgba(124,58,237,.06);{bdr}">'
        f'{cover}'
        f'<div style="margin-top:0.75rem">'
        f'<div style="font-weight:700;color:#1e1b2e;font-size:0.9rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis" title="{bk[chr(34)+"title"+chr(34)]}">{bk["title"]}</div>'
        f'<div style="margin:4px 0">{badge(bk.get("status","Planejamento"))}</div>'
        f'<div style="font-size:0.72rem;color:#9ca3af;display:flex;justify-content:space-between">'
        f'<span>{bk.get("genre","") or "—"}</span><span>{len(chs)} cap · {wc} palavras</span>'
        f'</div></div></div>',
        unsafe_allow_html=True,
    )
    c1,c2,c3=st.columns(3)
    with c1:
        lbl="✏️ Fechar" if is_edit else "✏️ Editar"
        if st.button(lbl,key=f"e_{bid}",use_container_width=True):
            if is_edit: st.session_state.pop("show_edit_book",None)
            else: st.session_state["show_edit_book"]=bid; st.session_state["show_new_book"]=False
            st.rerun()
    with c2:
        if st.button("✍️ Escrever",key=f"w_{bid}",use_container_width=True):
            st.session_state["selected_book_id"]=bid; book_touch(bid)
            st.session_state["current_page"]="✍️ Capítulos"; st.rerun()
    with c3:
        if st.button("📖 Ler",key=f"r_{bid}",use_container_width=True):
            st.session_state["kindle_book_id"]=bid; book_touch(bid)
            st.session_state["current_page"]="📖 Modo Kindle"; st.rerun()

def _lib_edit(bk):
    bid=bk["id"]; ck=f"cdel_{bid}"
    with st.expander(f"✏️ {bk['title']}",expanded=True):
        with st.form(f"ef_{bid}"):
            ca,cb=st.columns([1,2])
            with ca:
                if bk.get("cover_image"):
                    st.markdown(f'<img src="{img_b64(bk["cover_image"])}" style="width:100%;border-radius:8px;margin-bottom:0.5rem">',unsafe_allow_html=True)
                cf=st.file_uploader("Nova capa",type=["jpg","jpeg","png","webp"],key=f"cf_{bid}")
            with cb:
                t=st.text_input("Título",value=bk["title"]); syn=st.text_area("Sinopse",value=bk.get("synopsis",""),height=90)
                cg,cs=st.columns(2)
                with cg:
                    opts=[""]+GENRES; cur=bk.get("genre","")
                    g=st.selectbox("Gênero",opts,index=opts.index(cur) if cur in opts else 0)
                with cs:
                    cur=bk.get("status",STATUSES[0])
                    if cur not in STATUSES: cur=STATUSES[0]
                    s=st.selectbox("Status",STATUSES,index=STATUSES.index(cur))
            s1,s2,s3=st.columns(3)
            with s1:
                if st.form_submit_button("💾 Salvar",use_container_width=True):
                    kw=dict(title=t.strip(),synopsis=syn,genre=g,status=s)
                    if cf: img,mime=img_process(cf); kw["cover_image"]=img; kw["cover_mime"]=mime
                    book_update(bid,**kw); st.session_state.pop("show_edit_book",None); st.rerun()
            with s2:
                if st.form_submit_button("❌ Cancelar",use_container_width=True):
                    st.session_state.pop("show_edit_book",None); st.rerun()
            with s3:
                if st.form_submit_button("🗑️ Lixeira",use_container_width=True):
                    if st.session_state.get(ck):
                        book_soft_delete(bid); st.session_state.pop("show_edit_book",None); st.session_state.pop(ck,None); st.rerun()
                    else:
                        st.session_state[ck]=True; st.rerun()
        if st.session_state.get(ck):
            st.warning(f"⚠️ Mover **{bk['title']}** para a lixeira? Clique em 🗑️ novamente.")

def _lib_trash():
    deleted=book_list_deleted()
    if not deleted:
        st.markdown('<div style="text-align:center;padding:2.5rem;color:#9ca3af">✨ Lixeira vazia.</div>',unsafe_allow_html=True); return
    st.markdown(f"**{len(deleted)} livro(s) na lixeira**")
    for b in deleted:
        c1,c2,c3=st.columns([5,1,1])
        with c1: st.markdown(f'<div style="padding:0.5rem 0;border-bottom:1px solid #f0ebff"><span style="color:#1e1b2e;font-weight:500">{b["title"]}</span><span style="color:#9ca3af;font-size:0.75rem;margin-left:0.75rem">{b.get("genre","") or "—"} · {b.get("word_count",0):,} palavras</span></div>',unsafe_allow_html=True)
        with c2:
            if st.button("↩",key=f"rb_{b['id']}",use_container_width=True): book_restore(b["id"]); st.rerun()
        with c3:
            if st.button("💀",key=f"pb_{b['id']}",use_container_width=True): st.session_state[f"pbk_{b['id']}"]=True
        if st.session_state.get(f"pbk_{b['id']}"):
            st.warning(f"Excluir **{b['title']}** permanentemente?")
            p1,p2=st.columns(2)
            with p1:
                if st.button("✅ Sim",key=f"pby_{b['id']}"): book_hard_delete(b["id"]); st.session_state.pop(f"pbk_{b['id']}",None); st.rerun()
            with p2:
                if st.button("❌ Não",key=f"pbn_{b['id']}"): st.session_state.pop(f"pbk_{b['id']}",None); st.rerun()

# ══════════════════════════════════════════════════════
# CAPÍTULOS
# ══════════════════════════════════════════════════════

_AUTOSAVE=timedelta(seconds=45)
def _dk(i): return f"draft_{i}"
def _dirty(i): return f"dirty_{i}"
def _sat(i): return f"sat_{i}"
def _wstart(i): return f"wstart_{i}"

def _init_draft(ch):
    k=_dk(ch["id"])
    if k not in st.session_state:
        st.session_state[k]=ch.get("content") or ""; st.session_state[_dirty(ch["id"])]=False; st.session_state[_sat(ch["id"])]=datetime.now()

def _flush(cid,bid):
    content=st.session_state.get(_dk(cid),"")
    start=st.session_state.get(_wstart(cid)); minutes=int((datetime.now()-start).total_seconds()/60) if start else 0
    ch_save(cid,content,bid,minutes)
    st.session_state[_dirty(cid)]=False; st.session_state[_sat(cid)]=datetime.now(); st.session_state[_wstart(cid)]=datetime.now()

def _autosave(cid,bid):
    if not st.session_state.get(_dirty(cid)): return False
    if datetime.now()-st.session_state.get(_sat(cid),datetime.min)>=_AUTOSAVE:
        _flush(cid,bid); return True
    return False

def page_chapters():
    if st.session_state.get("focus_mode"):
        st.markdown("""<style>
        [data-testid="stSidebar"]{display:none!important}
        .block-container{max-width:920px!important;padding:1rem 1.5rem!important}
        </style>""", unsafe_allow_html=True)
        # Exit button — always visible so user is never stuck with no navigation
        _fcol, _ = st.columns([1, 6])
        with _fcol:
            if st.button("✕ Sair do foco", key="exit_focus_top", use_container_width=True):
                st.session_state["focus_mode"] = False
                st.rerun()
    hdr("✍️ Capítulos","Escreva e organize")
    books=book_list_lw()
    if not books: st.info("📚 Crie um livro primeiro."); return
    opts={b["id"]:b["title"] for b in books}; sel=st.session_state.get("selected_book_id")
    ids=list(opts.keys()); idx=ids.index(sel) if sel in ids else 0
    c1,c2,c3=st.columns([4,1,1])
    with c1:
        bid=st.selectbox("Livro",ids,format_func=lambda x:opts[x],index=idx,label_visibility="collapsed")
        if bid!=sel: st.session_state["selected_book_id"]=bid; st.session_state.pop("active_chapter_id",None); book_touch(bid)
    with c2:
        bk=book_get(bid)
        if bk: st.markdown(badge(bk.get("status","Planejamento")),unsafe_allow_html=True)
    with c3:
        lbl="🔲 Sair" if st.session_state.get("focus_mode") else "🔲 Foco"
        if st.button(lbl,use_container_width=True): st.session_state["focus_mode"]=not st.session_state.get("focus_mode",False); st.rerun()
    st.markdown("---")
    t1,t2,t3=st.tabs(["✍️ Editor","📊 Visão Geral","🗑️ Lixeira"])
    with t1: _ch_editor(bid)
    with t2: _ch_overview(bid)
    with t3: _ch_trash(bid)

def _ch_overview(bid):
    stats=ch_stats_for_book(bid)
    if not stats: st.markdown('<div style="text-align:center;padding:2rem;color:#64748b">Nenhum capítulo ainda.</div>',unsafe_allow_html=True); return
    total_wc=sum(c["word_count"] for c in stats); total_goal=sum(c["word_goal"] for c in stats if c.get("word_goal"))
    st.markdown(f'<div style="background:#f9f7ff;border:1px solid #ede9ff;border-radius:12px;padding:0.75rem 1rem;margin-bottom:1rem"><span style="color:#c084fc;font-weight:700">{total_wc:,}</span><span style="color:#9ca3af;font-size:0.8rem"> palavras · {reading_time(total_wc)} de leitura</span>{f" · <span style=\'color:#06b6d4;font-weight:700\'>{int(total_wc/total_goal*100)}%</span><span style=\'color:#9ca3af;font-size:0.8rem\'> da meta ({total_goal:,})</span>" if total_goal else ""}</div>',unsafe_allow_html=True)
    for ch in stats:
        wc=ch["word_count"]; goal=ch.get("word_goal",0); pct=min(100,int(wc/goal*100)) if goal else 0
        marker=ch.get("scene_marker","")
        st.markdown(f'<div style="background:#fff;border:1px solid #f5f0ff;border-radius:14px;padding:0.9rem 1rem;margin-bottom:0.5rem;box-shadow:0 2px 8px rgba(124,58,237,.05)"><div style="display:flex;justify-content:space-between;align-items:center"><div><span style="color:#1e1b2e;font-weight:500">{ch["title"]}</span>{f" <span style=\'background:#ede9ff;color:#7c3aed;padding:1px 8px;border-radius:10px;font-size:0.7rem\'>{marker}</span>" if marker else ""}</div><div style="text-align:right;font-size:0.8rem"><span style="color:#6366f1;font-weight:600">{wc:,}</span><span style="color:#64748b"> palavras · {reading_time(wc)}{f" · meta: {goal:,}" if goal else ""}</span></div></div>{f"<div style=\'margin-top:6px\'>{progress_bar(pct)}</div>" if goal else ""}</div>',unsafe_allow_html=True)

def _ch_editor(bid):
    nav=ch_list_lw(bid); focus=st.session_state.get("focus_mode",False)
    if focus: _ch_main(bid,nav)
    else:
        cl,ce=st.columns([1,3])
        with cl: _ch_sidebar(bid,nav)
        with ce: _ch_main(bid,nav)

def _ch_sidebar(bid,nav):
    st.markdown("**📑 Capítulos**")
    with st.form("nch"):
        nt=st.text_input("Novo capítulo",placeholder="Título…")
        if st.form_submit_button("✚ Adicionar",use_container_width=True) and nt.strip():
            cid=ch_create(bid,nt.strip()); st.session_state["active_chapter_id"]=cid; st.session_state[_wstart(cid)]=datetime.now(); st.rerun()
    st.markdown("")
    acid=st.session_state.get("active_chapter_id")
    for ch in nav:
        cid=ch["id"]; is_a=cid==acid; dirty=st.session_state.get(_dirty(cid),False) if is_a else False
        marker=ch.get("scene_marker",""); lbl=f"{'▶ ' if is_a else ''}{'🔴 ' if dirty else ''}{ch['title']}"
        cb,db=st.columns([4,1])
        with cb:
            if st.button(lbl,key=f"nb_{cid}",use_container_width=True):
                if cid!=acid:
                    if acid and st.session_state.get(_dirty(acid)): st.session_state["pending_switch"]=cid
                    else: st.session_state["active_chapter_id"]=cid; st.session_state.setdefault(_wstart(cid),datetime.now())
                    st.rerun()
        with db:
            if st.button("🗑",key=f"nd_{cid}"): st.session_state[f"cdel_{cid}"]=True
        if st.session_state.get(f"cdel_{cid}"):
            st.warning(f"Mover '{ch['title']}' para lixeira?")
            y,n=st.columns(2)
            with y:
                if st.button("Sim",key=f"cy_{cid}"):
                    ch_soft_delete(cid,bid); st.session_state.pop(f"cdel_{cid}",None)
                    if acid==cid: st.session_state.pop("active_chapter_id",None)
                    st.rerun()
            with n:
                if st.button("Não",key=f"cn_{cid}"): st.session_state.pop(f"cdel_{cid}",None); st.rerun()
        meta=f"{ch.get('word_count',0):,} palavras"
        if marker: meta+=f" · {marker}"
        if ch.get("word_goal"): meta+=f" · {min(100,int(ch['word_count']/ch['word_goal']*100))}% meta"
        st.markdown(f'<div style="font-size:0.68rem;color:#64748b;margin-top:-6px;padding-left:4px;margin-bottom:4px">{meta}</div>',unsafe_allow_html=True)
    if len(nav)>1:
        st.markdown("---")
        with st.expander("↕ Reordenar"):
            nm={c["id"]:c["title"] for c in nav}; mv=st.selectbox("Mover",list(nm.keys()),format_func=lambda x:nm[x])
            dr=st.radio("",["⬆ Subir","⬇ Descer"])
            if st.button("Aplicar"):
                ids=[c["id"] for c in nav]; i=ids.index(mv)
                if dr.startswith("⬆") and i>0: ids[i],ids[i-1]=ids[i-1],ids[i]
                elif dr.startswith("⬇") and i<len(ids)-1: ids[i],ids[i+1]=ids[i+1],ids[i]
                ch_reorder(bid,ids); st.rerun()

def _ch_main(bid,nav):
    acid=st.session_state.get("active_chapter_id"); pending=st.session_state.get("pending_switch")
    if pending and acid:
        tgt=next((c["title"] for c in nav if c["id"]==pending),"capítulo")
        st.warning(f"⚠️ Alterações não salvas. O que fazer antes de abrir **{tgt}**?")
        g1,g2,g3=st.columns(3)
        with g1:
            if st.button("💾 Salvar e continuar",use_container_width=True):
                _flush(acid,bid); st.session_state["active_chapter_id"]=pending; st.session_state.pop("pending_switch",None); st.rerun()
        with g2:
            if st.button("🗑 Descartar",use_container_width=True):
                st.session_state.pop(_dk(acid),None); st.session_state[_dirty(acid)]=False
                st.session_state["active_chapter_id"]=pending; st.session_state.pop("pending_switch",None); st.rerun()
        with g3:
            if st.button("❌ Cancelar",use_container_width=True): st.session_state.pop("pending_switch",None); st.rerun()
        return
    if not acid:
        st.markdown('<div style="text-align:center;padding:4rem;color:#9ca3af"><div style="font-size:3rem">✍️</div><h3 style="color:#7c3aed">Selecione ou crie um capítulo</h3></div>',unsafe_allow_html=True); return
    ch=ch_get(acid)
    if not ch: st.warning("Capítulo não encontrado."); return
    _init_draft(ch)
    ct,cw=st.columns([3,1])
    with ct:
        nt=st.text_input("Título",value=ch["title"],key=f"cht_{acid}")
        if nt!=ch["title"]: ch_update(acid,title=nt)
    with cw:
        draft=st.session_state.get(_dk(acid),""); wc=count_words(draft)
        dirty=st.session_state.get(_dirty(acid),False); sat=st.session_state.get(_sat(acid),datetime.now())
        ind="🔴 Não salvo" if dirty else f"✅ {sat.strftime('%H:%M')}"; ic="#f59e0b" if dirty else "#10b981"
        st.markdown(f'<div style="text-align:right;padding-top:1.5rem"><div style="font-size:0.72rem;color:{ic}">{ind}</div><div style="color:#6366f1;font-weight:700;font-size:1rem">{wc:,}</div><div style="color:#64748b;font-size:0.68rem">palavras · {reading_time(wc)}</div></div>',unsafe_allow_html=True)

    with st.expander("⚙️ Configurações do capítulo",expanded=False):
        cm1,cm2=st.columns(2)
        with cm1:
            new_marker=st.text_input("Marcador de cena",value=ch.get("scene_marker",""),placeholder="ex: Abertura, Clímax…",key=f"sm_{acid}")
            if new_marker!=ch.get("scene_marker",""): ch_update(acid,scene_marker=new_marker)
        with cm2:
            new_goal=st.number_input("Meta de palavras",value=ch.get("word_goal",0),min_value=0,step=100,key=f"wg_{acid}")
            if new_goal!=ch.get("word_goal",0): ch_update(acid,word_goal=new_goal)
        if new_goal: st.markdown(progress_bar(min(100,int(wc/new_goal*100)) if new_goal else 0,"#6366f1",f"{wc:,}/{new_goal:,}"),unsafe_allow_html=True)

    prev_on=st.session_state.get(f"prev_{acid}",False)
    ci,cp=st.columns([5,1])
    with ci: st.markdown('<div style="background:#f0ebff;border:1px solid #e9d5ff;border-radius:10px;padding:0.45rem 1rem;color:#7c3aed;font-size:0.85rem">💡 <b>Markdown</b> — **negrito** *itálico* ## Título &gt; Citação &nbsp;·&nbsp; Auto-save 45s</div>',unsafe_allow_html=True)
    with cp:
        if st.button("👁 Preview",use_container_width=True,key=f"pt_{acid}"): st.session_state[f"prev_{acid}"]=not prev_on; st.rerun()

    if prev_on:
        ec,pc=st.columns(2)
        with ec: content=st.text_area("",value=st.session_state.get(_dk(acid),""),height=500,key=f"ed_{acid}",label_visibility="collapsed",placeholder="Comece a escrever…")
        with pc:
            html=markdown2.markdown(st.session_state.get(_dk(acid),"") or "",extras=["fenced-code-blocks","tables","strike","footnotes"])
            st.markdown(f'<div style="background:#13131f;border:1px solid #1e1e3f;border-radius:8px;padding:1.5rem 2rem;font-family:Georgia,serif;line-height:1.85;color:#d1d5db;height:500px;overflow-y:auto;font-size:0.95rem">{html}</div>',unsafe_allow_html=True)
    else:
        content=st.text_area("",value=st.session_state.get(_dk(acid),""),height=500,key=f"ed_{acid}",label_visibility="collapsed",placeholder="Comece a escrever…")

    if content!=st.session_state.get(_dk(acid)):
        st.session_state[_dk(acid)]=content; st.session_state[_dirty(acid)]=True
        if _wstart(acid) not in st.session_state: st.session_state[_wstart(acid)]=datetime.now()

    s1,s2=st.columns([1,5])
    with s1:
        if st.button("💾 Salvar",key=f"sv_{acid}",use_container_width=True): _flush(acid,bid); st.rerun()
    if _autosave(acid,bid): st.toast("💾 Auto-saved!",icon="✅")

def _ch_trash(bid):
    deleted=ch_list_deleted(bid)
    if not deleted: st.markdown('<div style="text-align:center;padding:2rem;color:#9ca3af">✨ Lixeira vazia.</div>',unsafe_allow_html=True); return
    st.markdown(f"**{len(deleted)} capítulo(s) na lixeira**")
    for ch in deleted:
        c1,c2,c3=st.columns([5,1,1])
        with c1: st.markdown(f'<div style="padding:0.5rem 0;border-bottom:1px solid #f0ebff"><span style="color:#1e1b2e;font-weight:500">{ch["title"]}</span><span style="color:#9ca3af;font-size:0.75rem;margin-left:0.75rem">{ch.get("word_count",0):,} palavras · {(ch.get("deleted_at") or "")[:10]}</span></div>',unsafe_allow_html=True)
        with c2:
            if st.button("↩",key=f"cr_{ch['id']}",use_container_width=True): ch_restore(ch["id"],bid); st.rerun()
        with c3:
            if st.button("💀",key=f"cp_{ch['id']}",use_container_width=True): st.session_state[f"cpg_{ch['id']}"]=True
        if st.session_state.get(f"cpg_{ch['id']}"):
            st.warning("Excluir permanentemente?")
            p1,p2=st.columns(2)
            with p1:
                if st.button("✅ Sim",key=f"cpy_{ch['id']}"): ch_hard_delete(ch["id"],bid); st.session_state.pop(f"cpg_{ch['id']}",None); st.rerun()
            with p2:
                if st.button("❌ Não",key=f"cpn_{ch['id']}"): st.session_state.pop(f"cpg_{ch['id']}",None); st.rerun()

# ══════════════════════════════════════════════════════
# KINDLE
# ══════════════════════════════════════════════════════

_THEMES={"🌙 Escuro":{"bg":"#1a1209","text":"#d4a853","border":"#3d2e1a","prog":"#d4a853","nav":"#110e06"},"☀️ Claro":{"bg":"#faf6f0","text":"#2c2416","border":"#ede8e0","prog":"#6366f1","nav":"#f0ebe3"},"📜 Sépia":{"bg":"#f4ecd8","text":"#5c4a32","border":"#e8d9b8","prog":"#8b5e3c","nav":"#ecdfc8"}}
_FONTS={"Serif":"'Georgia','Palatino',serif","Sans":"'Helvetica Neue',Arial,sans-serif","Mono":"'Courier New',monospace"}
_SIZES=[13,15,17,19,21,24]

def page_kindle():
    st.session_state["kindle_active"]=True
    st.markdown("""<style>
    [data-testid="stSidebar"]{display:none!important}
    .block-container{padding:0!important;max-width:100%!important}
    .main{background:#0a0a0f!important}
    </style>""", unsafe_allow_html=True)
    books=book_list_lw()
    if not books:
        st.markdown('<div style="display:flex;align-items:center;justify-content:center;height:80vh;flex-direction:column;gap:1rem;color:#9ca3af"><div style="font-size:3rem">📭</div><p>Crie um livro primeiro.</p></div>',unsafe_allow_html=True); return
    opts={b["id"]:b["title"] for b in books}; ids=list(opts.keys())
    sbd,sidx=kindle_pos_get(); bid=st.session_state.get("kindle_book_id") or sbd
    if bid not in ids: bid=ids[0]
    cidx=st.session_state.get("kindle_chapter_idx")
    if cidx is None: cidx=sidx if sbd==bid else 0
    theme_k=st.session_state.get("kindle_theme","🌙 Escuro"); font_k=st.session_state.get("kindle_font","Serif")
    size=st.session_state.get("kindle_size",17)
    if size not in _SIZES: size=17
    T=_THEMES[theme_k]; FF=_FONTS[font_k]
    nav=ch_list_lw(bid)
    if not nav: st.markdown('<div style="text-align:center;padding:4rem;color:#64748b">Nenhum capítulo.</div>',unsafe_allow_html=True); return
    cidx=min(int(cidx),len(nav)-1)
    st.session_state["kindle_book_id"]=bid; st.session_state["kindle_chapter_idx"]=cidx; kindle_pos_save(bid,cidx)
    total_w=sum(c.get("word_count",0) for c in nav); words_r=sum(nav[i].get("word_count",0) for i in range(cidx+1))
    prog=int((cidx+1)/len(nav)*100); ch_nav=nav[cidx]; ch_id=ch_nav["id"]
    ch_full=ch_get(ch_id); content=(ch_full or {}).get("content","") or ""
    ck=f"khtml_{ch_id}_{hash(content)}"
    if ck not in st.session_state:
        st.session_state[ck]=markdown2.markdown(content or "_Capítulo vazio._",extras=["fenced-code-blocks","tables","break-on-newline"])
    html=st.session_state[ck]; bk=book_get(bid); bt=bk["title"] if bk else ""
    bk_count=len(bookmark_list(bid))
    st.markdown(f"""<style>
    .kr{{background:{T['bg']};color:{T['text']};font-family:{FF};font-size:{size}px;line-height:1.95;max-width:640px;margin:0 auto;padding:2rem 1.5rem}}
    .kr h1{{font-size:{int(size*1.6)}px;font-weight:700;text-align:center;margin:0 0 2rem;padding-bottom:1rem;border-bottom:1px solid {T['border']}}}
    .kr h2,.kr h3{{font-size:{int(size*1.2)}px;margin:1.8rem 0 0.8rem}}
    .kr p{{margin:0 0 1.1em;text-align:justify;text-indent:1.8em;hyphens:auto}}
    .kr p:first-of-type{{text-indent:0}}
    .kr blockquote{{border-left:3px solid {T['prog']};padding-left:1em;font-style:italic;opacity:0.8;margin:1em 0}}
    .kprog{{position:fixed;top:0;left:0;right:0;height:3px;background:rgba(128,128,128,0.15);z-index:1000}}
    .kprogf{{height:3px;width:{prog}%;background:{T['prog']}}}
    .ktop{{position:fixed;top:3px;left:0;right:0;height:42px;background:{T['nav']};border-bottom:1px solid {T['border']};display:flex;align-items:center;justify-content:space-between;padding:0 1rem;z-index:999}}
    .ktit{{font-size:0.75rem;color:{T['text']}99;letter-spacing:0.08em;text-transform:uppercase;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:70%}}
    .kmeta{{font-size:0.72rem;color:{T['text']}66;white-space:nowrap}}
    .karea{{padding:55px 0 90px;background:{T['bg']};min-height:100vh}}
    .knav{{position:fixed;bottom:0;left:0;right:0;background:{T['nav']};border-top:1px solid {T['border']};padding:0.6rem 1rem;display:flex;align-items:center;justify-content:space-between;z-index:999}}
    .knav-info{{flex:1;text-align:center;font-size:0.72rem;color:{T['text']}77}}
    </style>""",unsafe_allow_html=True)
    st.markdown(f"""
    <div class="kprog"><div class="kprogf"></div></div>
    <div class="ktop"><div class="ktit">{bt}</div><div class="kmeta">{cidx+1}/{len(nav)} · {prog}% · 🔖 {bk_count}</div></div>
    <div class="karea"><div class="kr"><h1>{ch_nav['title']}</h1><div>{html}</div></div></div>
    <div class="knav"><div style="min-width:90px"></div><div class="knav-info">{words_r:,} / {total_w:,} palavras</div><div style="min-width:90px"></div></div>
    """,unsafe_allow_html=True)
    nc1,nc2,nc3=st.columns([1,3,1])
    with nc1:
        if st.button("← Anterior",key="kprev",disabled=cidx==0,use_container_width=True):
            st.session_state["kindle_chapter_idx"]=cidx-1; kindle_pos_save(bid,cidx-1); st.rerun()
    with nc3:
        if st.button("Próximo →",key="knext",disabled=cidx>=len(nav)-1,use_container_width=True):
            st.session_state["kindle_chapter_idx"]=cidx+1; kindle_pos_save(bid,cidx+1); st.rerun()
    st.markdown("---")
    col_cfg,col_bk=st.columns(2)
    with col_cfg:
        with st.expander("⚙️ Configurações"):
            ca,cb,cc=st.columns(3)
            with ca:
                ntheme=st.selectbox("Tema",list(_THEMES.keys()),index=list(_THEMES.keys()).index(theme_k),key="kts")
                if ntheme!=theme_k: st.session_state["kindle_theme"]=ntheme; st.rerun()
            with cb:
                nfont=st.selectbox("Fonte",list(_FONTS.keys()),index=list(_FONTS.keys()).index(font_k),key="kfs")
                if nfont!=font_k: st.session_state["kindle_font"]=nfont; st.rerun()
            with cc:
                nsize=st.selectbox("Tam.",_SIZES,index=_SIZES.index(size),key="kss")
                if nsize!=size: st.session_state["kindle_size"]=nsize; st.rerun()
            ji=st.selectbox("Capítulo",range(len(nav)),format_func=lambda i:f"{i+1}. {nav[i]['title']}",index=cidx,key="kjump",label_visibility="collapsed")
            if ji!=cidx: st.session_state["kindle_chapter_idx"]=ji; kindle_pos_save(bid,ji); st.rerun()
            jb=st.selectbox("Livro",ids,format_func=lambda x:opts[x],index=ids.index(bid),key="kbjump",label_visibility="collapsed")
            if jb!=bid: st.session_state["kindle_book_id"]=jb; st.session_state["kindle_chapter_idx"]=0; kindle_pos_save(jb,0); book_touch(jb); st.rerun()
    with col_bk:
        with st.expander("🔖 Marcadores"):
            with st.form("add_bk"):
                note=st.text_input("Nota",placeholder="O que há de especial aqui…")
                if st.form_submit_button("🔖 Marcar capítulo atual",use_container_width=True): bookmark_add(bid,ch_id,note); st.rerun()
            bks=bookmark_list(bid)
            if bks:
                for bki in bks:
                    bc1,bc2=st.columns([4,1])
                    with bc1: st.markdown(f'<div style="font-size:0.85rem;color:#e2e8f0">{bki.get("ch_title","")}</div><div style="font-size:0.75rem;color:#64748b">{bki.get("note","")}</div>',unsafe_allow_html=True)
                    with bc2:
                        if st.button("×",key=f"bkd_{bki['id']}"): bookmark_delete(bki["id"]); st.rerun()
            else:
                st.markdown('<div style="color:#9ca3af;font-size:0.85rem">Nenhum marcador.</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# PERSONAGENS
# ══════════════════════════════════════════════════════

def page_characters():
    hdr("👥 Personagens","Gerencie os personagens")
    books=book_list_lw()
    if not books: st.info("📚 Crie um livro primeiro."); return
    opts={b["id"]:b["title"] for b in books}; sel=st.session_state.get("selected_book_id")
    ids=list(opts.keys()); idx=ids.index(sel) if sel in ids else 0
    c1,c2,c3,c4=st.columns([3,2,2,1])
    with c1: bid=st.selectbox("Livro",ids,format_func=lambda x:opts[x],index=idx,label_visibility="collapsed"); st.session_state["selected_book_id"]=bid
    with c2: q=st.text_input("🔍","",placeholder="Buscar…",label_visibility="collapsed")
    with c3: role_f=st.selectbox("Papel",["Todos"]+char_roles(bid),label_visibility="collapsed")
    with c4:
        if st.button("✚ Novo",use_container_width=True): st.session_state["show_new_char"]=True
    if st.session_state.get("show_new_char"): _char_form(bid)
    chars=char_search(bid,q) if q else char_list(bid,None if role_f=="Todos" else role_f)
    if not chars:
        st.markdown('<div style="text-align:center;padding:3rem;color:#9ca3af"><div style="font-size:3rem">👥</div><h3 style="color:#7c3aed">Nenhum personagem</h3></div>',unsafe_allow_html=True); return
    if len(chars)>=2 and not q:
        with st.expander("🕸️ Mapa de relacionamentos"):
            for ch in chars:
                if ch.get("relationships"): st.markdown(f'<div style="background:#faf8ff;border:1px solid #ede9ff;border-radius:12px;padding:0.75rem 1rem;margin-bottom:0.5rem"><span style="color:#7c3aed;font-weight:700">{ch["name"]}</span><span style="color:#64748b;font-size:0.85rem"> → {ch["relationships"]}</span></div>',unsafe_allow_html=True)
    for i in range(0,len(chars),3):
        cols=st.columns(3)
        for j,ch in enumerate(chars[i:i+3]):
            with cols[j]: _char_card(ch,bid)

def _char_form(bid,ch=None):
    is_edit=ch is not None; cid=ch["id"] if is_edit else None
    with st.expander(f"{'✏️ Editar' if is_edit else '✚ Novo'} Personagem",expanded=True):
        with st.form(f"cf_{cid or 'new'}"):
            c1,c2=st.columns([1,2])
            with c1:
                pf=st.file_uploader("Foto",type=["jpg","jpeg","png","webp"],key=f"pf_{cid or 'n'}")
                if is_edit and ch.get("photo"): st.markdown(f'<img src="{img_b64(ch["photo"])}" style="width:100%;border-radius:8px">',unsafe_allow_html=True)
            with c2:
                name=st.text_input("Nome *",value=ch["name"] if is_edit else "")
                age=st.text_input("Idade",value=ch.get("age","") if is_edit else "",placeholder="Ex: 26, desconhecida…")
                role_i=ROLES.index(ch["role"])+1 if is_edit and ch.get("role") in ROLES else 0
                role=st.selectbox("Papel",[""]+ROLES,index=role_i)
                desc=st.text_area("Descrição",value=ch.get("description","") if is_edit else "",height=70)
                rel=st.text_area("Relacionamentos",value=ch.get("relationships","") if is_edit else "",height=55)
                notes=st.text_area("Notas",value=ch.get("notes","") if is_edit else "",height=55)
            s1,s2=st.columns(2)
            with s1: ok=st.form_submit_button("💾 Salvar",use_container_width=True)
            with s2:
                if st.form_submit_button("❌ Cancelar",use_container_width=True):
                    st.session_state.pop("show_new_char",None); st.session_state.pop(f"edit_char_{cid}",None); st.rerun()
            if ok:
                if not name.strip(): st.error("Nome obrigatório.")
                else:
                    photo,mime=(img_process(pf,(300,300)) if pf else (None,"image/jpeg"))
                    if is_edit:
                        kw=dict(name=name,role=role,description=desc,relationships=rel,notes=notes,age=age)
                        if pf: kw["photo"]=photo; kw["photo_mime"]=mime
                        char_update(cid,**kw); st.session_state.pop(f"edit_char_{cid}",None)
                    else:
                        char_create(bid,name,role,desc,photo,mime,rel,notes,age)
                        st.session_state.pop("show_new_char",None)
                    st.rerun()

def _char_card(ch,bid):
    cid=ch["id"]
    photo_html=(f'<img src="{img_b64(ch["photo"])}" style="width:72px;height:72px;object-fit:cover;border-radius:50%;border:2px solid #6366f1">' if ch.get("photo") else '<div style="width:72px;height:72px;border-radius:50%;background:linear-gradient(135deg,#ede9ff,#ddd6fe);display:flex;align-items:center;justify-content:center;font-size:2rem">👤</div>')
    rc={"Protagonista":"#6366f1","Antagonista":"#ef4444","Vilão":"#ef4444","Mentor":"#f59e0b","Interesse Romântico":"#ec4899"}.get(ch.get("role",""),"#64748b")
    desc=(ch.get("description","") or "")[:120]; age_str=f" · {ch['age']}" if ch.get("age") else ""
    rel_html = f'<div style="font-size:0.75rem;color:#9ca3af;border-top:1px solid #f0ebff;padding-top:0.4rem;margin-top:0.4rem">🔗 {ch["relationships"][:70]}</div>' if ch.get("relationships") else ""
    dots = "…" if len(ch.get("description","") or "") > 120 else ""
    st.markdown(
        f'<div style="background:#fff;border:1px solid #f5f0ff;border-radius:16px;padding:1rem;margin-bottom:0.5rem;box-shadow:0 2px 10px rgba(124,58,237,.05)">'
        f'<div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.5rem">{photo_html}'
        f'<div style="min-width:0"><div style="font-weight:700;color:#e2e8f0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{ch["name"]}</div>'
        f'<div style="font-size:0.75rem;color:{rc};font-weight:600">{ch.get("role","")}{age_str}</div></div></div>'
        f'<div style="color:#6b7280;font-size:0.85rem;line-height:1.5">{desc}{dots}</div>'
        f'{rel_html}</div>',
        unsafe_allow_html=True,
    )
    c1,c2=st.columns(2)
    with c1:
        if st.button("✏️ Editar",key=f"ce_{cid}",use_container_width=True): st.session_state[f"edit_char_{cid}"]=True; st.rerun()
    with c2:
        if st.button("🗑️",key=f"cd_{cid}",use_container_width=True): char_soft_delete(cid); st.rerun()
    if st.session_state.get(f"edit_char_{cid}"): _char_form(bid,ch)

# ══════════════════════════════════════════════════════
# WORLD BUILDING
# ══════════════════════════════════════════════════════

def page_world():
    hdr("🌍 World Building","Construa o universo")
    books=book_list_lw()
    if not books: st.info("📚 Crie um livro primeiro."); return
    opts={b["id"]:b["title"] for b in books}; sel=st.session_state.get("selected_book_id"); ids=list(opts.keys())
    idx=ids.index(sel) if sel in ids else 0
    bid=st.selectbox("Livro",ids,format_func=lambda x:opts[x],index=idx,label_visibility="collapsed"); st.session_state["selected_book_id"]=bid
    t1,t2,t3=st.tabs(["📍 Locais","⚔️ Facções","⏳ Cronologia"])
    with t1: _world_locs(bid)
    with t2: _world_facs(bid)
    with t3: _world_ev(bid)

def _world_locs(bid):
    c1,c2=st.columns([5,1])
    with c1: q=st.text_input("🔍","",placeholder="Buscar locais…",key="lq",label_visibility="collapsed")
    with c2:
        if st.button("✚ Local",key="nl"): st.session_state["show_new_loc"]=True
    if st.session_state.get("show_new_loc"):
        with st.form("nlf"):
            n=st.text_input("Nome *"); d=st.text_area("Descrição",height=80); nt=st.text_area("Notas",height=60)
            s1,s2=st.columns(2)
            with s1:
                if st.form_submit_button("💾 Criar",use_container_width=True) and n.strip(): loc_create(bid,n,d,nt); st.session_state.pop("show_new_loc",None); st.rerun()
            with s2:
                if st.form_submit_button("❌ Cancelar",use_container_width=True): st.session_state.pop("show_new_loc",None); st.rerun()
    locs=loc_search(bid,q) if q else loc_list(bid)
    if not locs: st.markdown('<div style="text-align:center;padding:2rem;color:#9ca3af">📍 Nenhum local cadastrado.</div>',unsafe_allow_html=True); return
    for loc in locs:
        with st.expander(f"📍 {loc['name']}"):
            with st.form(f"lf_{loc['id']}"):
                n=st.text_input("Nome",value=loc["name"],key=f"ln_{loc['id']}")
                d=st.text_area("Descrição",value=loc.get("description",""),key=f"ld_{loc['id']}",height=80)
                nt=st.text_area("Notas",value=loc.get("notes",""),key=f"lnt_{loc['id']}",height=60)
                s1,s2=st.columns(2)
                with s1:
                    if st.form_submit_button("💾 Salvar",use_container_width=True): loc_update(loc["id"],name=n,description=d,notes=nt); st.rerun()
                with s2:
                    if st.form_submit_button("🗑️ Excluir",use_container_width=True): loc_soft_delete(loc["id"]); st.rerun()

def _world_facs(bid):
    c1=st.columns([5,1])
    with c1[1]:
        if st.button("✚ Facção",key="nf"): st.session_state["show_new_fac"]=True
    if st.session_state.get("show_new_fac"):
        with st.form("nff"):
            n=st.text_input("Nome *"); d=st.text_area("Descrição",height=80); nt=st.text_area("Notas",height=60)
            s1,s2=st.columns(2)
            with s1:
                if st.form_submit_button("💾 Criar",use_container_width=True) and n.strip(): fac_create(bid,n,d,nt); st.session_state.pop("show_new_fac",None); st.rerun()
            with s2:
                if st.form_submit_button("❌ Cancelar",use_container_width=True): st.session_state.pop("show_new_fac",None); st.rerun()
    facs=fac_list(bid)
    if not facs: st.markdown('<div style="text-align:center;padding:2rem;color:#9ca3af">⚔️ Nenhuma facção cadastrada.</div>',unsafe_allow_html=True); return
    for f in facs:
        with st.expander(f"⚔️ {f['name']}"):
            with st.form(f"ff_{f['id']}"):
                n=st.text_input("Nome",value=f["name"],key=f"fn_{f['id']}")
                d=st.text_area("Descrição",value=f.get("description",""),key=f"fd_{f['id']}",height=80)
                nt=st.text_area("Notas",value=f.get("notes",""),key=f"fnt_{f['id']}",height=60)
                s1,s2=st.columns(2)
                with s1:
                    if st.form_submit_button("💾 Salvar",use_container_width=True): fac_update(f["id"],name=n,description=d,notes=nt); st.rerun()
                with s2:
                    if st.form_submit_button("🗑️ Excluir",use_container_width=True): fac_soft_delete(f["id"]); st.rerun()

def _world_ev(bid):
    c1=st.columns([5,1])
    with c1[1]:
        if st.button("✚ Evento",key="ne"): st.session_state["show_new_ev"]=True
    if st.session_state.get("show_new_ev"):
        with st.form("nef"):
            t=st.text_input("Título *"); dl=st.text_input("Data/Período",placeholder="Ex: Ano 432…"); d=st.text_area("Descrição",height=80)
            s1,s2=st.columns(2)
            with s1:
                if st.form_submit_button("💾 Criar",use_container_width=True) and t.strip(): ev_create(bid,t,d,dl); st.session_state.pop("show_new_ev",None); st.rerun()
            with s2:
                if st.form_submit_button("❌ Cancelar",use_container_width=True): st.session_state.pop("show_new_ev",None); st.rerun()
    evs=ev_list(bid)
    if not evs: st.markdown('<div style="text-align:center;padding:2rem;color:#9ca3af">⏳ Nenhum evento na cronologia.</div>',unsafe_allow_html=True); return
    for i,ev in enumerate(evs):
        lbl=f"📅 {ev.get('date_label','')} — {ev['title']}" if ev.get('date_label') else f"{'🟣' if i==0 else '📅'} {ev['title']}"
        with st.expander(lbl):
            with st.form(f"ef_{ev['id']}"):
                t=st.text_input("Título",value=ev["title"],key=f"et_{ev['id']}")
                dl=st.text_input("Data",value=ev.get("date_label",""),key=f"edl_{ev['id']}")
                d=st.text_area("Descrição",value=ev.get("description",""),key=f"ed_{ev['id']}",height=80)
                s1,s2=st.columns(2)
                with s1:
                    if st.form_submit_button("💾 Salvar",use_container_width=True): ev_update(ev["id"],title=t,description=d,date_label=dl); st.rerun()
                with s2:
                    if st.form_submit_button("🗑️ Excluir",use_container_width=True): ev_soft_delete(ev["id"]); st.rerun()

# ══════════════════════════════════════════════════════
# BRAIN DUMP
# ══════════════════════════════════════════════════════

def page_brain_dump():
    hdr("🧠 Brain Dump","Capture ideias antes que se percam")
    books=book_list_lw()
    c1,c2,c3,c4=st.columns([3,2,2,1])
    with c1: q=st.text_input("🔍","",placeholder="Buscar…",label_visibility="collapsed")
    with c2: all_tags=bd_tags(); tf=st.selectbox("Tag",["Todas"]+all_tags,label_visibility="collapsed")
    with c3:
        bopts={None:"Todos os livros"}; bopts.update({b["id"]:b["title"] for b in books})
        bf=st.selectbox("Livro",list(bopts.keys()),format_func=lambda x:bopts[x],label_visibility="collapsed")
    with c4:
        if st.button("✚ Ideia",use_container_width=True): st.session_state["show_new_dump"]=True

    if st.session_state.get("show_new_dump"):
        with st.form("nbd"):
            c=st.text_area("Ideia *",height=120,label_visibility="collapsed",placeholder="Capture sua ideia aqui…")
            ti,tg=st.columns(2)
            with ti: tags=st.text_input("Tags",placeholder="plot, revisar, personagem")
            with tg:
                lb=[None]+[b["id"] for b in books]
                lbk=st.selectbox("Vincular a livro",lb,format_func=lambda x:"Sem vínculo" if x is None else bopts.get(x,""),label_visibility="collapsed")
            s1,s2=st.columns(2)
            with s1:
                if st.form_submit_button("💾 Salvar",use_container_width=True):
                    if c.strip(): bd_create(c,lbk,",".join(t.strip() for t in tags.split(",") if t.strip())); st.session_state.pop("show_new_dump",None); st.rerun()
            with s2:
                if st.form_submit_button("❌ Cancelar",use_container_width=True): st.session_state.pop("show_new_dump",None); st.rerun()

    tag_f=None if tf=="Todas" else tf
    dumps=bd_list(q,bf,tag_f)
    if not dumps:
        st.markdown('<div style="text-align:center;padding:3rem;color:#9ca3af"><div style="font-size:3rem">🧠</div><h3 style="color:#7c3aed">Nenhuma ideia ainda</h3></div>',unsafe_allow_html=True); return
    st.markdown(f"<div style='color:#64748b;font-size:0.85rem;margin-bottom:1rem'>{len(dumps)} ideia(s)</div>",unsafe_allow_html=True)

    for d in dumps:
        did=d["id"]; tags=[t.strip() for t in d.get("tags","").split(",") if t.strip()]
        tags_html=" ".join(f'<span style="background:#ede9ff;color:#7c3aed;padding:2px 8px;border-radius:12px;font-size:0.72rem">{t}</span>' for t in tags)
        is_pinned=bool(d.get("pinned")); pin_icon="📌" if is_pinned else "📍"
        preview=(d["content"][:300]+("…" if len(d["content"])>300 else "")).replace("\n","<br>")
        linked_book=""
        if d.get("book_id"): bname=bopts.get(d["book_id"],""); linked_book=f'<span style="color:#06b6d4;font-size:0.72rem">📚 {bname}</span>' if bname else ""
        if st.session_state.get(f"ed_bd_{did}"):
            with st.form(f"bdf_{did}"):
                nc=st.text_area("",value=d["content"],height=120,label_visibility="collapsed")
                nt=st.text_input("Tags",value=d.get("tags",""))
                s1,s2,s3=st.columns(3)
                with s1:
                    if st.form_submit_button("💾 Salvar"): bd_update(did,nc,nt); st.session_state.pop(f"ed_bd_{did}",None); st.rerun()
                with s2:
                    if st.form_submit_button("❌ Cancelar"): st.session_state.pop(f"ed_bd_{did}",None); st.rerun()
                with s3:
                    if st.form_submit_button("🗑️ Excluir"): bd_soft_delete(did); st.session_state.pop(f"ed_bd_{did}",None); st.rerun()
        else:
            border="border-left:3px solid #f59e0b;" if is_pinned else ""
            st.markdown(f'<div style="background:#fff;border:1px solid #f5f0ff;border-radius:14px;padding:1rem;margin-bottom:0.75rem;box-shadow:0 2px 8px rgba(124,58,237,.05);{border}"><div style="display:flex;justify-content:space-between;margin-bottom:0.5rem"><div style="display:flex;gap:0.4rem;flex-wrap:wrap">{tags_html}</div><div style="display:flex;gap:0.5rem;align-items:center">{linked_book}<span style="font-size:0.72rem;color:#64748b">{d.get("created_at","")[:10]}</span></div></div><div style="color:#374151;line-height:1.7;font-size:0.9rem">{preview}</div></div>',unsafe_allow_html=True)
            bc1,bc2,bc3=st.columns([1,1,5])
            with bc1:
                if st.button(pin_icon,key=f"pin_{did}",help="Fixar/desfixar"): bd_toggle_pin(did); st.rerun()
            with bc2:
                if st.button("✏️",key=f"ebd_{did}"): st.session_state[f"ed_bd_{did}"]=True; st.rerun()

# ══════════════════════════════════════════════════════
# EXPORTAR
# ══════════════════════════════════════════════════════

def page_export():
    hdr("📤 Exportar","Exporte em PDF, DOCX ou EPUB")
    books=book_list_lw()
    if not books: st.info("📚 Crie e escreva um livro primeiro."); return
    opts={b["id"]:b["title"] for b in books}; sel=st.session_state.get("selected_book_id"); ids=list(opts.keys())
    idx=ids.index(sel) if sel in ids else 0
    bid=st.selectbox("Livro",ids,format_func=lambda x:opts[x],index=idx)
    bk=book_get(bid)
    if not bk: return
    wc=bk.get("word_count",0); chs=ch_list_lw(bid); rt=reading_time(wc)
    st.markdown(f'<div style="background:#fff;border:1px solid #f5f0ff;border-radius:16px;padding:1.25rem;margin:1rem 0;box-shadow:0 2px 10px rgba(124,58,237,.06);display:flex;gap:1.5rem;align-items:flex-start">{"<img src="+chr(39)+img_b64(bk["cover_image"])+chr(39)+" style="+chr(39)+"width:80px;height:120px;object-fit:cover;border-radius:6px"+chr(39)+">" if bk.get("cover_image") else "<div style=\'width:80px;height:120px;background:linear-gradient(135deg,#1e1b4b,#2d1b69);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:2rem\'>📖</div>"}<div><div style="font-size:1.25rem;font-weight:700;color:#e2e8f0;margin-bottom:0.25rem">{bk["title"]}</div><div style="color:#64748b;font-size:0.85rem;margin-bottom:0.5rem">{bk.get("genre","") or "—"} · {bk.get("status","")}</div><div style="display:flex;gap:1rem;flex-wrap:wrap"><span style="color:#6366f1;font-size:0.85rem">📄 {len(chs)} capítulos</span><span style="color:#10b981;font-size:0.85rem">✍️ {wc:,} palavras</span><span style="color:#06b6d4;font-size:0.85rem">📖 {rt}</span></div></div></div>',unsafe_allow_html=True)
    if wc==0: st.warning("⚠️ Nenhum conteúdo para exportar. Escreva alguns capítulos primeiro.")
    st.markdown("### Formatos")
    c1,c2,c3=st.columns(3)
    for col,fmt,icon,desc,fn,mime,ext in [
        (c1,"PDF","📄","Formatado para impressão. Inclui capa, sumário e números de página.",export_pdf,"application/pdf","pdf"),
        (c2,"DOCX","📝","Microsoft Word com capa e sumário. Edite após exportar.",export_docx,"application/vnd.openxmlformats-officedocument.wordprocessingml.document","docx"),
        (c3,"EPUB","📱","Kindle, Kobo, Apple Books. Inclui capa e metadados.",export_epub,"application/epub+zip","epub"),
    ]:
        with col:
            st.markdown(f'<div style="background:#fff;border:1px solid #f5f0ff;border-radius:16px;padding:1.25rem;text-align:center;margin-bottom:0.75rem;min-height:120px;box-shadow:0 2px 8px rgba(124,58,237,.05)"><div style="font-size:2.5rem">{icon}</div><div style="font-weight:700;color:#1e1b2e;margin:0.4rem 0">{fmt}</div><div style="color:#64748b;font-size:0.78rem;line-height:1.4">{desc}</div></div>',unsafe_allow_html=True)
            if st.button(f"⬇ Gerar {fmt}",key=f"exp_{fmt}",use_container_width=True,disabled=wc==0):
                with st.spinner(f"Gerando {fmt}…"):
                    try:
                        data=fn(bid); fname=f"{bk['title'].replace(' ','_')}.{ext}"
                        st.download_button(f"📥 Baixar {fmt}",data=data,file_name=fname,mime=mime,use_container_width=True,key=f"dl_{fmt}"); st.success(f"✅ {fmt} pronto!")
                    except Exception as e:
                        st.error(f"Erro ao gerar {fmt}: {e}")
