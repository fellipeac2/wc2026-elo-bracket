import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="Copa 2026 — ELO",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────
# PONTOS FIFA  (FIFA/Coca-Cola Men's World Ranking · jun 2026)
# Fonte: inside.fifa.com  —  o sistema FIFA usa modelo ELO
# ─────────────────────────────────────────────────────────────────
ELO: dict[str, float] = {
    "Argentina":       1907.40, "França":          1906.84, "Espanha":         1879.58,
    "Inglaterra":      1840.46, "Brasil":          1785.19, "Marrocos":        1776.40,
    "Holanda":         1775.50, "Portugal":        1764.86, "México":          1736.01,
    "Bélgica":         1735.41, "Colômbia":        1729.30, "Alemanha":        1726.22,
    "Croácia":         1723.05, "EUA":             1677.17, "Suíça":           1676.00,
    "Japão":           1673.68, "Senegal":         1653.43, "Áustria":         1598.82,
    "Noruega":         1594.04, "Equador":         1592.59, "Egito":           1584.71,
    "Austrália":       1581.35, "Argélia":         1576.80, "Costa do Marfim": 1565.47,
    "Canadá":          1551.07, "Suécia":          1525.58, "Paraguai":        1520.59,
    "Congo DR":        1495.48, "África do Sul":   1451.24, "Bósnia":          1408.93,
    "Cabo Verde":      1402.97, "Gana":            1387.00,
}

FLAGS: dict[str, str] = {
    "Espanha": "🇪🇸", "Argentina": "🇦🇷", "França": "🇫🇷",
    "Inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Brasil": "🇧🇷", "Colômbia": "🇨🇴",
    "Portugal": "🇵🇹", "Alemanha": "🇩🇪", "Holanda": "🇳🇱",
    "Bélgica": "🇧🇪", "Senegal": "🇸🇳", "Marrocos": "🇲🇦",
    "Noruega": "🇳🇴", "Croácia": "🇭🇷", "Suíça": "🇨🇭",
    "Áustria": "🇦🇹", "Costa do Marfim": "🇨🇮", "Suécia": "🇸🇪",
    "EUA": "🇺🇸", "México": "🇲🇽", "Equador": "🇪🇨",
    "Japão": "🇯🇵", "Austrália": "🇦🇺", "África do Sul": "🇿🇦",
    "Canadá": "🇨🇦", "Paraguai": "🇵🇾", "Egito": "🇪🇬",
    "Bósnia": "🇧🇦", "Congo DR": "🇨🇩", "Cabo Verde": "🇨🇻",
    "Gana": "🇬🇭", "Argélia": "🇩🇿",
}


def flag(team: str) -> str:
    return FLAGS.get(team, "🏳️")


# ─────────────────────────────────────────────────────────────────
# BRACKET TREE
# ─────────────────────────────────────────────────────────────────
class Node:
    def __init__(self, label: str, left=None, right=None, team: str | None = None):
        self.label = label
        self.left = left
        self.right = right
        self.team = team

    @property
    def is_team(self) -> bool:
        return self.team is not None

    def all_teams(self) -> list[str]:
        if self.is_team:
            return [self.team]
        return self.left.all_teams() + self.right.all_teams()


def T(name: str) -> Node:
    return Node(name, team=name)


def M(label: str, a: str, b: str) -> Node:
    return Node(label, left=T(a), right=T(b))


# Chaveamento oficial (Globo Esporte / FIFA, 28 jun 2026)
#
# LADO ESQUERDO → Semifinal 1:
#   O1: Alemanha/Paraguai × França/Suécia
#   O2: África do Sul/Canadá × Holanda/Marrocos
#   Q1: O1 × O2
#   O3: Portugal/Croácia × Espanha/Áustria
#   O4: EUA/Bósnia × Bélgica/Senegal
#   Q2: O3 × O4
#   S1: Q1 × Q2
#
# LADO DIREITO → Semifinal 2:
#   O5: Brasil/Japão × Costa do Marfim/Noruega
#   O6: México/Equador × Inglaterra/Congo DR
#   Q3: O5 × O6
#   O7: Argentina/Cabo Verde × Austrália/Egito
#   O8: Suíça/Argélia × Colômbia/Gana
#   Q4: O7 × O8
#   S2: Q3 × Q4
#
# FINAL: S1 × S2  →  França só encontra Brasil na final

r32: dict[str, Node] = {
    # Lado esquerdo
    "MA": M("Alemanha × Paraguai (29/jun)",       "Alemanha",        "Paraguai"),
    "MB": M("França × Suécia (30/jun)",           "França",          "Suécia"),
    "MC": M("África do Sul × Canadá (28/jun)",    "África do Sul",   "Canadá"),
    "MD": M("Holanda × Marrocos (29/jun)",        "Holanda",         "Marrocos"),
    "ME": M("Portugal × Croácia (2/jul)",         "Portugal",        "Croácia"),
    "MF": M("Espanha × Áustria (2/jul)",          "Espanha",         "Áustria"),
    "MG": M("EUA × Bósnia (1/jul)",               "EUA",             "Bósnia"),
    "MH": M("Bélgica × Senegal (1/jul)",          "Bélgica",         "Senegal"),
    # Lado direito
    "MI": M("Brasil × Japão (29/jun)",            "Brasil",          "Japão"),
    "MJ": M("Costa do Marfim × Noruega (30/jun)", "Costa do Marfim", "Noruega"),
    "MK": M("México × Equador (30/jun)",          "México",          "Equador"),
    "ML": M("Inglaterra × Congo DR (1/jul)",      "Inglaterra",      "Congo DR"),
    "MM": M("Argentina × Cabo Verde (3/jul)",     "Argentina",       "Cabo Verde"),
    "MN": M("Austrália × Egito (3/jul)",          "Austrália",       "Egito"),
    "MO": M("Suíça × Argélia (3/jul)",            "Suíça",           "Argélia"),
    "MP": M("Colômbia × Gana (3/jul)",            "Colômbia",        "Gana"),
}

r16: dict[str, Node] = {
    # Lado esquerdo → Semifinal 1
    "O1": Node("Oitavas 1: venc(Alem/Par) × venc(Fra/Sue) — 4/jul",   r32["MA"], r32["MB"]),
    "O2": Node("Oitavas 2: venc(AfSul/Can) × venc(Hol/Mar) — 4/jul",  r32["MC"], r32["MD"]),
    "O3": Node("Oitavas 3: venc(Por/Cro) × venc(Esp/Aut) — 6/jul",    r32["ME"], r32["MF"]),
    "O4": Node("Oitavas 4: venc(EUA/Bos) × venc(Bel/Sen) — 6/jul",    r32["MG"], r32["MH"]),
    # Lado direito → Semifinal 2
    "O5": Node("Oitavas 5: venc(Bra/Jap) × venc(Mar/Nor) — 5/jul",    r32["MI"], r32["MJ"]),
    "O6": Node("Oitavas 6: venc(Mex/Equ) × venc(Ing/Con) — 5/jul",    r32["MK"], r32["ML"]),
    "O7": Node("Oitavas 7: venc(Arg/Cab) × venc(Aus/Egi) — 7/jul",    r32["MM"], r32["MN"]),
    "O8": Node("Oitavas 8: venc(Sui/Alg) × venc(Col/Gan) — 7/jul",    r32["MO"], r32["MP"]),
}

qf: dict[str, Node] = {
    "Q1": Node("Quartas 1: O1 × O2 — 9/jul",   r16["O1"], r16["O2"]),
    "Q2": Node("Quartas 2: O3 × O4 — 10/jul",  r16["O3"], r16["O4"]),
    "Q3": Node("Quartas 3: O5 × O6 — 11/jul",  r16["O5"], r16["O6"]),
    "Q4": Node("Quartas 4: O7 × O8 — 11/jul",  r16["O7"], r16["O8"]),
}

sf: dict[str, Node] = {
    "S1": Node("Semifinal 1: Q1 × Q2 — 14/jul", qf["Q1"], qf["Q2"]),
    "S2": Node("Semifinal 2: Q3 × Q4 — 15/jul", qf["Q3"], qf["Q4"]),
}

final = Node("Final 🏆 — 19/jul", sf["S1"], sf["S2"])

# ─────────────────────────────────────────────────────────────────
# PROBABILITY ENGINE
# ─────────────────────────────────────────────────────────────────
def win_prob(elo_a: float, elo_b: float) -> float:
    return 1.0 / (1.0 + 10.0 ** ((elo_b - elo_a) / 400.0))


@st.cache_data(show_spinner=False)
def node_win_probs(label: str, _node: Node) -> dict[str, float]:
    """P(team wins this node) for every team in the subtree."""
    if _node.is_team:
        return {_node.team: 1.0}
    lp = node_win_probs(_node.left.label,  _node.left)
    rp = node_win_probs(_node.right.label, _node.right)
    result: dict[str, float] = {}
    for ta, pa in lp.items():
        result[ta] = sum(pa * pb * win_prob(ELO[ta], ELO[tb]) for tb, pb in rp.items())
    for tb, pb in rp.items():
        result[tb] = sum(pb * pa * win_prob(ELO[tb], ELO[ta]) for ta, pa in lp.items())
    return result


# ─────────────────────────────────────────────────────────────────
# VISUAL LAYOUT  (visual slot order for the bracket figure)
# ─────────────────────────────────────────────────────────────────
# R32 rows: cada par consecutivo alimenta a mesma oitava
# Linhas 0-7  = lado esquerdo → S1 (França, Alemanha, Espanha, Portugal…)
# Linhas 8-15 = lado direito  → S2 (Brasil, Argentina, México, Inglaterra…)
ROW_ORDER: list[Node] = [
    r32["MA"], r32["MB"],   # → O1  (Alemanha/Paraguai × França/Suécia)
    r32["MC"], r32["MD"],   # → O2  (África do Sul/Canadá × Holanda/Marrocos)
    r32["ME"], r32["MF"],   # → O3  (Portugal/Croácia × Espanha/Áustria)
    r32["MG"], r32["MH"],   # → O4  (EUA/Bósnia × Bélgica/Senegal)
    r32["MI"], r32["MJ"],   # → O5  (Brasil/Japão × Marfim/Noruega)
    r32["MK"], r32["ML"],   # → O6  (México/Equador × Inglaterra/Congo)
    r32["MM"], r32["MN"],   # → O7  (Argentina/Cabo Verde × Austrália/Egito)
    r32["MO"], r32["MP"],   # → O8  (Suíça/Argélia × Colômbia/Gana)
]

R16_ORDER = [r16["O1"], r16["O2"], r16["O3"], r16["O4"],
             r16["O5"], r16["O6"], r16["O7"], r16["O8"]]
QF_ORDER  = [qf["Q1"], qf["Q2"], qf["Q3"], qf["Q4"]]
SF_ORDER  = [sf["S1"], sf["S2"]]

# (round_idx, slot_idx, node)
VISUAL_NODES: list[tuple[int, int, Node]] = (
    [(0, i, n) for i, n in enumerate(ROW_ORDER)] +
    [(1, i, n) for i, n in enumerate(R16_ORDER)] +
    [(2, i, n) for i, n in enumerate(QF_ORDER)]  +
    [(3, i, n) for i, n in enumerate(SF_ORDER)]  +
    [(4, 0, final)]
)

NODE_BY_LABEL: dict[str, Node] = {n.label: n for _, _, n in VISUAL_NODES}

# Pre-compute all probabilities once
ALL_PROBS: dict[str, dict[str, float]] = {
    n.label: node_win_probs(n.label, n) for _, _, n in VISUAL_NODES
}

ELO_SORTED: list[tuple[str, float]] = sorted(ELO.items(), key=lambda x: -x[1])

# ─────────────────────────────────────────────────────────────────
# BRACKET FIGURE BUILDER
# ─────────────────────────────────────────────────────────────────
X_GAP   = 3.0    # horizontal space per round
BOX_W   = 2.7    # box width
BOX_H   = 0.82   # box height
N_ROWS  = 16     # total R32 rows

ROUND_LABELS = ["16-avos", "Oitavas", "Quartas", "Semis", "Final 🏆"]
DARK_BG = "rgba(14,17,30,1)"


def _cx(rnd: int) -> float:
    return rnd * X_GAP


def _cy(rnd: int, slot: int) -> float:
    step = 2 ** rnd
    return slot * step + (step - 1) / 2.0


def _elo_color(prob: float) -> str:
    """Red → amber → green based on favourite's win probability."""
    r = int(220 * (1 - prob))
    g = int(180 * prob + 40)
    return f"rgba({r},{g},55,0.92)"


@st.cache_data(show_spinner=False)
def build_bracket(selected_label: str | None = None) -> go.Figure:
    shapes: list[dict] = []
    annotations: list[dict] = []
    click_x, click_y, click_labels, click_ptidx = [], [], [], []
    line_x: list = []
    line_y: list = []

    for rnd, slot, node in VISUAL_NODES:
        cx = _cx(rnd)
        cy = _cy(rnd, slot)
        probs = ALL_PROBS[node.label]
        top  = max(probs, key=probs.__getitem__)
        topp = probs[top]
        is_sel = node.label == selected_label

        # ── box ──────────────────────────────────────
        shapes.append(dict(
            type="rect",
            x0=cx, x1=cx + BOX_W,
            y0=cy - BOX_H / 2, y1=cy + BOX_H / 2,
            fillcolor=_elo_color(topp),
            line=dict(color="gold" if is_sel else "rgba(200,200,200,0.35)",
                      width=2.5 if is_sel else 0.8),
        ))

        # ── label inside box ──────────────────────────
        teams_shown = sorted(probs.items(), key=lambda x: -x[1])[:3]
        lines = [f"<b>{flag(t)} {t}</b> <i>{p:.0%}</i>" for t, p in teams_shown]
        text = "<br>".join(lines)
        font_sz = 10.5

        annotations.append(dict(
            x=cx + BOX_W / 2, y=cy,
            text=text,
            showarrow=False,
            font=dict(size=font_sz, color="white"),
            align="center",
        ))

        # ── invisible click target ────────────────────
        click_x.append(cx + BOX_W / 2)
        click_y.append(cy)
        click_labels.append(node.label)
        click_ptidx.append(len(click_ptidx))

        # ── connector to parent round ─────────────────
        if rnd < 4:
            parent_cy = _cy(rnd + 1, slot // 2)
            parent_cx = _cx(rnd + 1)
            mid_x = cx + BOX_W + 0.12
            line_x += [cx + BOX_W, mid_x, mid_x, parent_cx, None]
            line_y += [cy, cy, parent_cy, parent_cy, None]

    fig = go.Figure()

    # connector lines
    fig.add_trace(go.Scatter(
        x=line_x, y=line_y,
        mode="lines",
        line=dict(color="rgba(160,160,180,0.35)", width=1.2),
        showlegend=False, hoverinfo="skip",
    ))

    # invisible click targets (one scatter point per box)
    fig.add_trace(go.Scatter(
        x=click_x, y=click_y,
        mode="markers",
        marker=dict(size=50, color="rgba(0,0,0,0)", symbol="square"),
        customdata=click_labels,
        text=click_labels,
        hovertemplate="%{text}<extra></extra>",
        showlegend=False,
    ))

    # round header labels
    for i, lbl in enumerate(ROUND_LABELS):
        annotations.append(dict(
            x=_cx(i) + BOX_W / 2, y=N_ROWS + 0.05,
            text=f"<b>{lbl}</b>",
            showarrow=False,
            font=dict(color="rgba(200,210,255,0.9)", size=11),
            align="center",
        ))

    fig.update_layout(
        shapes=shapes,
        annotations=annotations,
        xaxis=dict(visible=False, range=[-0.15, _cx(4) + BOX_W + 0.3]),
        yaxis=dict(visible=False, range=[-0.6, N_ROWS + 0.4]),
        height=820,
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor=DARK_BG,
        paper_bgcolor=DARK_BG,
        dragmode=False,
        clickmode="event+select",
    )
    return fig


# ─────────────────────────────────────────────────────────────────
# PROBABILITY PANEL
# ─────────────────────────────────────────────────────────────────
def _side_probs(node: Node) -> dict[str, float]:
    """P de cada time chegar ao confronto deste nó (vencer o seu lado)."""
    if node.is_team:
        return {node.team: 1.0}
    return node_win_probs(node.label, node)


def prob_panel(node: Node) -> None:
    """Tabela com barra de progresso — clique na linha para ver a decomposição."""
    probs = ALL_PROBS[node.label]
    teams_sorted = sorted(probs, key=lambda t: -probs[t])
    sel_set = set(st.session_state.get("selected_teams", []))

    df = pd.DataFrame({
        "Time": [f"{'★ ' if t in sel_set else ''}{flag(t)} {t}" for t in teams_sorted],
        "%":    [round(probs[t] * 100, 1) for t in teams_sorted],
    })

    ev = st.dataframe(
        df,
        column_config={
            "Time": st.column_config.TextColumn(),
            "%": st.column_config.ProgressColumn(
                format="%.1f%%",
                min_value=0,
                max_value=df["%"].max(),
            ),
        },
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="prob_panel",
        height=min(len(teams_sorted) * 35 + 38, 720),
    )

    if ev.selection.rows:
        st.session_state.sel_team = teams_sorted[ev.selection.rows[0]]

    st.caption("↑ Clique em uma linha para ver a decomposição da probabilidade")


def team_breakdown(node: Node, team: str) -> None:
    """
    Explica como `team` acumula sua probabilidade neste nó.

    Fórmula por adversário Y:
        P(chegar) × P(Y chegar pelo outro lado) × P(team vence Y) = contribuição
    """
    left_set = set(node.left.all_teams())   # type: ignore[union-attr]
    if team in left_set:
        my_node, opp_node = node.left, node.right
    else:
        my_node, opp_node = node.right, node.left  # type: ignore[union-attr]

    my_probs  = _side_probs(my_node)
    opp_probs = _side_probs(opp_node)

    p_reach = my_probs[team]
    p_total = ALL_PROBS[node.label][team]

    # ── métricas de cabeçalho ────────────────────────────────────
    c1, c2 = st.columns(2)
    c1.metric("P(chegar a esta fase)", f"{p_reach:.1%}")
    c2.metric("P(vencer a fase)", f"{p_total:.1%}",
              delta=f"{(p_total/p_reach*100):.0f}% se chegar" if p_reach > 0 else "")

    st.caption(
        f"**{flag(team)} {team}** (ELO {ELO[team]:.0f}) — "
        f"total = P(chegar) × Σ [ P(adversário chegar) × P(vencer duelo) ]"
    )

    # ── dados por adversário possível ────────────────────────────
    opps = sorted(opp_probs, key=lambda t: -opp_probs[t])
    rows = []
    for opp in opps:
        p_opp   = opp_probs[opp]
        p_win   = win_prob(ELO[team], ELO[opp])
        p_duelo = p_reach * p_opp          # P(este duelo acontecer)
        contrib = p_duelo * p_win          # contribuição ao total
        rows.append(dict(
            opp=opp, p_opp=p_opp, p_win=p_win, p_duelo=p_duelo, contrib=contrib,
        ))

    # ── gráfico de barras empilhadas por adversário ──────────────
    opp_labels  = [f"{flag(r['opp'])} {r['opp']}" for r in rows]
    contribs    = [r["contrib"] * 100 for r in rows]
    hover_texts = [
        f"<b>vs {flag(r['opp'])} {r['opp']}</b> (ELO {ELO[r['opp']]:.0f})<br>"
        f"P(duelo acontecer) = {r['p_duelo']*100:.1f}%"
        f"  =  P({team} chega {p_reach*100:.1f}%) × P({r['opp']} chega {r['p_opp']*100:.1f}%)<br>"
        f"P({team} vence o duelo) = {r['p_win']*100:.0f}%<br>"
        f"<b>Contribuição = {r['contrib']*100:.1f}%</b>"
        for r in rows
    ]

    fig = go.Figure(go.Bar(
        x=opp_labels,
        y=contribs,
        marker=dict(
            color=[r["p_win"] for r in rows],
            colorscale="RdYlGn",
            cmin=0, cmax=1,
            showscale=True,
            colorbar=dict(title="P(vence<br>duelo)", tickformat=".0%"),
        ),
        text=[f"{v:.1f}%" for v in contribs],
        textposition="outside",
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hover_texts,
    ))
    # linha do total
    fig.add_hline(
        y=p_total * 100,
        line_dash="dash", line_color="gold", line_width=2,
        annotation_text=f"  Total: {p_total:.1%}",
        annotation_font_color="gold",
        annotation_position="top right",
    )
    fig.update_layout(
        title=dict(
            text=f"Como {flag(team)} {team} acumula {p_total:.1%}<br>"
                 f"<sup>Cada barra = contribuição de um possível adversário  "
                 f"(cor = P({team} vence o duelo direto)</sup>",
            font_size=13,
        ),
        xaxis=dict(title="Possível adversário", tickangle=-20, tickfont=dict(size=10)),
        yaxis=dict(title="Contribuição (%)", range=[0, max(contribs) * 1.3]),
        height=420,
        margin=dict(l=10, r=80, t=90, b=80),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        showlegend=False,
    )
    st.plotly_chart(fig, key="team_breakdown_chart")

    # ── tabela detalhada ─────────────────────────────────────────
    with st.expander("Ver tabela completa"):
        df_detail = pd.DataFrame([{
            "Adversário":        f"{flag(r['opp'])} {r['opp']}",
            "ELO adv.":          f"{ELO[r['opp']]:.0f}",
            "P(adv. chega)":     f"{r['p_opp']*100:.1f}%",
            "P(duelo acontece)": f"{r['p_duelo']*100:.1f}%",
            f"P({team} vence)":  f"{r['p_win']*100:.0f}%",
            "Contribuição":      f"{r['contrib']*100:.1f}%",
        } for r in rows])
        st.dataframe(df_detail, hide_index=True)


# ─────────────────────────────────────────────────────────────────
# STREAMLIT APP
# ─────────────────────────────────────────────────────────────────
if "sel"                 not in st.session_state:
    st.session_state.sel                 = final.label
if "sel_team"            not in st.session_state:
    st.session_state.sel_team            = None
if "selected_teams"      not in st.session_state:
    st.session_state.selected_teams      = []
if "_sidebar_gen"        not in st.session_state:
    st.session_state._sidebar_gen        = 0
if "_prev_sidebar_rows"  not in st.session_state:
    st.session_state._prev_sidebar_rows  = []

# ── Sidebar PRIMEIRO: atualiza selected_teams antes do conteúdo principal ──
with st.sidebar:
    st.header("Rankings FIFA (ELO)")
    st.caption("Clique nas linhas para adicionar/remover da comparação")
    sel_set = set(st.session_state.selected_teams)
    elo_df = pd.DataFrame({
        "#":       range(1, len(ELO_SORTED) + 1),
        "Seleção": [f"{'★ ' if t in sel_set else ''}{flag(t)} {t}" for t, _ in ELO_SORTED],
        "Pts":     [round(pts) for _, pts in ELO_SORTED],
    })
    ev_rank = st.dataframe(
        elo_df,
        column_config={"#": st.column_config.NumberColumn(width=40)},
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row",
        key=f"ranking_sel_{st.session_state._sidebar_gen}",
        height=700,
    )
    curr_rows = set(ev_rank.selection.rows if ev_rank and ev_rank.selection else [])
    prev_rows = set(st.session_state._prev_sidebar_rows)
    if curr_rows != prev_rows:
        st.session_state._prev_sidebar_rows = list(curr_rows)
        added   = curr_rows - prev_rows
        removed = prev_rows - curr_rows
        teams   = set(st.session_state.selected_teams)
        if added and removed:
            # clique simples substituiu a seleção visual: só toggling o item clicado
            team_clicked = ELO_SORTED[next(iter(added))][0]
            if team_clicked in teams:
                teams.discard(team_clicked)
            else:
                teams.add(team_clicked)
        else:
            teams |= {ELO_SORTED[i][0] for i in added}
            teams -= {ELO_SORTED[i][0] for i in removed}
        st.session_state.selected_teams = list(teams)

    st.divider()
    st.markdown("#### Como é calculada a probabilidade?")
    st.markdown(
        "Os pontos do **Ranking FIFA** seguem o modelo **ELO** — quanto maior a pontuação, "
        "mais forte a seleção. A probabilidade de vitória num confronto direto é calculada "
        "pela função logística:"
    )
    st.markdown(
        """
<div style="text-align:center;padding:14px 8px;margin:8px 0;
            background:rgba(255,255,255,0.05);border-radius:10px;
            font-family:Georgia,'Times New Roman',serif;font-size:1.05em;line-height:1.6;">
  <span>P(A&nbsp;vence&nbsp;B)&nbsp;&nbsp;=&nbsp;&nbsp;</span>
  <span style="display:inline-block;vertical-align:middle;text-align:center;">
    <span style="display:block;border-bottom:1px solid rgba(255,255,255,0.7);
                 padding:0 6px 3px;font-size:1.05em;">1</span>
    <span style="display:block;padding:3px 6px 0;">
      1&nbsp;+&nbsp;10<sup style="font-size:0.72em;line-height:1;">
        &thinsp;(ELO<sub>B</sub>&nbsp;&minus;&nbsp;ELO<sub>A</sub>)&nbsp;/&nbsp;400
      </sup>
    </span>
  </span>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        "- Se as duas seleções têm **ELO igual**, P = 50%  \n"
        "- Uma diferença de **+400 pts** dá ≈ 91% de chance ao favorito  \n"
        "- Uma diferença de **+100 pts** dá ≈ 64%  \n\n"
        "Para fases com múltiplos jogos (oitavas, quartas…), a probabilidade de "
        "**vencer a fase** é calculada recursivamente: cada seleção precisa primeiro "
        "chegar ao jogo e depois vencer todos os possíveis adversários ponderados "
        "pela chance de cada um também chegar."
    )

# ── Conteúdo principal ────────────────────────────────────────────
st.markdown(
    "<h2 style='margin-bottom:0'>🏆 Copa do Mundo 2026 — Simulador ELO</h2>"
    "<p style='color:gray;margin-top:2px'>"
    "① Clique em uma partida no bracket · "
    "② Clique em uma seleção no painel direito para ver a decomposição"
    "</p>",
    unsafe_allow_html=True,
)

col_b, col_p = st.columns([3, 1], gap="small")

with col_b:
    fig_bracket = build_bracket(st.session_state.sel)
    ev_bracket = st.plotly_chart(
        fig_bracket,
        on_select="rerun",
        selection_mode="points",
        key="bracket_chart",
    )
    if ev_bracket and ev_bracket.selection and ev_bracket.selection.points:
        clicked_label = ev_bracket.selection.points[0].get("customdata")
        if clicked_label and clicked_label in NODE_BY_LABEL:
            if clicked_label != st.session_state.sel:
                st.session_state.sel      = clicked_label
                st.session_state.sel_team = None
                st.rerun()

with col_p:
    sel_node   = NODE_BY_LABEL[st.session_state.sel]
    probs_here = ALL_PROBS[sel_node.label]
    phase_teams = sel_node.all_teams()
    elo_names   = [t for t, _ in ELO_SORTED]
    active      = [t for t in st.session_state.selected_teams if t in probs_here]

    if active:
        soma = sum(probs_here[t] for t in active)
        label_n = "1 seleção" if len(active) == 1 else f"{len(active)} seleções"
        st.metric(f"Prob. combinada — {label_n}", f"{soma:.1%}")
        st.divider()

    if st.button(f"Selecionar todos ({len(phase_teams)}) no ranking"):
        st.session_state.selected_teams     = list(phase_teams)
        st.session_state._sidebar_gen      += 1
        st.session_state._prev_sidebar_rows = []
        st.rerun()

    st.markdown(f"**{sel_node.label}**")
    st.caption(f"{len(phase_teams)} seleções — clique numa para detalhar")
    prob_panel(sel_node)

# ── Painel de decomposição (largura total, abaixo do bracket) ────
st.divider()
sel_node = NODE_BY_LABEL[st.session_state.sel]
sel_team = st.session_state.get("sel_team")

if sel_team and sel_team in sel_node.all_teams():
    if sel_node.left and sel_node.left.is_team:
        ta, tb = sel_node.left.team, sel_node.right.team  # type: ignore[union-attr]
        p = win_prob(ELO[ta], ELO[tb])
        other  = tb if sel_team == ta else ta
        p_show = p  if sel_team == ta else 1 - p
        st.markdown(f"#### {flag(sel_team)} {sel_team} — confronto direto")
        c1, c2, c3 = st.columns(3)
        c1.metric(f"{flag(sel_team)} {sel_team}", f"ELO {ELO[sel_team]:.0f}")
        c2.metric("P(vence)", f"{p_show:.1%}")
        c3.metric(f"{flag(other)} {other}", f"ELO {ELO[other]:.0f}")
    else:
        st.markdown(
            f"#### {flag(sel_team)} {sel_team} — decomposição de "
            f"**{ALL_PROBS[sel_node.label][sel_team]:.1%}** em **{sel_node.label}**"
        )
        team_breakdown(sel_node, sel_team)
        st.caption(
            "Fórmula: P(total) = P(chegar) × Σᵧ [ P(Y chegar pelo outro lado) × P(vencer Y) ]  "
            "| Cor da barra = P(vencer o duelo direto contra Y)"
        )
else:
    st.caption("Selecione uma seleção no painel direito para ver a decomposição da probabilidade.")
