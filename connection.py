from __future__ import annotations

from datetime import date

import streamlit as st
from google.cloud import bigquery


PROJECT_ID = "coral-broker-445211-g7"
SITE_ABBR = "YSO"
SITE_DISPLAY_NAME = "Yung Shue Au"

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
