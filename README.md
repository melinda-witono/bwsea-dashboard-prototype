# BWSea CT Forecast Dashboard Prototype

This repository contains the first working prototype of the BWSea CT forecast dashboard.

The application is built with **Python** and **Streamlit** and connects to the prepared **BigQuery CT cache table**.

Current pilot site:

- **Site name:** Yung Shue Au
- **Site abbreviation:** YSO

The dashboard currently shows:

- Today
- Tomorrow
- Day 2
- Day 3
- Lowest CT prediction for each day
- CT risk level
- English / Simplified Chinese switch
- Mobile-friendly layout
- Refresh button
- Loading, no-data, and error states

---

# 1. Purpose of the prototype

The purpose of this prototype is to validate the complete data-to-dashboard flow before building the full commercial website.

```text
BigQuery cache table
        ↓
Filter YSO data
        ↓
Keep today + next 3 days
        ↓
Calculate the lowest CT value for each day
        ↓
Apply CT risk thresholds
        ↓
Display the result in a responsive web page
```

This is still a prototype. It does not yet include:

- Login
- Customer-to-site access control
- Site selection
- Multiple prediction pages
- Production deployment
- Final UI design

---

# 2. Project structure

```text
bwsea-dashboard-prototype/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── .venv/          # local only, not uploaded to GitHub
```

## `app.py`

Contains the current full application:

- Project and site configuration
- BigQuery SQL query
- English and Chinese text
- CSS styling
- BigQuery connection
- CT risk classification
- Refresh behavior
- Forecast card rendering
- Error handling

## `requirements.txt`

Contains the Python packages required to run the app.

## `README.md`

Explains how the code works, what each section controls, and how to run the website.

## `.gitignore`

Prevents local or sensitive files from being uploaded, including:

```text
.venv/
__pycache__/
*.pyc
.env
.streamlit/secrets.toml
credentials.json
service-account*.json
```

---

# 3. Requirements

Install:

- Python 3.10 or newer
- Google Cloud CLI
- Git
- VS Code, recommended

Check the installations:

```powershell
py --version
gcloud --version
git --version
```

---

# 4. How to run the website

## Step 1: Open PowerShell

```powershell
cd $HOME\Desktop\bwsea-dashboard-prototype
```

## Step 2: Create the virtual environment

Only needed the first time:

```powershell
py -m venv .venv
```

## Step 3: Install the packages

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Step 4: Authenticate with Google Cloud

```powershell
gcloud auth application-default login
```

Sign in with a Google account that has access to:

```text
coral-broker-445211-g7
```

Set the project:

```powershell
gcloud config set project coral-broker-445211-g7
```

## Step 5: Start the app

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open:

```text
http://localhost:8501
```

Cleaner demo view:

```text
http://localhost:8501/?embed=true
```

## Step 6: Stop the app

Return to PowerShell and press:

```text
Ctrl + C
```

---

# 5. BigQuery connection

The app uses the Google Cloud BigQuery Python client.

The connection is created with:

```python
client = bigquery.Client(project=PROJECT_ID)
```

The current project is set near the top of `app.py`:

```python
PROJECT_ID = "coral-broker-445211-g7"
```

The current table is:

```text
coral-broker-445211-g7.metabase.ct_value_cache
```

The repository does not include personal credentials or a service-account key.

Local authentication is provided by:

```powershell
gcloud auth application-default login
```

---

# 6. SQL query logic

The SQL query is stored near the top of `app.py` in:

```python
QUERY = """
...
"""
```

The query:

1. Filters the selected site
2. Uses Hong Kong local date
3. Keeps today and the next 3 days
4. Groups results by date
5. Calculates the minimum CT value for each day

Current query:

```sql
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
```

## Why minimum CT is used

There can be several CT predictions for one day.

Lower CT means higher risk, so the dashboard uses:

```sql
MIN(prediction)
```

Example:

```text
28.8
28.5
28.7
28.3
```

Displayed daily value:

```text
28.3
```

---

# 7. CT risk logic

The risk classification function is:

```python
get_risk_status()
```

Current thresholds:

```text
0 <= CT < 25
→ High Risk

25 <= CT < 30
→ Medium Risk

30 <= CT <= 35
→ Low Risk
```

The function returns:

1. Risk icon
2. Risk text
3. CSS class

Example:

```python
return "🔶", text["medium_risk"], "risk-medium"
```

This displays:

```text
🔶 Medium Risk
```

Current boundary handling:

```text
25 → Medium Risk
30 → Low Risk
```

Values outside `0–35` are currently shown as:

```text
Risk unavailable
```

---

# 8. Language switching

The language selector is created with:

```python
language = st.radio(
    "Language",
    ["English", "中文"],
    horizontal=True,
    label_visibility="collapsed",
)
```

All language text is stored in:

```python
TEXT = {
    "English": {...},
    "中文": {...},
}
```

The following change with the selected language:

- Page title
- Subtitle
- Day labels
- Lowest CT label
- Risk labels
- Refresh button
- Loading message
- No-data message
- Error message
- Footer note

English date format:

```text
07 Jul 2026
```

Chinese date format:

```text
2026年7月7日
```

---

# 9. Refresh behavior

The Refresh button uses:

```python
if st.button(text["refresh"], use_container_width=True):
    st.cache_data.clear()
    st.rerun()
```

The process is:

```text
Click Refresh
        ↓
Clear Streamlit local cache
        ↓
Run the BigQuery query again
        ↓
Read the latest data currently in the cache table
        ↓
Update the page
```

The button does not rerun the prediction model.

If the BigQuery table has not been updated, the values may remain the same.

---

# 10. Forecast cards

The app creates four day labels:

```python
day_labels = [
    text["today"],
    text["tomorrow"],
    text["day_2"],
    text["day_3"],
]
```

The loop is:

```python
for day_offset, day_label in enumerate(day_labels):
```

Each card contains:

```text
Day
Date
Large CT value
Lowest CT label
Risk icon
Risk label
```

Example:

```text
📅 Today
07 Jul 2026

28.52

Lowest CT

🔶 Medium Risk
```

---

# 11. CSS and layout

The styling is inside the large section:

```python
st.markdown(
    """
    <style>
        ...
    </style>
    """,
    unsafe_allow_html=True,
)
```

This controls:

- Page background
- Page width
- Top spacing
- Card size
- Card border
- Card shadow
- Font sizes
- CT number size
- Risk badge colors
- Language toggle styling
- Refresh button styling
- Footer styling
- Mobile layout

---

# 12. Exactly what to change for each website part

## Change the GCP project

Find:

```python
PROJECT_ID = "coral-broker-445211-g7"
```

Replace the project ID.

---

## Change the default site

Find:

```python
SITE_ABBR = "YSO"
SITE_DISPLAY_NAME = "Yung Shue Au"
```

Example:

```python
SITE_ABBR = "SMT"
SITE_DISPLAY_NAME = "Sam Mun Tsai"
```

The abbreviation must exist in the BigQuery table.

---

## Change the BigQuery table

Find inside `QUERY`:

```sql
FROM `coral-broker-445211-g7.metabase.ct_value_cache`
```

Replace it with the new full table name.

---

## Change the number of forecast days

Find:

```sql
INTERVAL 3 DAY
```

This means:

```text
Today + next 3 days = 4 days total
```

For today + next 6 days:

```sql
INTERVAL 6 DAY
```

You must also add more entries to `day_labels`.

---

## Change the page title

Find inside `TEXT`:

```python
"title": "CT Forecast"
```

Chinese:

```python
"title": "CT 预测"
```

---

## Change the subtitle

Find:

```python
"subtitle": "Today and next 3 days"
```

Chinese:

```python
"subtitle": "今天及未来 3 天"
```

---

## Change the site name displayed on the page

Find:

```python
SITE_DISPLAY_NAME = "Yung Shue Au"
```

The smaller abbreviation is controlled by:

```python
SITE_ABBR = "YSO"
```

---

## Change the risk thresholds

Find:

```python
def get_risk_status(...):
```

Current logic:

```python
if ct_value < 25:
    return "⚠️", text["high_risk"], "risk-high"

if ct_value < 30:
    return "🔶", text["medium_risk"], "risk-medium"

return "✅", text["low_risk"], "risk-low"
```

Example: High Risk below 24:

```python
if ct_value < 24:
```

Example: Medium Risk below 29:

```python
if ct_value < 29:
```

---

## Change the risk icons

Find:

```python
"⚠️"
"🔶"
"✅"
"❔"
```

Example replacement:

```python
"🔴"
"🟠"
"🟢"
"⚪"
```

These are Unicode icons, so no image files are required.

---

## Change risk labels

Find inside `TEXT`:

```python
"high_risk": "High Risk"
"medium_risk": "Medium Risk"
"low_risk": "Low Risk"
```

Chinese:

```python
"high_risk": "高风险"
"medium_risk": "中风险"
"low_risk": "低风险"
```

---

## Change the CT number size

Find:

```css
.ct-value {
    font-size: 4.8rem;
}
```

Smaller:

```css
font-size: 4rem;
```

Larger:

```css
font-size: 5.5rem;
```

Also update the mobile value:

```css
@media (max-width: 480px) {
    .ct-value {
        font-size: 4.35rem;
    }
}
```

---

## Change card size

Find:

```css
.ct-card {
    padding: 28px 22px;
    margin-bottom: 18px;
}
```

Smaller example:

```css
padding: 20px 16px;
margin-bottom: 12px;
```

---

## Change card corner radius

Find:

```css
border-radius: 24px;
```

More square:

```css
border-radius: 12px;
```

More rounded:

```css
border-radius: 32px;
```

---

## Change page background

Find:

```css
.stApp {
    background: #f4f7fb;
}
```

Replace the hex color.

---

## Change card background

Find inside `.ct-card`:

```css
background: #ffffff;
```

---

## Change risk colors

Find:

```css
.risk-high
.risk-medium
.risk-low
.risk-unknown
```

Example:

```css
.risk-high {
    background: #fee2e2;
    color: #991b1b;
}
```

`background` changes the badge background.

`color` changes the text color.

---

## Change page width

Find:

```css
.block-container {
    max-width: 760px;
}
```

Wider:

```css
max-width: 900px;
```

Narrower:

```css
max-width: 600px;
```

---

## Change top spacing

Find:

```css
padding-top: 4.5rem;
```

If the page is always opened using `?embed=true`, this may be reduced:

```css
padding-top: 1.5rem;
```

---

## Change footer text

Find inside `TEXT`:

```python
"footer": "Forecast data from BWSea prediction system"
```

Chinese:

```python
"footer": "数据来自 BWSea 预测系统"
```

---

## Change browser tab title

Find:

```python
page_title="YSO CT Forecast"
```

---

## Change page icon

Find:

```python
page_icon="💧"
```

Replace the emoji.

---

# 13. Mobile layout

The mobile layout is controlled by:

```css
@media (max-width: 480px) {
    ...
}
```

This section changes:

- Page padding
- Site name size
- Page title size
- Card padding
- CT number size
- Risk badge size

To inspect the mobile page in Microsoft Edge:

```text
F12
```

Then:

```text
Ctrl + Shift + M
```

Choose a device such as:

```text
iPhone SE
```

---

# 14. Streamlit cache

The BigQuery function uses:

```python
@st.cache_data(ttl=300, show_spinner=False)
```

`ttl=300` means the data is cached for 300 seconds, or 5 minutes.

Change to 10 minutes:

```python
ttl=600
```

Removing the decorator disables caching, but this can increase BigQuery queries.

---

# 15. Loading, no-data, and error states

The application includes:

## Loading

```text
Loading predictions...
```

## No data

```text
No prediction data available
```

## Connection or query error

```text
Unable to load prediction data
```

For the internal prototype, technical details are shown in:

```python
with st.expander("Technical details"):
```

For a customer version, remove this section.

---

# 16. Current limitations

## One hard-coded site

```python
SITE_ABBR = "YSO"
```

## No login

The app does not identify customers.

## No site permissions

The app does not restrict which user can see which site.

## Localhost only

The app currently runs at:

```text
localhost:8501
```

Other users cannot open your localhost link.

## No true last-updated timestamp

The app does not show a confirmed cache refresh timestamp.

## One large Python file

Everything is currently kept in `app.py` for the prototype.

Before adding login, multiple sites, and multiple pages, the code should be separated.

---

# 17. Recommended future folder structure

```text
bwsea-dashboard/
│
├── app.py
├── config.py
├── data.py
├── logic.py
├── components.py
├── auth.py
├── requirements.txt
└── README.md
```

Suggested responsibilities:

```text
app.py
→ Main page flow

config.py
→ Project ID, site settings, table names

data.py
→ BigQuery connection and SQL queries

logic.py
→ Daily minimum CT and risk classification

components.py
→ Reusable cards and UI components

auth.py
→ Login and customer access
```

---

# 18. Future login and site-selection flow

```text
User opens the app
        ↓
User logs in
        ↓
System identifies the customer
        ↓
System gets allowed sites
        ↓
User selects a site
        ↓
The app queries that site
        ↓
The app displays the forecast
```

Possible access mapping:

```text
user email
        ↓
customer ID
        ↓
company ID
        ↓
allowed site IDs
        ↓
user role
```

---

# 19. GitHub update workflow

After editing:

```powershell
cd $HOME\Desktop\bwsea-dashboard-prototype
git status
git add .
git commit -m "Describe the change"
git push
```

Example:

```powershell
git add .
git commit -m "Update dashboard card layout"
git push
```

Keep the repository private unless BWSea approves making it public.

---

# 20. Quick run command

```powershell
cd $HOME\Desktop\bwsea-dashboard-prototype
gcloud auth application-default login
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open:

```text
http://localhost:8501/?embed=true
```

---

# 21. Final pipeline summary

```text
BigQuery CT cache table
        ↓
YSO filter
        ↓
Today + next 3 days
        ↓
Daily minimum CT
        ↓
Risk classification
        ↓
English / Chinese labels
        ↓
Responsive forecast cards
        ↓
Streamlit web application
```

This repository should be treated as the technical prototype and starting point for the future commercial dashboard.
