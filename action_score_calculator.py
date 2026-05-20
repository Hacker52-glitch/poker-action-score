import streamlit as st

st.set_page_config(page_title="Poker Action Score Calculator", page_icon="🎰", layout="centered")

st.title("🎰 Poker Action Score Calculator")
st.markdown("Calculate a player's **Action Score** and **Rakeback Tier** based on VPIP and PFR.")
st.markdown("---")

CONFIG = {
    "Texas Hold'em": {"V": 33, "P": 23, "C1": 99, "C2": 162},
    "PLO (Omaha)":   {"V": 45, "P": 26, "C1": 106, "C2": 167},
}

with st.sidebar:
    st.header("📖 How It Works")
    st.markdown("""
    **Formula:**
    ```
    Score = [0.40 × (VPIP/V*)
          + 0.45 × (PFR/P*)
          + 0.15 × (PFR/VPIP)] × 100
    ```

    **Benchmarks & Cutoffs:**
    - **Texas:** V*=33, P*=23
      Tier1 <99 · Tier2 99–162 · Tier3 ≥162
    - **PLO:** V*=45, P*=26
      Tier1 <106 · Tier2 106–167 · Tier3 ≥167

    **Tiers → Rakeback:**
    - Tier 1 (Standard): 10%
    - Tier 2 (Active): 15%
    - Tier 3 (Action): 20%

    *VPIP & PFR are rake-weighted across all hands (higher-stake hands count more).*
    """)

st.subheader("📊 Player Stats")

col1, col2, col3 = st.columns(3)
with col1:
    game_type = st.selectbox("Game Type", list(CONFIG.keys()),
                             help="Different games have different benchmarks")
with col2:
    vpip = st.number_input("VPIP (%)", min_value=0.0, max_value=100.0, value=33.0, step=0.1,
                           help="Voluntarily Put $ In Pot - rake-weighted")
with col3:
    pfr = st.number_input("PFR (%)", min_value=0.0, max_value=100.0, value=23.0, step=0.1,
                          help="Pre-Flop Raise - rake-weighted")

if pfr > vpip:
    st.error("⚠️ PFR cannot be greater than VPIP. A player can't raise more hands than they play.")
    st.stop()

cfg = CONFIG[game_type]
v_target, p_target, C1, C2 = cfg["V"], cfg["P"], cfg["C1"], cfg["C2"]

if vpip == 0:
    st.warning("⚠️ VPIP is 0. Player hasn't played any hands voluntarily.")
    score = 0.0
    vpip_ratio = pfr_ratio = aggression_ratio = 0.0
    vpip_component = pfr_component = ratio_component = 0.0
else:
    vpip_ratio = vpip / v_target
    pfr_ratio = pfr / p_target
    aggression_ratio = pfr / vpip
    vpip_component = 0.40 * vpip_ratio
    pfr_component = 0.45 * pfr_ratio
    ratio_component = 0.15 * aggression_ratio
    score = (vpip_component + pfr_component + ratio_component) * 100

if score < C1:
    tier, tier_name, rakeback, tier_color, tier_emoji = 1, "Standard", 10, "🔵", "😐"
elif score < C2:
    tier, tier_name, rakeback, tier_color, tier_emoji = 2, "Active", 15, "🟢", "🔥"
else:
    tier, tier_name, rakeback, tier_color, tier_emoji = 3, "Action", 20, "🟡", "🚀"

st.markdown("---")
st.subheader("🎯 Results")

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("Action Score", f"{score:.1f}")
with col_b:
    st.metric(f"Tier {tier} {tier_emoji}", tier_name)
with col_c:
    st.metric("Rakeback", f"{rakeback}%",
              delta=f"+{rakeback - 10}% bonus" if rakeback > 10 else "Base rate")

st.markdown(f"### {tier_color} **Tier {tier}: {tier_name}** — {rakeback}% Rakeback")

if tier == 1:
    progress = min(score / C1, 1.0) if C1 > 0 else 1.0
    st.progress(progress)
    st.caption(f"📈 {C1 - score:.1f} points to reach **Tier 2 (Active)** — 15% rakeback")
elif tier == 2:
    span = C2 - C1
    progress = min((score - C1) / span, 1.0) if span > 0 else 1.0
    st.progress(progress)
    st.caption(f"📈 {C2 - score:.1f} points to reach **Tier 3 (Action)** — 20% rakeback")
else:
    st.progress(1.0)
    st.caption("🏆 Maximum tier reached! Keep bringing the action!")

st.markdown("---")
st.subheader("🔍 Score Breakdown")
with st.expander("See the math step-by-step", expanded=True):
    st.markdown(f"**Game Type:** {game_type}")
    st.markdown(f"**Benchmarks:** V\\* = {v_target}, P\\* = {p_target}")
    st.markdown(f"**Cutoffs:** Tier 1 below {C1} · Tier 2 {C1}–{C2} · Tier 3 at/above {C2}")
    st.markdown("")
    st.table({
        "Component": ["1. Activity (VPIP)", "2. Aggression (PFR)",
                      "3. Style (PFR/VPIP)", "Total Score"],
        "Calculation": [
            f"0.40 x ({vpip}/{v_target}) = 0.40 x {vpip_ratio:.3f}",
            f"0.45 x ({pfr}/{p_target}) = 0.45 x {pfr_ratio:.3f}",
            f"0.15 x ({pfr}/{vpip}) = 0.15 x {aggression_ratio:.3f}" if vpip > 0 else "0.15 x 0",
            "Sum x 100",
        ],
        "Contribution": [f"{vpip_component:.3f}", f"{pfr_component:.3f}",
                         f"{ratio_component:.3f}", f"{score:.1f}"],
    })

st.markdown("---")
st.subheader("🎭 Player Profile")
loose_cut = 35 if game_type == "Texas Hold'em" else 50
mid_cut = 50 if game_type == "Texas Hold'em" else 65
if vpip < 20:
    archetype = "🪨 **The Rock / Nit**" if aggression_ratio > 0.7 else "🐌 **The Passive Nit**"
    description = ("Very tight, raises when playing. Predictable." if aggression_ratio > 0.7
                   else "Very tight and passive. Rarely raises.")
elif vpip < loose_cut:
    archetype = "🎯 **The TAG (Tight-Aggressive)**" if aggression_ratio > 0.6 else "📞 **The Tight Caller**"
    description = ("Solid, disciplined, aggressive when in. Standard winning style."
                   if aggression_ratio > 0.6 else "Tight but passive - calls more than raises.")
elif vpip < mid_cut:
    archetype = "🔥 **The LAG (Loose-Aggressive)**" if aggression_ratio > 0.6 else "🐟 **The Loose Passive**"
    description = ("Active and aggressive. Great for action!" if aggression_ratio > 0.6
                   else "Plays lots of hands but limps/calls - passive.")
else:
    archetype = "🚀 **The Maniac**" if aggression_ratio > 0.6 else "🌊 **The Whale**"
    description = ("Hyper-aggressive, tons of action." if aggression_ratio > 0.6
                   else "Plays everything, mostly passively.")
st.markdown(archetype)
st.markdown(description)

st.markdown("---")
col_x, col_y, col_z = st.columns(3)
with col_x:
    st.caption("**VPIP vs Target**")
    st.markdown(f"{vpip}% / {v_target}% = **{vpip_ratio:.2f}x**")
with col_y:
    st.caption("**PFR vs Target**")
    st.markdown(f"{pfr}% / {p_target}% = **{pfr_ratio:.2f}x**")
with col_z:
    st.caption("**Aggression Ratio**")
    st.markdown(f"{pfr}% / {vpip}% = **{aggression_ratio:.2f}**")

st.markdown("---")
with st.expander("📊 See all tier thresholds for this game"):
    st.table({
        "Tier": ["Tier 1 — Standard", "Tier 2 — Active", "Tier 3 — Action"],
        "Action Score": [f"< {C1}", f"{C1} – {C2}", f"≥ {C2}"],
        "Rakeback": ["10%", "15%", "20%"],
    })

st.caption("💡 VPIP & PFR are rake-weighted across all hands in the period, so higher-stake "
           "hands contribute more. A minimum-hands gate (e.g. 1,000 NLH / 1,500 PLO) defaults "
           "low-volume players to Tier 1.")
