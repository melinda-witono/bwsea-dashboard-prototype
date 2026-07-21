from __future__ import annotations

from datetime import date

import streamlit as st


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
        return "❔", text["unknown_risk"], "risk-unknown"
    if ct_value < 25:
        return "⚠️", text["high_risk"], "risk-high"
    if ct_value < 30:
        return "🔶", text["medium_risk"], "risk-medium"
    return "✅", text["low_risk"], "risk-low"


def inject_css() -> None:
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


def render_site_header(
    site_display_name: str,
    site_abbr: str,
    text: dict[str, str],
) -> None:
    st.markdown(
        f"""
        <div class="site-block">
            <div class="site-name">{site_display_name}</div>
            <div class="site-abbr">{site_abbr}</div>
        </div>
        <div class="dashboard-header">
            <div class="page-title">{text["title"]}</div>
            <div class="page-subtitle">{text["subtitle"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_forecast_card(
    day_label: str,
    target_date: date,
    ct_value: float | None,
    language: str,
    text: dict[str, str],
) -> None:
    value_display = "--" if ct_value is None else f"{ct_value:.2f}"

    if language == "中文":
        date_display = (
            f"{target_date.year}年"
            f"{target_date.month}月"
            f"{target_date.day}日"
        )
    else:
        date_display = target_date.strftime("%d %b %Y")

    risk_icon, risk_label, risk_class = get_risk_status(ct_value, text)

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
