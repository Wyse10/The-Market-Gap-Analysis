import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------
st.set_page_config(
    page_title="The Sugar Trap | Market Gap Analysis",
    page_icon="🍫",
    layout="wide",
)

SUGAR_THRESHOLD = 10     # g / 100g  -> "Low Sugar" cutoff used in the underlying analysis
PROTEIN_THRESHOLD = 45   # g / 100g  -> "High Protein" cutoff used in the underlying analysis

QUADRANT_COLORS = {
    "Blue Ocean (High Protein, Low Sugar)": "#2563eb",
    "Red Ocean (Low Protein, High Sugar)": "#dc2626",
    "High Protein & High Sugar": "#f59e0b",
    "Low Protein & Low Sugar": "#94a3b8",
}

PROTEIN_SOURCES = {
    "Peanuts": ["peanut", "peanuts"],
    "Almonds": ["almond", "almonds"],
    "Whey": ["whey"],
    "Soy Protein": ["soy", "soy protein", "soya protein", "soja protein"],
    "Pea Protein": ["pea protein"],
    "Milk Protein / Casein": ["milk protein", "casein", "lait"],  # 'lait' is French for milk
    "Egg": ["egg white", "egg protein", "egg powder"],
    "Cheese": ["cheese"],
    "Protein Isolate (General)": ["isolate"],  # catches general protein isolates
    "Wheat Protein": ["wheat protein", "wheat gluten"],
}


# ------------------------------------------------------------------
# Data loading
# ------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_snacks.csv")
    return df


@st.cache_data
def top_protein_sources(ingredients_series: pd.Series, n=3):
    from collections import Counter
    counts = Counter()
    texts = ingredients_series.dropna().str.lower()
    for text in texts:
        for label, kws in PROTEIN_SOURCES.items():
            if any(kw in text for kw in kws):
                counts[label] += 1
                break  # count once per product, priority order
    total = len(texts) if len(texts) else 1
    ranked = counts.most_common(n)
    return [(label, count, count / total * 100) for label, count in ranked]


df = load_data()

# ------------------------------------------------------------------
# Header
# ------------------------------------------------------------------
st.title("🍫 The Sugar Trap: Where's the Blue Ocean in the Snack Aisle?")
st.caption(
    "Market gap analysis for Helix CPG Partners — built on Open Food Facts data. "
    f"Blue Ocean = High Protein (≥{PROTEIN_THRESHOLD}g/100g) & Low Sugar (<{SUGAR_THRESHOLD}g/100g)."
)

# ------------------------------------------------------------------
# Sidebar filters
# ------------------------------------------------------------------
st.sidebar.header("Filters")
all_categories = sorted(df["primary_category"].unique())
selected_categories = st.sidebar.multiselect(
    "Primary Category", options=all_categories, default=all_categories
)

sugar_range = st.sidebar.slider(
    "Sugar range (g/100g)",
    float(df["sugars_100g"].min()),
    float(df["sugars_100g"].max()),
    (float(df["sugars_100g"].min()), float(df["sugars_100g"].max())),
)
protein_range = st.sidebar.slider(
    "Protein range (g/100g)",
    float(df["proteins_100g"].min()),
    float(df["proteins_100g"].max()),
    (float(df["proteins_100g"].min()), float(df["proteins_100g"].max())),
)

filtered = df[
    df["primary_category"].isin(selected_categories)
    & df["sugars_100g"].between(*sugar_range)
    & df["proteins_100g"].between(*protein_range)
]

st.sidebar.markdown(f"**{len(filtered):,}** products match your filters")

# ------------------------------------------------------------------
# Top KPI row
# ------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Products analyzed", f"{len(filtered):,}")
blue_count = (filtered["quadrant"] == "Blue Ocean (High Protein, Low Sugar)").sum()
k2.metric("Blue Ocean products", f"{blue_count:,}", f"{blue_count/len(filtered)*100:.1f}% of selection" if len(filtered) else "0%")
k3.metric("Avg. Sugar (g/100g)", f"{filtered['sugars_100g'].mean():.1f}" if len(filtered) else "–")
k4.metric("Avg. Protein (g/100g)", f"{filtered['proteins_100g'].mean():.1f}" if len(filtered) else "–")

st.divider()

# ------------------------------------------------------------------
# Story 3: Nutrient Matrix scatter plot
# ------------------------------------------------------------------
st.subheader("📊 The Nutrient Matrix: Sugar vs. Protein")

col_chart, col_gap = st.columns([2, 1])

with col_chart:
    fig = px.scatter(
        filtered,
        x="sugars_100g",
        y="proteins_100g",
        color="quadrant",
        color_discrete_map=QUADRANT_COLORS,
        hover_data=["product_name", "primary_category"],
        labels={"sugars_100g": "Sugar (g/100g)", "proteins_100g": "Protein (g/100g)"},
        opacity=0.6,
        height=550,
    )
    # Shade the empty quadrant (high protein, low sugar) to make it pop
    fig.add_shape(
        type="rect",
        x0=0, x1=SUGAR_THRESHOLD,
        y0=PROTEIN_THRESHOLD, y1=max(filtered["proteins_100g"].max(), PROTEIN_THRESHOLD) + 5,
        fillcolor="rgba(37, 99, 235, 0.08)",
        line=dict(color="#2563eb", width=1, dash="dash"),
        layer="below",
    )
    fig.add_annotation(
        x=SUGAR_THRESHOLD / 2, y=max(filtered["proteins_100g"].max(), PROTEIN_THRESHOLD) + 3,
        text="Blue Ocean zone", showarrow=False, font=dict(color="#2563eb", size=12),
    )
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0))
    st.plotly_chart(fig, use_container_width=True)

with col_gap:
    st.markdown("**Blue Ocean penetration by category**")
    st.caption("Share of each category's products that are already High Protein / Low Sugar. The lowest bars are the biggest gaps.")
    total_by_cat = df.groupby("primary_category").size()
    blue_by_cat = df[df["quadrant"] == "Blue Ocean (High Protein, Low Sugar)"].groupby("primary_category").size()
    penetration = (blue_by_cat / total_by_cat * 100).reindex(all_categories).fillna(0).sort_values()
    fig2 = px.bar(
        penetration,
        orientation="h",
        labels={"value": "Blue Ocean %", "primary_category": ""},
        color=penetration.values,
        color_continuous_scale=["#dc2626", "#2563eb"],
    )
    fig2.update_layout(showlegend=False, coloraxis_showscale=False, height=550, margin=dict(l=0, r=10, t=10, b=10))
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ------------------------------------------------------------------
# Story 4: Key Insight box
# ------------------------------------------------------------------
st.subheader("💡 Key Insight & Recommendation")

# Identify the biggest opportunity: lowest Blue Ocean penetration among true "snack" categories
snack_categories = ["Bakery & Biscuits", "Sweets & Candies", "Savory Snacks"]
opportunity_cat = penetration.reindex(snack_categories).dropna().idxmin()
opp_pct = penetration[opportunity_cat]

# Comparator: whichever category currently has the HIGHEST Blue Ocean penetration
# (computed dynamically rather than hardcoded, since this can shift with the thresholds/data)
comparator_cat = penetration.idxmax()
comparator_pct = penetration[comparator_cat]

# Data-backed target figures: instead of just restating the flat 45g/10g pass/fail cutoff,
# use the median protein/sugar of the FEW products that already succeed within the
# opportunity category's Blue Ocean cluster. This mirrors the notebook's approach and gives
# a concrete formulation target rather than a bare threshold.
opp_blue = df[
    (df["primary_category"] == opportunity_cat)
    & (df["quadrant"] == "Blue Ocean (High Protein, Low Sugar)")
]
if len(opp_blue) > 0:
    target_protein = opp_blue["proteins_100g"].median()
    target_sugar = opp_blue["sugars_100g"].median()
else:
    # Fallback to the flat thresholds if no products currently qualify
    target_protein, target_sugar = PROTEIN_THRESHOLD, SUGAR_THRESHOLD

st.info(
    f"**Based on the data, the biggest market opportunity is in {opportunity_cat}, "
    f"specifically targeting products with at least {target_protein:.0f}g of protein and "
    f"less than {target_sugar:.1f}g of sugar per 100g.**\n\n"
    f"Only **{opp_pct:.2f}%** of {opportunity_cat} products currently sit in the Blue Ocean "
    f"quadrant (≥{PROTEIN_THRESHOLD}g protein / <{SUGAR_THRESHOLD}g sugar per 100g), compared to "
    f"**{comparator_pct:.2f}%** for {comparator_cat} — the category where this combination is "
    f"currently most common. This makes {opportunity_cat} the clearest under-served pocket of "
    f"demand: consumers already buy heavily into this aisle, but almost nothing on the shelf meets "
    f"both a health-conscious sugar level and a meaningful protein claim. The {target_protein:.0f}g / "
    f"{target_sugar:.1f}g target above isn't an arbitrary cutoff — it's the median profile of the "
    f"handful of {opportunity_cat} products (n={len(opp_blue)}) that already occupy this space today."
)

st.divider()

# ------------------------------------------------------------------
# Bonus Story: Hidden Gem — top protein sources
# ------------------------------------------------------------------
st.subheader("🔍 Bonus: The Hidden Gem — What's Driving Protein in the Blue Ocean Cluster?")

blue_df = df[df["quadrant"] == "Blue Ocean (High Protein, Low Sugar)"]
sources = top_protein_sources(blue_df["ingredients_text"], n=3)

cols = st.columns(3)
medals = ["🥇", "🥈", "🥉"]
for i, (label, count, pct) in enumerate(sources):
    with cols[i]:
        st.metric(f"{medals[i]} {label}", f"{pct:.1f}%", f"{count:,} products")

st.caption(
    "Share of Blue Ocean products (High Protein / Low Sugar) whose ingredient list mentions each "
    "protein source. Products can only be counted under one source, ranked by priority match."
)

st.divider()

# ------------------------------------------------------------------
# Candidate's Choice
# ------------------------------------------------------------------
st.subheader("⭐ Candidate's Choice: Blue Ocean Penetration Rate")

highest_count_cat = blue_by_cat.idxmax()
highest_count_n = int(blue_by_cat[highest_count_cat])

st.markdown(
    f"""
**What I added:** the *Blue Ocean penetration rate by category* chart (top right of the scatter plot),
showing what **percentage** of each category is already High Protein (≥{PROTEIN_THRESHOLD}g/100g) /
Low Sugar (<{SUGAR_THRESHOLD}g/100g) — rather than just raw counts.

**Why it matters:** raw counts are misleading here. {highest_count_cat} has the most Blue Ocean
products in absolute terms ({highest_count_n:,}), which could tempt a team to conclude that category
is the opportunity. But {highest_count_cat} is also one of the *larger* categories overall, so a
bigger raw count doesn't necessarily mean a bigger *gap*. {opportunity_cat}, by contrast, sits at just
**{opp_pct:.2f}%** penetration — meaning almost the entire category is still "Red Ocean" despite
strong consumer demand for that aisle. Normalizing by category size turns this from a counting
exercise into a genuine gap-finding tool, which is the whole point of a Blue Ocean analysis.
"""
)

with st.expander("View underlying data"):
    st.dataframe(
        filtered[["product_name", "primary_category", "sugars_100g", "proteins_100g", "quadrant"]],
        use_container_width=True,
        height=350,
    )

st.caption("Data: Open Food Facts (openfoodfacts.org), first 500,000 rows, filtered to snack-relevant categories. Built for Helix CPG Partners.")
