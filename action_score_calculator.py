import streamlit as st

st.set_page_config(page_title="Poker Action Score Calculator", page_icon="🎰", layout="centered")

# ---- Final step-up model: weights and per-game-type config ----
W_VPIP, W_PFR, W_RATIO = 0.50, 0.45, 0.05

CONFIG = {
    "NLH (Texas)": {"V": 31, "P": 21, "C1": 100, "C2": 117},
    "4PLO":        {"V": 42, "P": 21, "C1": 98,  "C2": 135},
    "5PLO":        {"V": 47, "P": 22, "C1": 98,  "C2": 138},
    "6PLO":        {"V": 57, "P": 26, "C1": 97,  "C2": 137},
}

# Approx VPIP/PFR needed to reach each tier (typical aggression ratio per game)
TIER_RANGES = {
    "NLH (Texas)": {"t2": (32, 21), "t3": (37, 25)},
    "4PLO":        {"t2": (42, 21), "t3": (59, 29)},
    "5PLO":        {"t2": (47, 22), "t3": (67, 31)},
    "6PLO":        {"t2": (57, 26), "t3": (81, 37)},
}

def compute_score(vpip, pfr, cfg):
    if vpip <= 0:
        return 0.0, 0.0, 0.0, 0.0
    vr = vpip / cfg["V"]
    pr = pfr / cfg["P"]
    ar = pfr / vpip
    score = (W_VPIP * vr + W_PFR * pr + W_RATIO * ar) * 100
    return score, vr, pr, ar

def tier_of(score, cfg):
    if score < cfg["C1"]:
        return 1, "Standard", 10, "🔵", "😐"
    elif score < cfg["C2"]:
        return 2, "Active", 15, "🟢", "🔥"
    else:
        return 3, "Action", 20, "🟡", "🚀"

st.title("🎰 Poker Action Score Calculator")
st.markdown("Rewards players for **stepping up their action** — playing more hands and raising more. "
            "Higher Action Score → higher rakeback tier.")
st.markdown("---")

with st.sidebar:
    st.header("📖 How It Works")
    st.markdown(f"""
    **Formula:**
    ```
    Score = [{W_VPIP:.2f} × (VPIP/V*)
          + {W_PFR:.2f} × (PFR/P*)
          + {W_RATIO:.2f} × (PFR/VPIP)] × 100
    ```

    **Weights** (tilted to volume so playing more hands raises the score):
    - {int(W_VPIP*100)}% — playing hands (VPIP)
    - {int(W_PFR*100)}% — raising (PFR)
    - {int(W_RATIO*100)}% — aggression ratio

    **Tiers → Rakeback:**
    - Tier 1 (Standard): 10%
    - Tier 2 (Active): 15%
    - Tier 3 (Action): 20%

    *VPIP & PFR are rake-weighted across all hands (higher-stake hands count more).*
    """)
    st.markdown("**Benchmarks by game:**")
    for g, c in CONFIG.items():
        st.markdown(f"- **{g}**: V*={c['V']}, P*={c['P']} · T2≥{c['C1']} · T3≥{c['C2']}")

st.subheader("📊 Player Stats")
col1, col2, col3 = st.columns(3)
with col1:
    game_type = st.selectbox("Game Type", list(CONFIG.keys()))
with col2:
    vpip = st.number_input("VPIP (%)", 0.0, 100.0, 30.0, 0.1,
                           help="Voluntarily Put $ In Pot (rake-weighted)")
with col3:
    pfr = st.number_input("PFR (%)", 0.0, 100.0, 21.0, 0.1,
                          help="Pre-Flop Raise (rake-weighted)")

if pfr > vpip:
    st.error("⚠️ PFR cannot be greater than VPIP. A player can't raise more hands than they play.")
    st.stop()

cfg = CONFIG[game_type]
score, vr, pr, ar = compute_score(vpip, pfr, cfg)
tier, tier_name, rakeback, tcolor, temoji = tier_of(score, cfg)

if vpip == 0:
    st.warning("⚠️ VPIP is 0 — player hasn't voluntarily played any hands. Defaulting to Tier 1.")

st.markdown("---")
st.subheader("🎯 Results")
a, b, c = st.columns(3)
with a:
    st.metric("Action Score", f"{score:.1f}")
with b:
    st.metric(f"Tier {tier} {temoji}", tier_name)
with c:
    st.metric("Rakeback", f"{rakeback}%",
              delta=f"+{rakeback-10}% bonus" if rakeback > 10 else "Base rate")

st.markdown(f"### {tcolor} **Tier {tier}: {tier_name}** — {rakeback}% Rakeback")

# Progress + how much more action to step up
if tier == 1:
    prog = min(score / cfg["C1"], 1.0) if cfg["C1"] else 1.0
    st.progress(prog)
    t2v, t2p = TIER_RANGES[game_type]["t2"]
    st.caption(f"📈 {cfg['C1']-score:.1f} pts to **Tier 2 (15%)** — around VPIP {t2v}, PFR {t2p} for this game.")
elif tier == 2:
    span = cfg["C2"] - cfg["C1"]
    prog = min((score - cfg["C1"]) / span, 1.0) if span else 1.0
    st.progress(prog)
    t3v, t3p = TIER_RANGES[game_type]["t3"]
    st.caption(f"📈 {cfg['C2']-score:.1f} pts to **Tier 3 (20%)** — around VPIP {t3v}, PFR {t3p} for this game.")
else:
    st.progress(1.0)
    st.caption("🏆 Top tier reached! Maximum action rakeback.")

# Score breakdown
st.markdown("---")
st.subheader("🔍 Score Breakdown")
with st.expander("See the math step-by-step", expanded=True):
    st.markdown(f"**Game:** {game_type}  ·  **Benchmarks:** V\\* = {cfg['V']}, P\\* = {cfg['P']}")
    st.markdown(f"**Cutoffs:** Tier 1 < {cfg['C1']} · Tier 2 {cfg['C1']}–{cfg['C2']} · Tier 3 ≥ {cfg['C2']}")
    st.table({
        "Component": ["1. Volume (VPIP)", "2. Aggression (PFR)", "3. Style (PFR/VPIP)", "Total"],
        "Calculation": [
            f"{W_VPIP:.2f} x ({vpip}/{cfg['V']}) = {W_VPIP:.2f} x {vr:.3f}",
            f"{W_PFR:.2f} x ({pfr}/{cfg['P']}) = {W_PFR:.2f} x {pr:.3f}",
            f"{W_RATIO:.2f} x ({pfr}/{vpip}) = {W_RATIO:.2f} x {ar:.3f}" if vpip > 0 else "0",
            "Sum x 100",
        ],
        "Contribution": [f"{W_VPIP*vr:.3f}", f"{W_PFR*pr:.3f}", f"{W_RATIO*ar:.3f}", f"{score:.1f}"],
    })

# Tier range reference for ALL games
st.markdown("---")
st.subheader("🪜 Tier Ranges by Game (step-up guide)")
st.caption("Approximate VPIP/PFR to reach each tier, assuming a typical aggression ratio for the game. "
           "The true rule is the score; these are the common path to it.")
rows_game, rows_t1, rows_t2, rows_t3 = [], [], [], []
for g, c in CONFIG.items():
    t2v, t2p = TIER_RANGES[g]["t2"]
    t3v, t3p = TIER_RANGES[g]["t3"]
    rows_game.append(g)
    rows_t1.append(f"VPIP < {t2v}")
    rows_t2.append(f"VPIP ~{t2v}-{t3v}, PFR ~{t2p}-{t3p}")
    rows_t3.append(f"VPIP {t3v}+, PFR {t3p}+")
st.table({
    "Game Type": rows_game,
    "Tier 1 (10%)": rows_t1,
    "Tier 2 (15%)": rows_t2,
    "Tier 3 (20%)": rows_t3,
})

# Player profile
st.markdown("---")
st.subheader("🎭 Player Profile")
v_star = cfg["V"]
if vpip < v_star * 0.8:
    arche = "🪨 **Tight / Below Benchmark**"
    desc = "Plays fewer hands than the benchmark for this game. Stepping up VPIP/PFR will lift the tier."
elif vpip < v_star * 1.2:
    arche = "🎯 **Around Benchmark**"
    desc = "Right around the typical active player for this game. A bit more action pushes into a higher tier."
elif ar > 0.55:
    arche = "🔥 **Loose-Aggressive (LAG)**"
    desc = "Plays wide and raises a lot. Great for action — likely a top-tier player."
else:
    arche = "🐟 **Loose-Passive**"
    desc = "Plays many hands but raises less. More raising would lift the score further."
st.markdown(arche)
st.markdown(desc)

st.markdown("---")
x, y, z = st.columns(3)
with x:
    st.caption("**VPIP vs Target**")
    st.markdown(f"{vpip}% / {cfg['V']}% = **{vr:.2f}x**")
with y:
    st.caption("**PFR vs Target**")
    st.markdown(f"{pfr}% / {cfg['P']}% = **{pr:.2f}x**")
with z:
    st.caption("**Aggression Ratio**")
    st.markdown(f"{pfr}% / {vpip}% = **{ar:.2f}**")

st.caption("💡 VPIP & PFR are rake-weighted across all hands in the period, so higher-stake hands "
           "contribute more — this neutralises low-stakes and heads-up stat-farming.")
