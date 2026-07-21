from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st

from connection import SITE_ABBR, SITE_DISPLAY_NAME, get_predictions
from function import (
    TEXT,
    inject_css,
    render_forecast_card,
    render_site_header,
)


HONG_KONG_TZ = ZoneInfo("Asia/Hong_Kong")


st.set_page_config(
    page_title="YSO CT Forecast",
    page_icon="💧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

inject_css()

language = st.radio(
    "Language",
    ["English", "中文"],
    horizontal=True,
    label_visibility="collapsed",
)

text = TEXT[language]

render_site_header(SITE_DISPLAY_NAME, SITE_ABBR, text)

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
            render_forecast_card(day_label, target_date, ct_value, language, text)

except Exception as exc:
    st.error(text["load_error"])

    # Internal prototype only. Remove technical details for customer release.
    with st.expander("Technical details"):
        st.code(str(exc))

st.markdown(
    f'<div class="forecast-note">{text["footer"]}</div>',
    unsafe_allow_html=True,
)
