"""Web Catcher: which trends should Vans chase?

A tool I built as a Product & Merchandising intern at Vans in Shanghai in 2024,
rebuilt in 2026. Read how hot a new footwear trend is, rate how close Vans'
three core shoes are to it, pull the launch levers and make the call.

The same rules run on senergunsel.com/projects/web-catcher/ in JavaScript, in
the same order, so both give the same numbers. Every number here is
illustrative: none of it is Vans data or anyone's real sales.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from webcatcher_model import (
    BUZZ_WORDS, CALLS, LEVEL_WORDS, LEVERS, LINE, MAX_TRENDS, SHOES, SIZE_WORDS, TRAITS, WINDOWS,
    clamp, coach, defaults, evaluate, line_note, momentum, new_trend, shoe_name,
)

# ---------------------------------------------------------------- The page

ACCENT, INK, INK2, MUTED, HAIR, SURFACE = "#FF4F00", "#121211", "#4A4A45", "#66665F", "#D6D6D0", "#FBFBFA"

st.set_page_config(page_title="Web Catcher · Which trends should Vans chase?", page_icon="👟", layout="wide")

ss = st.session_state
if "trends" not in ss:
    ss.trends = defaults()
    ss.sel = "samba"
    ss.made = 0
    ss.gen = 0  # bumps on Start over so every widget starts fresh


def cur():
    return next(t for t in ss.trends if t["key"] == ss.sel)


def wkey(name, t):
    return f"{name}_{t['key']}_{ss.gen}"


def add_trend():
    if len(ss.trends) >= MAX_TRENDS:
        return
    ss.made += 1
    t = new_trend(ss.made)
    ss.trends.append(t)
    ss.sel = t["key"]
    ss[f"pick_{ss.gen}"] = t["key"]


def remove_trend():
    i = next(i for i, t in enumerate(ss.trends) if t["key"] == ss.sel)
    if ss.trends[i]["custom"]:
        ss.trends.pop(i)
        ss.sel = ss.trends[max(0, i - 1)]["key"]
        ss[f"pick_{ss.gen}"] = ss.sel


def rename(key, widget):
    t = next(x for x in ss.trends if x["key"] == key)
    t["name"] = (ss[widget] or "").strip() or "Your trend"


def relook(key, widget):
    t = next(x for x in ss.trends if x["key"] == key)
    t["look"] = (ss[widget] or "").strip()


def start_over():
    ss.trends = defaults()
    ss.sel = "samba"
    ss.made = 0
    ss.gen += 1


st.title("Which trends should Vans chase?")
st.markdown(
    "**Web Catcher** is a tool I built at Vans in 2024. When a competitor's shoe takes off, a brand has to decide fast: "
    "answer it with one of its own shoes, or let it pass. Read how hot a trend is, rate how close Vans' three core shoes are "
    "to it, and test what backing it would take."
)
st.caption("Every number is illustrative: the signals, the ratings and the calls are mine, and none of them is Vans data or anyone's real sales. "
           "The same rules run on [senergunsel.com](https://senergunsel.com/projects/web-catcher/).")

# Step 1: read the trend
st.header("1 · Read the trend", divider="orange")
pick = st.segmented_control(
    "Trend", [t["key"] for t in ss.trends], default=None if f"pick_{ss.gen}" in ss else ss.sel, required=True, key=f"pick_{ss.gen}",
    format_func=lambda k: next(t["name"] for t in ss.trends if t["key"] == k),
)
if pick and pick != ss.sel:
    ss.sel = pick
t = cur()

a, b = st.columns([1, 1], gap="large")
with a:
    if t["custom"]:
        st.text_input("Name your trend", value=t["name"], max_chars=28, key=wkey("name", t),
                      on_change=rename, args=(t["key"], wkey("name", t)))
        st.text_input("What it looks like", value=t["look"], max_chars=60, key=wkey("look", t), placeholder="One line, optional",
                      on_change=relook, args=(t["key"], wkey("look", t)))
    st.subheader(t["name"])
    if t["look"]:
        st.write(t["look"])
    mom_slot = st.empty()  # filled once the signals on the right are read
    bc1, bc2 = st.columns(2)
    bc1.button("Add a trend of your own", on_click=add_trend, disabled=len(ss.trends) >= MAX_TRENDS)
    if t["custom"]:
        bc2.button("Remove it", on_click=remove_trend)
with b:
    t["growth"] = st.slider("Growth over the last year (%)", -50, 50, t["growth"], 5, format="%+d%%", key=wkey("growth", t),
                            help="Sales against the year before. Counts for half of momentum.")
    t["buzz"] = st.select_slider("Buzz", options=[1, 2, 3, 4, 5], value=t["buzz"], format_func=lambda v: BUZZ_WORDS[v - 1],
                                 key=wkey("buzz", t), help="What people say about it. Counts for 30%.")
    t["size"] = st.select_slider("Size", options=[1, 2, 3, 4, 5], value=t["size"], format_func=lambda v: SIZE_WORDS[v - 1],
                                 key=wkey("size", t), help="How many people already buy it. Counts for 20%.")
    t["window"] = st.segmented_control("How long it should last", list(WINDOWS), default=t["window"], required=True,
                                       format_func=lambda k: WINDOWS[k]["name"], key=wkey("window", t)) or t["window"]
    st.caption(WINDOWS[t["window"]]["note"])

mom, parts = momentum(t)
with mom_slot.container(border=True):
    st.metric("Momentum, out of 100", mom, help="Growth counts for half, buzz for 30% and size for 20%, each scored 0 to 100 first.")
    st.caption(f"Growth {parts['growth']:g} · Buzz {parts['buzz']:g} · Size {parts['size']:g}. "
               f"{'Hot' if mom >= LINE else 'Not hot'}: {line_note(mom)}.")

# Step 2: try it on our shoes
st.header("2 · Try it on our shoes", divider="orange")
st.write("Rate how close each core shoe is to the trend on six traits, from 1 (far off) to 5 (right on it). The closest shoe is the one Vans would answer it with.")
ekey = wkey("ratings", t)
if ekey + "_src" not in ss:
    ss[ekey + "_src"] = pd.DataFrame(
        [{"Trait": tr["name"], "Question": tr["q"], **{s["name"]: t["ratings"][s["key"]][tr["key"]] for s in SHOES}} for tr in TRAITS]
    )
edited = st.data_editor(
    ss[ekey + "_src"], key=ekey, hide_index=True, num_rows="fixed", disabled=["Trait", "Question"],
    column_config={s["name"]: st.column_config.NumberColumn(s["name"], min_value=1, max_value=5, step=1, format="%d", required=True) for s in SHOES},
)
for i, tr in enumerate(TRAITS):
    for s in SHOES:
        v = edited.iloc[i][s["name"]]
        if pd.notna(v):
            t["ratings"][s["key"]][tr["key"]] = int(clamp(int(v), 1, 5))

# Step 3: back it, or not
st.header("3 · Back it, or not", divider="orange")
st.write("Each lever step moves the ratings it touches by half a point. Nothing changes a shoe's shape quickly, and product work only counts if it lands before the trend ends.")
lc, vc = st.columns([1, 1.4], gap="large")
with lc:
    for lv in LEVERS:
        t["levers"][lv["key"]] = st.select_slider(lv["name"], options=[1, 2, 3, 4, 5], value=t["levers"][lv["key"]],
                                                  format_func=lambda v: LEVEL_WORDS[v - 1], key=wkey("lever_" + lv["key"], t))
        note = lv["note"]
        if lv["key"] == "product" and WINDOWS[t["window"]]["product"] == 0:
            note = "This trend won't last long enough for new product to land, so this lever does nothing."
        st.caption(note)

e = evaluate(t)
ev = {x["key"]: evaluate(x) for x in ss.trends}
with vc:
    with st.container(border=True):
        st.caption(f"THE CALL FOR THE {t['name'].upper()}")
        color = {"back": ACCENT, "test": INK, "hold": INK, "pass": MUTED}[e["call"]]
        st.markdown(f"<p style='font-size:52px;font-weight:800;line-height:1;margin:0 0 8px;color:{color}'>{CALLS[e['call']]}</p>", unsafe_allow_html=True)
        st.write(e["play"])
        m1, m2 = st.columns(2)
        m1.metric("Momentum", e["momentum"], help=line_note(e["momentum"]))
        m2.metric("Best fit", e["fit"], delta=(e["fit"] - e["base_fit"]) or None, help=f"{shoe_name(e['shoe'])}, {line_note(e['fit'])}")
        st.caption(f"Momentum is {line_note(e['momentum'])}. The {shoe_name(e['shoe'])} is the closest shoe, {line_note(e['fit'])}. "
                   f"Lasts {WINDOWS[t['window']]['name'].lower()}. Bet: {e['bet'].lower()}.")
        if e["base_call"] != e["call"]:
            st.caption(f"Before the levers: {CALLS[e['base_call']]}.")
        st.caption(coach(t))

cols = st.columns(len(SHOES))
for c, s in zip(cols, SHOES):
    f = e["fits"][s["key"]]
    c.metric(s["name"] + (" · closest" if s["key"] == e["shoe"] else ""), f["now"],
             delta=(f["now"] - f["base"]) or None, help=s["look"], border=True)

# Step 4: the whole wall
st.header("4 · The whole wall", divider="orange")
st.write("Every trend on one chart. Higher is hotter, further right is closer to one of our shoes, and the corner a trend lands in is its call. Hollow dots are before the levers.")
fig = go.Figure()
fig.add_shape(type="rect", x0=LINE, x1=100, y0=LINE, y1=100, fillcolor="rgba(255,79,0,0.11)", line_width=0, layer="below")
fig.add_shape(type="rect", x0=0, x1=LINE, y0=LINE, y1=100, fillcolor="rgba(255,79,0,0.04)", line_width=0, layer="below")
for v in (LINE,):
    fig.add_shape(type="line", x0=v, x1=v, y0=0, y1=100, line=dict(color=INK2, width=1.2, dash="dash"))
    fig.add_shape(type="line", x0=0, x1=100, y0=v, y1=v, line=dict(color=INK2, width=1.2, dash="dash"))
for text, x, y, xa, ya, col in (("BACK IT", 98, 97, "right", "top", "#B33800"), ("TEST SMALL", 2, 97, "left", "top", MUTED),
                                ("HOLD", 98, 3, "right", "bottom", MUTED), ("PASS", 2, 3, "left", "bottom", MUTED)):
    fig.add_annotation(x=x, y=y, text=f"<b>{text}</b>", showarrow=False, xanchor=xa, yanchor=ya, font=dict(family="monospace", size=12, color=col))
spots = {"samba": "middle right", "af1": "middle left", "stansmith": "middle right", "nb993": "middle right", "dunk": "middle left"}
for x in ss.trends:
    r = ev[x["key"]]
    if r["base_fit"] != r["fit"]:
        fig.add_annotation(x=r["fit"], y=r["momentum"], ax=r["base_fit"], ay=r["momentum"], xref="x", yref="y", axref="x", ayref="y",
                           showarrow=True, arrowhead=2, arrowsize=1.1, arrowwidth=1.5, arrowcolor="#B33800", text="", standoff=7)
        fig.add_trace(go.Scatter(x=[r["base_fit"]], y=[r["momentum"]], mode="markers", hoverinfo="skip", showlegend=False,
                                 marker=dict(size=10, color=SURFACE, line=dict(color=MUTED, width=1.5))))
    sel = x["key"] == ss.sel
    fig.add_trace(go.Scatter(
        x=[r["fit"]], y=[r["momentum"]], mode="markers+text", text=[x["name"]], textposition=spots.get(x["key"], "top center"),
        textfont=dict(size=13, color="#B33800" if sel else INK), showlegend=False,
        marker=dict(size=15 if sel else 11, color={"back": ACCENT, "pass": MUTED}.get(r["call"], INK), line=dict(color=ACCENT if sel else SURFACE, width=3 if sel else 2)),
        hovertemplate=f"<b>{x['name']}</b><br>{CALLS[r['call']]} · {WINDOWS[x['window']]['name']}<br>Momentum {r['momentum']} · fit {r['fit']} with the {shoe_name(r['shoe'])}<extra></extra>",
    ))
fig.update_layout(height=540, margin=dict(l=70, r=20, t=20, b=64), plot_bgcolor="white", paper_bgcolor="white",
                  font=dict(color=INK2), hoverlabel=dict(bgcolor="white", font_color=INK))
fig.update_xaxes(range=[0, 100], dtick=25, title="Fit: how close our best shoe is", gridcolor=HAIR, zeroline=False, showline=True, linecolor=MUTED)
fig.update_yaxes(range=[0, 100], dtick=25, title="Momentum: how hot the trend is", gridcolor=HAIR, zeroline=False, showline=True, linecolor=MUTED)
st.plotly_chart(fig, theme=None, config={"displayModeBar": False})

with st.expander("See the numbers"):
    st.dataframe(pd.DataFrame([
        {"Trend": x["name"], "Momentum": ev[x["key"]]["momentum"], "Lasts": WINDOWS[x["window"]]["name"],
         **{s["name"]: ev[x["key"]]["fits"][s["key"]]["now"] for s in SHOES},
         "Best shoe": shoe_name(ev[x["key"]]["shoe"]), "Call": CALLS[ev[x["key"]]["call"]]}
        for x in ss.trends
    ]), hide_index=True)

st.divider()
f1, f2 = st.columns([3, 1])
f1.caption("Momentum: growth counts for half, buzz for 30% and size for 20%, each scored 0 to 100 first. Fit: the average of a shoe's six ratings on the same scale. "
           "Both need 50 to count as high. Built with Python, Streamlit, Plotly and pandas.")
f2.button("Start over", on_click=start_over)
