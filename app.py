from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st
from google.cloud import bigquery


PROJECT_ID = "coral-broker-445211-g7"
SITE_ABBR = "YSO"
SITE_DISPLAY_NAME = "Yung Shue Au"
HONG_KONG_TZ = ZoneInfo("Asia/Hong_Kong")

QUERY = """
SELECT
  prediction_date,
  MIN(prediction) AS lowest_ct
FROM `coral-broker-445211-g7.metabase.ct_value_cache`
WHERE Site_Name_abbr = @site_abbr
  AND prediction_date BETWEEN CURRENT_DATE('Asia/Hong_Kong')
  AND DATE_ADD(
    CURRENT_DATE('Asia/Hong_Kong'),
    INTERVAL 3 DAY
  )
GROUP BY prediction_date
ORDER BY prediction_date
"""

TEXT = {
    "English": {
        "title": "CT Forecast",
        "subtitle": "Today and next 3 days",
        "today": "Today",
        "tomorrow": "Tomorrow",
        "day_2": "Day 2",
        "day_3": "Day 3",
        "lowest_ct": "Lowest CT",
        "refresh": "↻ Refresh",
        "loading": "Loading predictions...",
        "no_data": "No prediction data available",
        "load_error": "Unable to load prediction data",
        "high_risk": "High Risk",
        "medium_risk": "Medium Risk",
        "low_risk": "Low Risk",
        "unknown_risk": "Risk unavailable",
        "footer": "Forecast data from BWSea prediction system",
    },
    "中文": {
        "title": "CT 预测",
        "subtitle": "今天及未来 3 天",
        "today": "今天",
        "tomorrow": "明天",
        "day_2": "第 2 天",
        "day_3": "第 3 天",
        "lowest_ct": "最低 CT 值",
        "refresh": "↻ 刷新",
        "loading": "正在加载预测数据...",
        "no_data": "暂无预测数据",
        "load_error": "无法加载预测数据",
        "high_risk": "高风险",
        "medium_risk": "中风险",
        "low_risk": "低风险",
        "unknown_risk": "风险状态不可用",
        "footer": "数据来自 BWSea 预测系统",
    },
}


st.set_page_config(
    page_title="YSO CT Forecast",
    page_icon="💧",
    layout="centered",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
    <style>
        html, body, [class*="css"] {
            font-family: Arial, "Microsoft YaHei", sans-serif;
        }

        .stApp {
            background: #f4f7fb;
            color: #111827;
        }

        .block-container {
            max-width: 760px;
            padding-top: 1.5rem;
            padding-left: 1rem;
            padding-right: 1rem;
            padding-bottom: 3rem;
        }

        .site-block {
            margin-top: 0.45rem;
            margin-bottom: 0.85rem;
        }

        .site-name {
            color: #111827;
            font-size: 1.45rem;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 0.15rem;
        }

        .site-abbr {
            color: #64748b;
            font-size: 1rem;
            font-weight: 700;
            letter-spacing: 0.05em;
        }

        .dashboard-header {
            margin-bottom: 1.4rem;
        }

        .page-title {
            color: #111827;
            font-size: 2.35rem;
            font-weight: 850;
            line-height: 1.15;
            margin: 0;
        }

        .page-subtitle {
            color: #64748b;
            font-size: 1.15rem;
            font-weight: 600;
            margin-top: 0.35rem;
        }

        .ct-card {
            width: 100%;
            box-sizing: border-box;
            border: 1px solid #dfe6ee;
            border-radius: 24px;
            padding: 28px 22px;
            margin-bottom: 18px;
            text-align: center;
            background: #ffffff;
            color: #111827;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.07);
        }

        .day-label {
            color: #1f2937;
            font-size: 1.45rem;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .date-label {
            color: #6b7280;
            font-size: 1rem;
            font-weight: 500;
            margin-bottom: 16px;
        }

        .ct-value {
            color: #0f172a;
            font-size: 4.8rem;
            font-weight: 900;
            line-height: 1;
            letter-spacing: -0.04em;
            margin: 12px 0 14px;
        }

        .ct-label {
            color: #4b5563;
            font-size: 1.25rem;
            font-weight: 700;
        }

        .risk-status {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 18px;
            padding: 10px 18px;
            border-radius: 999px;
            font-size: 1.15rem;
            font-weight: 850;
        }

        .risk-high {
            background: #fee2e2;
            color: #991b1b;
        }

        .risk-medium {
            background: #fef3c7;
            color: #92400e;
        }

        .risk-low {
            background: #dcfce7;
            color: #166534;
        }

        .risk-unknown {
            background: #e5e7eb;
            color: #4b5563;
        }

        .forecast-note {
            color: #64748b;
            text-align: center;
            font-size: 0.95rem;
            font-weight: 500;
            margin-top: 1.2rem;
            margin-bottom: 1rem;
        }

        div[data-testid="stRadio"] {
            margin-bottom: 0.65rem;
        }

        div[data-testid="stRadio"] [role="radiogroup"] label,
        div[data-testid="stRadio"] [role="radiogroup"] label *,
        div[data-testid="stRadio"] [role="radiogroup"] p,
        div[data-testid="stRadio"] [role="radiogroup"] span {
            color: #111827 !important;
            -webkit-text-fill-color: #111827 !important;
            opacity: 1 !important;
            font-weight: 700 !important;
        }

        div[data-testid="stButton"] > button {
            width: 100%;
            border-radius: 14px;
            border: 1px solid #cbd5e1;
            background: #ffffff;
            color: #111827;
            font-weight: 750;
            padding: 0.7rem 1rem;
        }

        div[data-testid="stButton"] > button:hover {
            border-color: #94a3b8;
            color: #111827;
        }

        .stAlert {
            border-radius: 16px;
        }

        @media (max-width: 480px) {
            .block-container {
                padding-top: 1rem;
                padding-left: 0.85rem;
                padding-right: 0.85rem;
            }

            .site-name {
                font-size: 1.35rem;
            }

            .site-abbr {
                font-size: 0.95rem;
            }

            .page-title {
                font-size: 2rem;
            }

            .page-subtitle {
                font-size: 1.05rem;
            }

            .ct-card {
                padding: 26px 16px;
                margin-bottom: 14px;
                border-radius: 20px;
            }

            .day-label {
                font-size: 1.35rem;
            }

            .date-label {
                font-size: 0.95rem;
                margin-bottom: 12px;
            }

            .ct-value {
                font-size: 4.35rem;
            }

            .ct-label {
                font-size: 1.15rem;
            }

            .risk-status {
                font-size: 1.05rem;
                padding: 9px 15px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_risk_status(
    ct_value: float | None,
    text: dict[str, str],
) -> tuple[str, str, str]:
    """Classify CT risk using Lydia's confirmed thresholds.

    0 <= CT < 25   -> High Risk
    25 <= CT < 30  -> Medium Risk
    30 <= CT <= 35 -> Low Risk

    Values outside the confirmed 0-35 range are flagged for review.
    """
    if ct_value is None or ct_value < 0 or ct_value > 35:
        return "❔", text["no_risk"], "risk-unknown"
    if ct_value < 25:
        return "⚠️", text["high_risk"], "risk-high"
    if ct_value < 30:
        return "🔶", text["medium_risk"], "risk-medium"
    return "✅", text["low_risk"], "risk-low"


@st.cache_data(ttl=300, show_spinner=False)
def get_predictions(site_abbr: str) -> dict[date, float]:
    """Return the lowest CT prediction for today and the next three days."""
    client = bigquery.Client(project=PROJECT_ID)

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "site_abbr",
                "STRING",
                site_abbr,
            )
        ]
    )

    rows = client.query(
        QUERY,
        job_config=job_config,
    ).result()

    predictions: dict[date, float] = {}
    for row in rows:
        if row.lowest_ct is not None:
            predictions[row.prediction_date] = float(row.lowest_ct)

    return predictions


language = st.radio(
    "Language",
    ["English", "中文"],
    horizontal=True,
    label_visibility="collapsed",
)

text = TEXT[language]

st.markdown(
    f"""
    <div class="site-block">
        <div class="site-name">{SITE_DISPLAY_NAME}</div>
        <div class="site-abbr">{SITE_ABBR}</div>
    </div>
    <div class="dashboard-header">
        <div class="page-title">{text["title"]}</div>
        <div class="page-subtitle">{text["subtitle"]}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.button(text["refresh"], use_container_width=True):
    st.cache_data.clear()
    st.rerun()

try:
    with st.spinner(text["loading"]):
        predictions = get_predictions(SITE_ABBR)

    if not predictions:
        st.warning(text["no_data"])
    else:
        today_hk = datetime.now(HONG_KONG_TZ).date()

        day_labels = [
            text["today"],
            text["tomorrow"],
            text["day_2"],
            text["day_3"],
        ]

        for day_offset, day_label in enumerate(day_labels):
            target_date = today_hk + timedelta(days=day_offset)
            ct_value = predictions.get(target_date)

            value_display = "--" if ct_value is None else f"{ct_value:.2f}"

            if language == "中文":
                date_display = (
                    f"{target_date.year}年"
                    f"{target_date.month}月"
                    f"{target_date.day}日"
                )
            else:
                date_display = target_date.strftime("%d %b %Y")

            risk_icon, risk_label, risk_class = get_risk_status(
                ct_value,
                text,
            )

            st.markdown(
                f"""
                <div class="ct-card">
                    <div class="day-label">📅 {day_label}</div>
                    <div class="date-label">{date_display}</div>
                    <div class="ct-value">{value_display}</div>
                    <div class="ct-label">{text["lowest_ct"]}</div>
                    <div class="risk-status {risk_class}">
                        <span>{risk_icon}</span>
                        <span>{risk_label}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

except Exception as exc:
    st.error(text["load_error"])

    # Internal prototype only. Remove technical details for customer release.
    with st.expander("Technical details"):
        st.code(str(exc))

st.markdown(
    f'<div class="forecast-note">{text["footer"]}</div>',
    unsafe_allow_html=True,
)
