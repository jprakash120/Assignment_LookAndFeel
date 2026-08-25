from pathlib import Path

import plotly.express as px
import streamlit as st

from downtime_analytics import answer_question, breakdown, filter_data, kpis, load_data


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "downtime_detail.csv"

st.set_page_config(
    page_title="Manufacturing Downtime Copilot",
    page_icon="⚙️",
    layout="wide",
)

st.markdown(
    """
    <style>
      .stApp { background: #f5f7fa; color: #14233a; }
      [data-testid="stSidebar"] { background: #0b1b2d; }
      [data-testid="stSidebar"] * { color: #eef5ff; }
      [data-testid="stMetric"] { background: white; border: 1px solid #e1e7ef; padding: 1rem; border-radius: 14px; }
      [data-testid="stMetricValue"] { color: #10243c; }
      .block-container { padding-top: 2rem; padding-bottom: 3rem; }
      h1, h2, h3 { letter-spacing: -0.025em; }
      .portfolio-kicker { color: #148c7d; font-size: .76rem; font-weight: 800; letter-spacing: .14em; }
      .portfolio-note { color: #607087; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def get_data():
    return load_data(DATA_PATH)


try:
    source = get_data()
except (FileNotFoundError, ValueError) as exc:
    st.error(f"Data validation failed: {exc}")
    st.stop()

st.markdown('<div class="portfolio-kicker">OPERATIONS INTELLIGENCE</div>', unsafe_allow_html=True)
st.title("Manufacturing Downtime Copilot")
st.markdown(
    '<p class="portfolio-note">Explore verified loss drivers, filter operational context, and ask deterministic natural-language questions.</p>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Filters")
    products = st.multiselect("Product", sorted(source["Product"].unique()))
    shifts = st.multiselect("Shift", sorted(source["Shift"].unique()))
    operators = st.multiselect("Operator", sorted(source["Operator"].unique()))
    date_values = source["Date"].dropna()
    date_range = None
    if not date_values.empty:
        date_range = st.date_input(
            "Date range",
            value=(date_values.min().date(), date_values.max().date()),
            min_value=date_values.min().date(),
            max_value=date_values.max().date(),
        )
    st.divider()
    st.caption("Public portfolio edition. Operator identities are anonymized; metrics are computed from the included rows.")

start_date = date_range[0] if isinstance(date_range, tuple) and len(date_range) == 2 else None
end_date = date_range[1] if isinstance(date_range, tuple) and len(date_range) == 2 else None
filtered = filter_data(
    source,
    products=products,
    shifts=shifts,
    operators=operators,
    start_date=start_date,
    end_date=end_date,
)

stats = kpis(filtered)
metric_columns = st.columns(4)
metric_columns[0].metric("Downtime minutes", f"{stats['total_minutes']:,}")
metric_columns[1].metric("Downtime events", f"{stats['events']:,}")
metric_columns[2].metric("Affected batches", f"{stats['affected_batches']:,}")
metric_columns[3].metric("Operator-attributed share", f"{stats['operator_error_share']:.0%}")

if filtered.empty:
    st.warning("No rows match the selected filters.")
    st.stop()

left, right = st.columns((1.15, 0.85), gap="large")
with left:
    reason_data = breakdown(filtered, "Description").sort_values("Downtime_Minutes")
    reason_chart = px.bar(
        reason_data,
        x="Downtime_Minutes",
        y="Description",
        orientation="h",
        title="Downtime by reason",
        labels={"Downtime_Minutes": "Minutes", "Description": ""},
        color_discrete_sequence=["#23b8a4"],
    )
    reason_chart.update_layout(showlegend=False, margin=dict(l=0, r=20, t=55, b=20), plot_bgcolor="white", paper_bgcolor="white")
    reason_chart.update_xaxes(gridcolor="#e9eef4")
    reason_chart.update_yaxes(gridcolor="rgba(0,0,0,0)")
    st.plotly_chart(reason_chart, use_container_width=True)

with right:
    daily = filtered.groupby("Date", as_index=False)["Downtime_Minutes"].sum()
    daily_chart = px.line(
        daily,
        x="Date",
        y="Downtime_Minutes",
        markers=True,
        title="Daily downtime trend",
        labels={"Downtime_Minutes": "Minutes", "Date": ""},
        color_discrete_sequence=["#477ff1"],
    )
    daily_chart.update_layout(margin=dict(l=0, r=20, t=55, b=20), plot_bgcolor="white", paper_bgcolor="white")
    daily_chart.update_xaxes(gridcolor="rgba(0,0,0,0)")
    daily_chart.update_yaxes(gridcolor="#e9eef4")
    st.plotly_chart(daily_chart, use_container_width=True)

st.subheader("Ask the analytics layer")
question = st.text_input(
    "Question",
    placeholder="Example: Summarize Shift B",
    label_visibility="collapsed",
)
if question:
    st.info(answer_question(filtered, question))
else:
    st.caption("Try: “What is the top downtime reason?”, “Summarize Shift B”, or “What is the operator error share?”")

with st.expander("View validated detail rows"):
    st.dataframe(
        filtered[["Date", "Batch", "Product", "Shift", "Operator", "Description", "Downtime_Minutes", "Operator_Error"]],
        use_container_width=True,
        hide_index=True,
    )
