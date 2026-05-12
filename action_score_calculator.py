import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Poker Action Score Calculator",
    page_icon="🎰",
    layout="centered"
)

# Title and description
st.title("🎰 Poker Action Score Calculator")
st.markdown("Calculate a player's **Action Score** and **Rakeback Tier** based on VPIP and PFR.")
st.markdown("---")

# Sidebar with formula explanation
with st.sidebar:
    st.header("📖 How It Works")
    st.markdown("""
    **Formula:**
    ```
    Score = [0.40 × (VPIP/V*) 
          + 0.45 × (PFR/P*) 
          + 0.15 × (PFR/VPIP)] × 100
    ```
    
    **Benchmarks:**
    - **Texas:** V* = 25, P* = 18
    - **PLO:** V* = 35, P* = 22
    
    **Weights:**
    - 40% — Playing hands (volume)
    - 45% — Raising (aggression)
    - 15% — Aggression ratio (style)
    
    **Tiers:**
    - **Tier 1 (Standard):** 0–70 → 10%
    - **Tier 2 (Active):** 70–110 → 15%
    - **Tier 3 (Action):** 110+ → 20%
    """)

# Input section
st.subheader("📊 Player Stats")

col1, col2, col3 = st.columns(3)

with col1:
    game_type = st.selectbox(
        "Game Type",
        ["Texas Hold'em", "PLO (Omaha)"],
        help="Different games have different benchmarks"
    )

with col2:
    vpip = st.number_input(
        "VPIP (%)",
        min_value=0.0,
        max_value=100.0,
        value=24.0,
        step=0.1,
        help="Voluntarily Put $ In Pot - how often the player plays a hand"
    )

with col3:
    pfr = st.number_input(
        "PFR (%)",
        min_value=0.0,
        max_value=100.0,
        value=19.0,
        step=0.1,
        help="Pre-Flop Raise - how often the player raises pre-flop"
    )

# Validation
if pfr > vpip:
    st.error("⚠️ PFR cannot be greater than VPIP. A player can't raise more hands than they play.")
    st.stop()

# Set benchmarks based on game type
if game_type == "Texas Hold'em":
    v_target = 25
    p_target = 18
else:
    v_target = 35
    p_target = 22

# Calculate score components
if vpip == 0:
    st.warning("⚠️ VPIP is 0. Player hasn't played any hands voluntarily.")
    score = 0
    vpip_component = 0
    pfr_component = 0
    ratio_component = 0
    vpip_ratio = 0
    pfr_ratio = 0
    aggression_ratio = 0
else:
    vpip_ratio = vpip / v_target
    pfr_ratio = pfr / p_target
    aggression_ratio = pfr / vpip
    
    vpip_component = 0.40 * vpip_ratio
    pfr_component = 0.45 * pfr_ratio
    ratio_component = 0.15 * aggression_ratio
    
    score = (vpip_component + pfr_component + ratio_component) * 100

# Determine tier
if score < 70:
    tier = 1
    tier_name = "Standard"
    rakeback = 10
    tier_color = "🔵"
    tier_emoji = "😐"
elif score < 110:
    tier = 2
    tier_name = "Active"
    rakeback = 15
    tier_color = "🟢"
    tier_emoji = "🔥"
else:
    tier = 3
    tier_name = "Action"
    rakeback = 20
    tier_color = "🟡"
    tier_emoji = "🚀"

# Results section
st.markdown("---")
st.subheader("🎯 Results")

# Main score display
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.metric(
        label="Action Score",
        value=f"{score:.1f}",
        help="Higher score = more action = better rakeback"
    )

with col_b:
    st.metric(
        label=f"Tier {tier} {tier_emoji}",
        value=tier_name,
        help=f"Tier {tier} out of 3"
    )

with col_c:
    st.metric(
        label="Rakeback",
        value=f"{rakeback}%",
        delta=f"+{rakeback - 10}% bonus" if rakeback > 10 else "Base rate"
    )

# Visual tier indicator
st.markdown(f"### {tier_color} **Tier {tier}: {tier_name}** — {rakeback}% Rakeback")

# Progress bar to next tier
if tier == 1:
    progress = min(score / 70, 1.0)
    st.progress(progress)
    st.caption(f"📈 {70 - score:.1f} points to reach **Tier 2 (Active)** — 15% rakeback")
elif tier == 2:
    progress = min((score - 70) / 40, 1.0)
    st.progress(progress)
    st.caption(f"📈 {110 - score:.1f} points to reach **Tier 3 (Action)** — 20% rakeback")
else:
    st.progress(1.0)
    st.caption("🏆 Maximum tier reached! Keep bringing the action!")

# Detailed breakdown
st.markdown("---")
st.subheader("🔍 Score Breakdown")

with st.expander("See the math step-by-step", expanded=True):
    st.markdown(f"**Game Type:** {game_type}")
    st.markdown(f"**Benchmarks:** V\\* = {v_target}, P\\* = {p_target}")
    st.markdown("")
    
    breakdown_data = {
        "Component": [
            "1️⃣ Activity (VPIP)",
            "2️⃣ Aggression (PFR)",
            "3️⃣ Style (PFR/VPIP ratio)",
            "**Total Score**"
        ],
        "Calculation": [
            f"0.40 × ({vpip}/{v_target}) = 0.40 × {vpip_ratio:.3f}",
            f"0.45 × ({pfr}/{p_target}) = 0.45 × {pfr_ratio:.3f}",
            f"0.15 × ({pfr}/{vpip}) = 0.15 × {aggression_ratio:.3f}" if vpip > 0 else "0.15 × 0",
            "Sum × 100"
        ],
        "Contribution": [
            f"{vpip_component:.3f}",
            f"{pfr_component:.3f}",
            f"{ratio_component:.3f}",
            f"**{score:.1f}**"
        ]
    }
    
    st.table(breakdown_data)

# Player profile interpretation
st.markdown("---")
st.subheader("🎭 Player Profile")

# Determine player archetype
if vpip < 15:
    if aggression_ratio > 0.7:
        archetype = "🪨 **The Rock / Nit**"
        description = "Very tight player. Plays few hands but raises when they do. Predictable but not exploitable."
    else:
        archetype = "🐌 **The Passive Nit**"
        description = "Very tight and passive. Plays few hands and rarely raises. Easy to play against."
elif vpip < 25 if game_type == "Texas Hold'em" else vpip < 30:
    if aggression_ratio > 0.75:
        archetype = "🎯 **The TAG (Tight-Aggressive)**"
        description = "Solid, disciplined player. Plays selectively but aggressively. Standard winning style."
    else:
        archetype = "📞 **The Tight Caller**"
        description = "Tight but passive. Plays cautiously and calls more than raises."
elif vpip < 35 if game_type == "Texas Hold'em" else vpip < 45:
    if aggression_ratio > 0.75:
        archetype = "🔥 **The LAG (Loose-Aggressive)**"
        description = "Active and aggressive. Creates lots of action. Ideal player for the ecosystem!"
    else:
        archetype = "🐟 **The Loose Passive (Calling Station)**"
        description = "Plays lots of hands but rarely raises. Limps and calls — passive style."
else:
    if aggression_ratio > 0.75:
        archetype = "🚀 **The Maniac**"
        description = "Hyper-aggressive! Plays tons of hands and raises constantly. Creates massive action."
    else:
        archetype = "🌊 **The Whale**"
        description = "Plays everything but mostly passively. Massive contributor to the pot."

st.markdown(f"{archetype}")
st.markdown(description)

# Footer with key stats
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

# Tier comparison table
st.markdown("---")
with st.expander("📊 See all tier thresholds"):
    tier_table = {
        "Tier": ["Tier 1 — Standard", "Tier 2 — Active", "Tier 3 — Action"],
        "Action Score": ["0 – 70", "70 – 110", "110+"],
        "Multiplier": ["1.0×", "1.5×", "2.0×"],
        "Rakeback": ["10%", "15%", "20%"],
        "Player Type": ["Nits, tight regs", "Solid TAGs, active players", "LAGs, maniacs, action players"]
    }
    st.table(tier_table)

st.caption("💡 *Note: This calculator shows the score for given VPIP/PFR inputs. In production, VPIP and PFR are rake-weighted across all hands in a 7-day window, so higher-stake hands contribute more to the final score.*")
