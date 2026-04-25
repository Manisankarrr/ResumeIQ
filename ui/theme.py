import streamlit as st

def apply_theme(dark: bool):
    css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --bg:        #ffffff;
  --bg2:       #f8f8f6;
  --bg3:       #f0f0ec;
  --bg4:       #eceae3;
  --text:      #111110;
  --text2:     #5c5b57;
  --text3:     #999890;
  --border:    rgba(0,0,0,.09);
  --border2:   rgba(0,0,0,.14);
  --accent:    #534AB7;
  --accent-bg: #EEEDFE;
  --green:     #27500A;
  --green-bg:  #EAF3DE;
  --green-bar: #639922;
  --red:       #791F1F;
  --red-bg:    #FCEBEB;
  --red-bar:   #E24B4A;
  --amber:     #633806;
  --amber-bg:  #FAEEDA;
  --amber-bar: #BA7517;
}

:root.dark, [data-theme="dark"] {
  --bg:        #141413;
  --bg2:       #1e1e1c;
  --bg3:       #282826;
  --bg4:       #2a2a27;
  --text:      #eeecea;
  --text2:     #9e9c96;
  --text3:     #65635e;
  --border:    rgba(255,255,255,.08);
  --border2:   rgba(255,255,255,.13);
  --accent:    #7F77DD;
  --accent-bg: #26215C;
  --green:     #C0DD97;
  --green-bg:  #173404;
  --green-bar: #639922;
  --red:       #F7C1C1;
  --red-bg:    #501313;
  --red-bar:   #E24B4A;
  --amber:     #FAC775;
  --amber-bg:  #412402;
  --amber-bar: #BA7517;
}

html, body, .stApp, .stApp > div {
  font-family: 'Inter', system-ui, sans-serif !important;
}
"""

    if dark:
        css += """
.stApp { background: var(--bg) !important; color: var(--text) !important; }
"""

    css += """
/* === TYPOGRAPHY === */
h1 { font-size: 28px !important; font-weight: 700 !important; color: var(--text) !important; }
h2, h3 { font-size: 18px !important; font-weight: 600 !important; color: var(--text) !important; }

/* === COMPONENT CSS === */
/* Kill default Streamlit chrome */
#MainMenu, footer, [data-testid="stToolbar"] { display: none !important; }

/* Force sidebar static — hide ALL toggle/close controls */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarNavCollapseIcon"],
[data-testid="stSidebar"] button[title="Close sidebar"],
[data-testid="stSidebar"] button[aria-label="Close sidebar"],
[data-testid="stSidebar"] > div:first-child > div > button:first-child {
  display: none !important;
}
/* Sidebar — always visible, user-resizable via drag handle */
[data-testid="stSidebar"] {
  transform: none !important;
  transition: none !important;
  min-width: 280px !important;
  width: clamp(280px, 22vw, 420px) !important;
  max-width: none !important;
  flex-shrink: 0 !important;
}
/* Allow inner content to fill whatever width user drags to */
section[data-testid="stSidebar"] > div {
  width: 100% !important;
}
/* Streamlit sidebar resize handle — enable grabbing */
[data-testid="stSidebar"] > div:first-child {
  overflow-x: hidden !important;
}
.block-container {
  padding-top: 1.5rem !important;
  padding-bottom: 2rem !important;
  max-width: 1100px !important;
}
[data-testid="stMainBlockContainer"] {
  padding-left: 2rem !important;
  padding-right: 2rem !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--border2) !important;
}
[data-testid="stSidebar"] * { font-family: 'Inter', system-ui, sans-serif !important; }

/* Sidebar textarea */
[data-testid="stSidebar"] textarea {
  background: var(--bg) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-size: 13px !important;
  line-height: 1.6 !important;
}
[data-testid="stSidebar"] textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(83,74,183,0.12) !important;
  outline: none !important;
}

/* File uploader — hide default instructions and 200MB label */
[data-testid="stFileUploaderDropzoneInstructions"] { display: none !important; }
[data-testid="stFileUploader"] small { display: none !important; }

/* Force the entire uploader widget to light sidebar bg */
[data-testid="stFileUploader"] {
  background: #f8f8f6 !important;
  color: #111110 !important;
}

/* Dropzone styling — match sidebar background */
[data-testid="stFileUploaderDropzone"] {
  border: 1.5px dashed rgba(0,0,0,.16) !important;
  border-radius: 10px !important;
  background: #f8f8f6 !important;
  min-height: 70px !important;
  color: #111110 !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
  border-color: #534AB7 !important;
  background: #f0f0ec !important;
}
/* The browse / add-more button → compact + circle */
[data-testid="stFileUploader"] button {
  position: static !important;
  float: none !important;
  margin: 4px auto 0 !important;
  width: 28px !important;
  height: 28px !important;
  min-height: unset !important;
  border-radius: 50% !important;
  padding: 0 !important;
  background: var(--accent) !important;
  border: none !important;
  cursor: pointer !important;
  flex-shrink: 0 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  overflow: hidden !important;
  box-shadow: none !important;
}
/* Hide ALL text inside the button */
[data-testid="stFileUploader"] button * {
  display: none !important;
}
/* Inject + via pseudo */
[data-testid="stFileUploader"] button::after {
  content: "+" !important;
  font-size: 18px !important;
  font-weight: 400 !important;
  line-height: 1 !important;
  color: #fff !important;
  display: block !important;
  pointer-events: none !important;
}
/* Label hidden */
[data-testid="stFileUploader"] label {
  display: none !important;
}

/* Primary button */
[data-testid="baseButton-primary"] {
  background: var(--accent) !important;
  border: none !important;
  border-radius: 10px !important;
  color: #ffffff !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  padding: 10px 0 !important;
  letter-spacing: 0.01em !important;
  transition: opacity .15s !important;
}
[data-testid="baseButton-primary"]:hover { opacity: 0.88 !important; }
[data-testid="baseButton-primary"]:active { opacity: 0.78 !important; }
[data-testid="baseButton-primary"]:disabled {
  background: var(--bg4) !important;
  color: var(--text3) !important;
}

/* st.metric (KPI cards) */
[data-testid="stMetric"] {
  background: var(--bg3) !important;
  border-radius: 12px !important;
  padding: 12px 16px !important;
  border: none !important;
}
[data-testid="stMetricLabel"] p {
  font-size: 10px !important;
  font-weight: 600 !important;
  color: var(--text3) !important;
  text-transform: uppercase !important;
  letter-spacing: .07em !important;
  margin-bottom: 4px !important;
}
[data-testid="stMetricValue"] {
  font-size: 24px !important;
  font-weight: 700 !important;
  color: var(--text) !important;
  line-height: 1.15 !important;
}
[data-testid="stMetricDelta"] { font-size: 11px !important; }

/* Tabs */
[data-testid="stTabs"] [role="tablist"] {
  border-bottom: 1.5px solid var(--border) !important;
  gap: 2px !important;
}
[data-testid="stTabs"] button[role="tab"] {
  font-family: 'Inter', system-ui, sans-serif !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  color: var(--text3) !important;
  border-radius: 8px 8px 0 0 !important;
  padding: 7px 14px !important;
  border: none !important;
  background: transparent !important;
  border-bottom: 2px solid transparent !important;
  margin-bottom: -1.5px !important;
  transition: color .15s !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
  color: var(--accent) !important;
  border-bottom-color: var(--accent) !important;
}
[data-testid="stTabsContent"] {
  border: none !important;
  padding-top: 1rem !important;
}

/* st.expander */
[data-testid="stExpander"] {
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  background: var(--bg) !important;
  margin-bottom: 10px !important;
  overflow: hidden !important;
}
[data-testid="stExpander"] summary {
  font-size: 14px !important;
  font-weight: 600 !important;
  color: var(--text) !important;
  padding: 12px 16px !important;
  background: var(--bg) !important;
}
[data-testid="stExpander"] summary:hover { background: var(--bg2) !important; }

/* st.warning / st.info / st.error */
[data-testid="stAlert"] {
  border-radius: 10px !important;
  font-size: 13px !important;
  font-weight: 400 !important;
  padding: 10px 14px !important;
  border-left-width: 3px !important;
}

/* Divider */
hr { border-color: var(--border) !important; margin: 1rem 0 !important; }

/* Download button */
[data-testid="baseButton-secondary"] {
  border: 1px solid var(--border2) !important;
  border-radius: 10px !important;
  background: var(--bg) !important;
  color: var(--text) !important;
  font-size: 13px !important;
  font-weight: 500 !important;
}
[data-testid="baseButton-secondary"]:hover { background: var(--bg3) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }

/* st.spinner */
[data-testid="stSpinner"] p {
  font-size: 13px !important;
  color: var(--text2) !important;
}
</style>
"""
    st.markdown(css, unsafe_allow_html=True)

# Injects a comprehensive CSS theme into the Streamlit app covering typography, sidebar, file uploader, buttons, tabs, metrics, expanders, alerts, scrollbars, and dark mode variables via a single `apply_theme()` call.
