import streamlit as st
import pandas as pd
from io import BytesIO
from pathlib import Path
from datetime import datetime

# =============================================================
# CONFIG
# =============================================================
st.set_page_config(page_title="Mason Data Explorer", layout="wide")

DATA_FILE = "mason_data.xlsx"  # persistent storage file

# =============================================================
# GLOBAL CSS
# =============================================================
st.markdown(
    """
<style>
body {
    background-color: #f3f4f6;
}

.app-intro {
    font-size: 0.95rem;
    color: #4b5563;
}

/* Stat cards */
.stat-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: 0 10px 20px rgba(15, 23, 42, 0.06);
    border-top: 3px solid #4f46e5;
}
.stat-title {
    font-size: 0.75rem;
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 0.05em;
    color: #6b7280;
    margin-bottom: 4px;
}
.stat-value {
    font-size: 2.0rem;
    font-weight: 700;
    color: #312e81;
}

/* Card-like container around each mason */
.mason-card-container {
    border-radius: 14px;
    padding: 14px 16px;
    background: #ffffff;
    box-shadow: 0 8px 16px rgba(15, 23, 42, 0.04);
    margin-bottom: 12px;
}

/* Small tag */
.small-tag {
    font-size: 0.7rem;
    padding: 3px 7px;
    border-radius: 999px;
    background: #eef2ff;
    color: #4f46e5;
}

/* Call button */
.call-btn {
    display:inline-flex;
    justify-content:center;
    align-items:center;
    width:100%;
    padding:0.55rem 0.9rem;
    border-radius:8px;
    background:#813405;
    color:#ffffff;
    font-weight:600;
    text-decoration:none;
}
.call-btn:hover {
    background:#6b2c03;
}
.call-btn-disabled {
    width:100%;
    padding:0.55rem 0.9rem;
    border-radius:8px;
    background:#e5e7eb;
    color:#6b7280;
    font-weight:600;
    text-align:center;
}

/* Make buttons a bit nicer */
div.stButton > button {
    border-radius: 8px;
    padding: 0.40rem 0.9rem;
    font-weight: 600;
}
</style>
""",
    unsafe_allow_html=True,
)

product_columns = ["HW305", "HW101", "Hw201", "HW103", "HW302", "HW310"]

# =============================================================
# HELPERS
# =============================================================
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).strip() for c in df.columns]
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df.fillna("")
    if "S.NO" in df.columns:
        df["S.NO"] = pd.to_numeric(df["S.NO"], errors="coerce").fillna(0).astype(int)
    return df


def get_template_excel() -> bytes:
    columns = [
        "S.NO",
        "MASON CODE",
        "MASON NAME",
        "CONTACT NUMBER",
        "DLR NAME",
        "Location",
        "DAY",
        "Category",
        "HW305",
        "HW101",
        "Hw201",
        "HW103",
        "HW302",
        "HW310",
        "other",
        "Visited_Status",
        "Visited_At",
        "Registered_Status",
        "Registered_At",
    ]
    df_template = pd.DataFrame(columns=columns)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_template.to_excel(writer, index=False, sheet_name="Template")
    return output.getvalue()


def load_excel_data(uploaded_file) -> pd.DataFrame | None:
    try:
        df = pd.read_excel(uploaded_file)
        return clean_dataframe(df)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None


def save_state_for_undo():
    st.session_state["prev_data"] = st.session_state["data"].copy()


def to_excel(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="MasonData")
    return output.getvalue()


# ------------ INITIAL DATA (HARD-CODED + PERSISTENCE) ------------

def get_initial_dataset() -> pd.DataFrame:
    """
    1. If mason_data.xlsx exists -> load & return.
    2. Else -> build from your big hardcoded dict, save to file, return.
    """
    if Path(DATA_FILE).exists():
        df = pd.read_excel(DATA_FILE)
        return clean_dataframe(df)

    data = {
        "S.NO": range(1, 216),
        "MASON CODE": ["M100258", "M100259", "M100260", "M100261", "M100262", "M100263", "M100264", "M100265", "M100266", "M100267", "M100268", "M100270", "M100271", "M100272", "M100273", "M100276", "M100290", "M103410", "M103411", "M103412", "M103413", "M103414", "M103415", "M103416", "M103417", "M103418", "M103419", "M103420", "M103421", "M103422", "M103423", "M103424", "M103425", "M103426", "M103411", "M103427", "M103429", "M104009", "M104011", "M104012", "M105830", "M105831", "M105835", "M106738", "M106739", "M106740", "M106741", "M106752", "M109420", "M112390", "M115196", "M115197", "M115198", "M115199", "M115200", "M115201", "M116145", "M119871", "M121996", "M123673", "M123689", "M129493", "M131585", "M131586", "M131587", "M131759", "M131760", "M131762", "M131916", "M132228", "M133092", "M133208", "M142615", "M144358", "M144601", "M146156", "M146159", "M146786", "M148793", "M149919", "M150738", "M151271", "M152371", "M152481", "M152661", "M152737", "M152857", "M153518", "M154050", "M154051", "M154753", "M154805", "M154848", "M154891", "M154994", "M155379", "M155380", "M155990", "M155995", "M156233", "M156476", "M156578", "M156800", "M157794", "M158421", "M158609", "M158901", "M159030", "M159036", "M159089", "M159008", "M159040", "M159143", "M159179", "M159221", "M159239", "M159495", "M159587", "M159588", "M159858", "M159866", "M156191", "M160161", "M160198", "M160442", "M160497", "M161240", "M161747", "M162303", "M162629", "M163111", "M163154", "M163263", "M163264", "M163299", "M163833", "M163849", "M163991", "M164049", "M164076", "M164217", "M164424", "M164685", "M164686", "M166022", "M166074", "M166076", "M166668", "M167243", "M167757", "M168106", "M168106", "M168677", "M168850", "M168963", "M169303", "M169393", "M169418", "M169600", "M169684", "M169685", "M169701", "M169703", "M169709", "M170017", "M171007", "M171434", "M171461", "M171484", "M172171", "M172592", "M172925", "M172926", "M176313", "M176331", "M176333", "M176334", "M176336", "M176424", "M176494", "M176512", "M176513", "M176514", "M176519", "M176520", "M176521", "M176528", "M176529", "M176530", "M176533", "M176544", "M176545", "M176551", "M176555", "M178257", "M178566", "M179206", "M179361", "M179767", "M180309", "M180889", "M181502", "M181503", "M181504", "M181505", "M181506", "M181507", "M181508", "M181509", "M181511", "M181512", "M182130", "M182217", "M182246", "M182392"],
        "DLR NAME": ["RAJA TRADERS", "RAJA TRADERS", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "SUNDER RAJ HARDWARES", "SUNDER RAJ HARDWARES", "", "PERUMAL KONAR SONS", "SRI SAKTHI ELECTRICALS", "SRI SAKTHI ELECTRICALS", "MM TRADERS", "PERUMAL KONAR SONS", "PERUMAL KONAR SONS", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "", "RAJA TRADERS", "SRI VALLI AGENCY", "SRI MUTHUMALAIMMAN HARDWARES", "SRI VALLI AGENCY", "JANAKIRAM STORES", "JANAKIRAM STORES", "JANAKIRAM STORES", "PERUMAL KONAR SONS", "", "", "SUNDER RAJ HARDWARES", "SHRI MATHI ENTERPRISES", "BISMILLAH AGENCIES", "", "BAMBIAH STORES", "MM TRADERS", "MM TRADERS", "BISMILLAH AGENCIES", "SHP AGENCY", "SRI SAKTHI ELECTRICALS", "SUNDER RAJ HARDWARES", "", "SRI SAKTHI ELECTRICALS", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "SRI MUTHUMALAIMMAN HARDWARES", "SRI VALLI AGENCY", "", "", "PANDIYAN HARDWARES", "", "ANNAM AGENCY", "", "PAPPA HARDWARES", "SRI SAKTHI ELECTRICALS", "SRI SAKTHI ELECTRICALS", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "JANAKIRAM STORES", "PAPPA HARDWARES", "", "JANAKIRAM STORES", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "SRI SAKTHI ELECTRICALS", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "SUNDER RAJ HARDWARES", "SRI MUTHUMALAIMMAN HARDWARES", "PM TRADERS", "PERUMAL KONAR SONS", "JANAKIRAM STORES", "THIRUMAL HARDWARES", "", "ANNAM AGENCY", "BISMILLAH AGENCIES", "SRI VALLI AGENCY", "PM TRADERS", "SHRI MATHI ENTERPRISES", "PM TRADERS", "PERUMAL KONAR SONS", "PM TRADERS", "SRI VALLI AGENCY", "SRI SAKTHI ELECTRICALS", "SRI MUTHUMALAIMMAN HARDWARES", "SUNDER RAJ HARDWARES", "ANNAM AGENCY", "ANNAM AGENCY", "BISMILLAH AGENCIES", "SHRI MATHI ENTERPRISES", "PM TRADERS", "SRI MUTHUMALAIMMAN HARDWARES", "SUNDER RAJ HARDWARES", "PM TRADERS", "SHRI MATHI ENTERPRISES", "PM TRADERS", "PERUMAL KONAR SONS", "SRI SAKTHI ELECTRICALS", "SHRI MATHI ENTERPRISES", "GTM TRADERS", "JAGATHA TRADERS", "PM TRADERS", "SUNDER RAJ HARDWARES", "SRI MUTHUMALAIMMAN HARDWARES", "JANAKIRAM STORES", "PM TRADERS", "THIRUMAL HARDWARES", "PERUMAL KONAR SONS", "THIRUMAL HARDWARES", "THIRUMAL HARDWARES", "PM TRADERS", "SRI MATHI ENTERPRISES", "RAJA TRADERS", "SRI SAKTHI ELECTRICALS", "PM TRADERS", "THIRUMAL HARDWARES", "SHRI MATHI ENTERPRISES", "PM TRADERS", "SRI MUTHUMALAIMMAN HARDWARES", "PM TRADERS", "SR AGENCY", "SR AGENCY", "SR AGENCY", "SR AGENCY", "PM TRADERS", "SR AGENCY", "PERUMAL KONAR SONS", "SHRI MATHI ENTERPRISES", "SR AGENCY", "SRI MATHI ENTERPRISES", "SR AGENCY", "SR AGENCY", "SR AGENCY", "SRI SAKTHI ELECTRICALS", "DHASWAN SAI ENTERPRISES", "SUNDER RAJ HARDWARES", "PERUMAL KONAR SONS", "SRI MUTHUMALAIMMAN HARDWARES", "SRI SAKTHI ELECTRICALS", "SRI MUTHUMALAIMMAN HARDWARES", "JANAKIRAM STORES", "ANNAM AGENCY", "", "SUNDER RAJ HARDWARES", "BAMBIAH STORES", "SHRIMATHI ENTERPRISES", "SRI SAKTHI ELECTRICALS", "PM TRADERS", "SRI VALLI AGENCY", "PANDIYAN HARDWARES", "SRI MUTHUMALAIMMAN HARDWARES", "SRI MATHI ENTERPRISES", "PERUMAL KONAR SONS", "PERUMAL KONAR SONS", "THIRUMAL HARDWARES", "SELVAM HARDWARES", "SR AGENCY", "SR AGENCY", "SRI SAKTHI ELECTRICALS", "SRI VALLI AGENCY", "RAJAMANI TRADERS", "", "PM TRADERS", "SHRI MATHI ENTERPRISES", "SHRI MATHI ENTERPRISES", "PERUMAL KONAR SONS", "PM TRADERS", "SHRI MATHI ENTERPRISES", "PANDIYAN HARDWARES", "PERUMAL KONAR SONS", "ASES TRADERS", "PERUMAL KONAR SONS", "SRI MUTHUMALAIMMAN HARDWARES", "PERUMAL KONAR SONS", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "RAJA TRADERS", "", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "SRI MUTHUMALAIMMAN HARDWARES", "GTM TRADERS", "SHRI MATHI ENTERPRISES", "PERUMAL KONAR SONS", "RAJAMANI TRADERS", "GTM TRADERS", "GTM TRADERS", "SHRI MATHI ENTERPRISES", "ANNAM AGENCY", "PERUMAL KONAR SONS", "GTM TRADERS", "RAJAMANI TRADERS", "SRI VALLI AGENCY", "PM TRADERS", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "SUNDER RAJ HARDWARES", "RAJA TRADERS", "RAJA TRADERS", "", "", "PERUMAL KONAR SONS", "PERUMAL KONAR SONS", "SRI MATHI ENTERPRISES", "PERUMAL KONAR SONS", "PERUMAL KONAR SONS", "ANNAM AGENCY", "ASES", "ASES", "ASES", "ASES", "PERUMAL KONAR SONS", "PERUMAL KONAR SONS", "PERUMAL KONAR SONS", "ANNAM AGENCY ", "PERUMAL KONAR SONS", "SRI VALLI AGENCY", "PERUMAL KONAR SONS"],
        "Location": ["TIRUCHENDUR", "TIRUCHENDUR", "ALWARTHIRUNAGIRI", "ALWARTHIRUNAGIRI", "ALWARTHIRUNAGIRI", "PEIKULAM", "PEIKULAM", "KAYALPATNAM", "SRIVAIGUNDAM", "SEIDHUNGANALLUR", "SEIDHUNGANALLUR", "ERAL", "RAMANUJAMPUTHUR", "RAMANUJAMPUTHUR", "ALWARTHIRUNAGIRI", "AATHUR", "", "TIRUCHENDUR", "ALWARTHIRUNAGIRI", "NAZARATH", "NAZARATH", "NAZARATH", "NAZARATH", "NAZARATH", "SRIVAIGUNDAM", "NAZARATH", "", "PEIKULAM", "ARUMUGANERI", "ARUMUGANERI", "TIRUCHENDUR", "AATHUR", "ERAL", "ERAL", "KAYALPATNAM", "KAYALPATNAM", "SEIDHUNGANALLUR", "PEIKULAM", "", "SEIDHUNGANALLUR", "ALWARTHIRUNAGIRI", "ALWARTHIRUNAGIRI", "NAZARATH", "ALWARTHIRUNAGIRI", "ALWARTHIRUNAGIRI", "ALWARTHIRUNAGIRI", "SONAKANVILAI", "", "ADAIKALAPURAM", "", "KARUNGULAM", "SEIDHUNGANALLUR", "SEIDHUNGANALLUR", "ALWARTHIRUNAGIRI", "ALWARTHIRUNAGIRI", "NAZARATH", "KARUNGULAM", "", "NAZARATH", "TIRUCHENDUR", "KAYALPATNAM", "SEIDHUNGANALLUR", "", "ALWARTHIRUNAGIRI", "MEINGANAPURAM", "ALWARTHIRUNAGIRI", "ALWARTHIRUNAGIRI", "NAZARATH", "NAZARATH", "UDANGUDI", "", "UDANGUDI", "KAYALPATNAM", "ALWARTHIRUNAGIRI", "MUDHALUR", "KAYALPATNAM", "TIRUCHENDUR", "TIRUCHENDUR", "UDANGUDI", "SRIVAIGUNDAM", "SEIDHUNGANALLUR", "NAZARATH", "PEIKULAM", "UDANGUDI", "RAMANUJAMPUTHUR", "KAYALPATNAM", "KAYALPATNAM", "SATHANKULAM", "ERAL", "PEIKULAM", "SATHANKULAM", "MEINGANAPURAM", "MEINGANAPURAM", "SRIVAIGUNDAM", "TIRUCHENDUR", "ARUMUGANERI", "MUDHALUR", "PERIYATHAZHAI", "KAYALPUR", "PEIKULAM", "ERAL", "NAZARATH", "TIRUCHENDUR", "SRIVAIGUNDAM", "KULASEGARAPATNAM", "KULASEGARAPATNAM", "PARAMAKURICHI", "MUDHALUR", "TIRUCHENDUR", "TIRUCHENDUR", "PEIKULAM", "TIRUCHENDUR", "UDANGUDI", "KULASEGARAPATNAM", "MUDHALUR", "ERAL", "ERAL", "KURUMBUR", "KURUMBUR", "KURUMBUR", "KURUMBUR", "SATHANKULAM", "KURUMBUR", "KARUNGULAM", "PARAMAKURICHI", "SATHANKULAM", "ADAIKALAPURAM", "KURUMBUR", "SATHANKULAM", "SATHANKULAM", "SEIDHUNGANALLUR", "KARUNGULAM", "PEIKULAM", "SEIDHUNGANALLUR", "ERAL", "SEIDHUNGANALLUR", "ERAL", "NAZARATH", "NAZARATH", "ALWARTHIRUNAGIRI", "PEIKULAM", "AATHUR", "ARUMUGANERI", "SEIDHUNGANALLUR", "SATHANKULAM", "SONAKANVILAI", "SONAKANVILAI", "NAZARATH", "SRIVAIGUNDAM", "TIRUCHENDUR", "UDANGUDI", "MEINGANAPURAM", "KURUMBUR", "KURUMBUR", "SRIVAIGUNDAM", "ALWARTHIRUNAGIRI", "PEIKULAM", "", "MUDHALUR", "TIRUCHENDUR", "TIRUCHENDUR", "SRIVAIGUNDAM", "MUDHALUR", "KAYALPATNAM", "ARUMUGANERI", "RAMANUJAMPUTHUR", "SRIVAIGUNDAM", "PEIKULAM", "ERAL", "SRIVAIGUNDAM", "TIRUCHENDUR", "ALWARTHIRUNAGIRI", "TIRUCHENDUR", "", "ALWARTHIRUNAGIRI", "UDANGUDI", "NAZARATH", "SATHANKULAM", "SEIDHUNGANALLUR", "RAMANUJAMPUTHUR", "PEIKULAM", "MUDHALUR", "SATHANKULAM", "SATHANKULAM", "UDANGUDI", "SRIVAIGUNDAM", "SATHANKULAM", "ALWARTHIRUNAGIRI", "ALWARTHIRUNAGIRI", "KAYALPATNAM", "KAYALPATNAM", "TIRUCHENDUR", "TIRUCHENDUR", "TIRUCHENDUR", "TIRUCHENDUR", "ALWARTHIRUNAGIRI", "", "SEIDHUNGANALLUR", "THURSDAY", "SRIVAIGUNDAM", "SRIVAIGUNDAM", "TIRUCHENDUR", "UDANGUDI", "SRIVAIGUNDAM", "SRIVAIGUNDAM", "SRIVAIGUNDAM", "SRIVAIGUNDAM", "SRIVAIGUNDAM", "KARUNGULAM", "SRIVAIGUNDAM", "MEINGANAPURAM", "KURUMBUR", "TIRUCHENDUR", "TIRUCHENDUR"],
        "DAY": ["MONDAY", "MONDAY", "SATURDAY", "SATURDAY", "SATURDAY", "FRIDAY", "FRIDAY", "TUESDAY", "THURSDAY", "THURSDAY", "THURSDAY", "TUESDAY", "FRIDAY", "FRIDAY", "SATURDAY", "TUESDAY", "", "MONDAY", "SATURDAY", "SATURDAY", "SATURDAY", "SATURDAY", "SATURDAY", "SATURDAY", "THURSDAY", "SATURDAY", "", "FRIDAY", "MONDAY", "TUESDAY", "MONDAY", "TUESDAY", "TUESDAY", "TUESDAY", "TUESDAY", "TUESDAY", "THURSDAY", "FRIDAY", "", "THURSDAY", "SATURDAY", "SATURDAY", "SATURDAY", "SATURDAY", "SATURDAY", "SATURDAY", "WEDNESDAY", "", "MONDAY", "", "THURSDAY", "THURSDAY", "THURSDAY", "SATURDAY", "SATURDAY", "SATURDAY", "THURSDAY", "FRIDAY", "SATURDAY", "MONDAY", "TUESDAY", "THURSDAY", "", "SATURDAY", "WEDNESDAY", "SATURDAY", "SATURDAY", "SATURDAY", "SATURDAY", "WEDNESDAY", "", "WEDNESDAY", "TUESDAY", "SATURDAY", "MONDAY", "MONDAY", "MONDAY", "WEDNESDAY", "THURSDAY", "THURSDAY", "SATURDAY", "FRIDAY", "WEDNESDAY", "FRIDAY", "TUESDAY", "FRIDAY", "FRIDAY", "WEDNESDAY", "WEDNESDAY", "THURSDAY", "MONDAY", "MONDAY", "WEDNESDAY", "WEDNESDAY", "MONDAY", "FRIDAY", "TUESDAY", "SATURDAY", "MONDAY", "THURSDAY", "WEDNESDAY", "WEDNESDAY", "WEDNESDAY", "WEDNESDAY", "MONDAY", "MONDAY", "FRIDAY", "MONDAY", "WEDNESDAY", "WEDNESDAY", "WEDNESDAY", "TUESDAY", "TUESDAY", "TUESDAY", "TUESDAY", "WEDNESDAY", "TUESDAY", "THURSDAY", "WEDNESDAY", "MONDAY", "MONDAY", "THURSDAY", "SATURDAY", "SATURDAY", "THURSDAY", "THURSDAY", "FRIDAY", "THURSDAY", "TUESDAY", "THURSDAY", "SATURDAY", "SATURDAY", "SATURDAY", "FRIDAY", "TUESDAY", "MONDAY", "THURSDAY", "FRIDAY", "SATURDAY", "MONDAY", "WEDNESDAY", "THURSDAY", "THURSDAY", "WEDNESDAY", "TUESDAY", "TUESDAY", "THURSDAY", "SATURDAY", "FRIDAY", "", "WEDNESDAY", "MONDAY", "MONDAY", "THURSDAY", "WEDNESDAY", "FRIDAY", "MONDAY", "FRIDAY", "THURSDAY", "FRIDAY", "TUESDAY", "THURSDAY", "MONDAY", "SATURDAY", "MONDAY", "", "SATURDAY", "WEDNESDAY", "SATURDAY", "FRIDAY", "THURSDAY", "FRIDAY", "WEDNESDAY", "FRIDAY", "FRIDAY", "WEDNESDAY", "FRIDAY", "FRIDAY", "SATURDAY", "SATURDAY", "TUESDAY", "TUESDAY", "SATURDAY", "MONDAY", "MONDAY", "MONDAY", "", "", "THURSDAY", "MONDAY", "THURSDAY", "MONDAY", "MONDAY", "WEDNESDAY", "THURSDAY", "THURSDAY", "THURSDAY", "THURSDAY", "THURSDAY", "THURSDAY", "THURSDAY", "WEDNESDAY", "TUESDAY", "MONDAY", "MONDAY"],
        "Category": ["E", "E", "E", "E", "E", "E", "M", "M", "E", "E", "E", "E", "E", "E", "E", "E", "", "E", "E", "E", "E", "M", "M", "M", "M", "M", "", "E", "E", "M", "E", "E", "M", "M", "M", "E", "E", "E", "", "E", "E", "E", "E", "E", "M", "E", "", "", "E", "", "E", "E", "E", "M", "M", "M", "M", "", "E", "E", "M", "M", "", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "M", "M", "E", "E", "M", "E", "M", "E", "E", "E", "E", "M", "E", "E", "E", "E", "E", "E", "M", "E", "E", "M", "E", "M", "M", "M", "M", "E", "M", "E", "E", "M", "E", "M", "E", "M", "M", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "M", "M", "M", "E", "E", "M", "M", "E", "E", "E", "E", "E", "E", "E", "E", "E", "", "E", "E", "E", "E", "M", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "M", "E", "M", "E", "M", "M", "E", "E", "E", "E", "E", "E", "M", "M", "E", "M", "M", "M", "E", "E", "E", "M", "E", "M", "M", "M", "M", "M", "M", "M", "M", "M", "M", "E", "E", "E"],
        "HW305": ["YES", "YES", "YES", "", "", "YES", "", "", "YES", "", "YES", "YES", "YES", "YES", "YES", "", "", "YES", "", "", "", "", "", "", "", "", "", "YES", "YES", "", "", "YES", "", "", "YES", "", "YES", "YES", "", "YES", "YES", "YES", "YES", "", "", "", "", "", "YES", "YES", "", "", "", "", "", "", "", "", "", "", "", "YES", "", "YES", "YES", "YES", "YES", "YES", "YES", "", "", "YES", "YES", "YES", "YES", "YES", "YES", "", "YES", "YES", "YES", "", "YES", "", "YES", "", "", "", "YES", "", "YES", "", "YES", "YES", "", "YES", "YES", "YES", "YES", "", "", "", "", "YES", "", "YES", "", "", "YES", "", "", "", "", "", "", "", "YES", "YES", "YES", "YES", "YES", "YES", "YES", "YES", "", "YES", "YES", "", "YES", "", "YES", "", "", "", "YES", "", "YES", "YES", "YES", "YES", "YES", "", "YES", "", "", "", "", "", "YES", "YES", "", "YES", "", "YES", "YES", "YES", "YES", "", "YES", "", "YES", "YES", "", "", "", "", "YES", "", "", "YES", "", "", "", "", "", "", "YES", "YES", "", "YES", "YES", "YES", "", "", "YES", "", "", "", "", "YES", "", "", "", "", "", "", "YES", "YES", "YES", "YES", "YES", "YES", "", "", "", "", "", "YES", "", "", "", "", "", "", "", "", "YES", "YES", "YES", "YES"],
        "HW101": ["YES", "YES", "YES", "", "", "YES", "", "", "YES", "", "YES", "YES", "YES", "YES", "YES", "", "", "", "", "YES", "", "", "", "", "", "", "", "YES", "", "", "", "", "", "", "YES", "YES", "YES", "YES", "", "YES", "YES", "YES", "YES", "", "", "", "", "", "", "YES", "", "", "", "", "", "", "", "", "", "", "", "YES", "", "YES", "YES", "YES", "YES", "", "", "", "", "YES", "YES", "YES", "YES", "YES", "YES", "", "YES", "YES", "YES", "", "YES", "", "YES", "", "", "", "YES", "", "YES", "", "YES", "YES", "", "YES", "YES", "YES", "YES", "", "", "", "", "YES", "", "YES", "", "", "YES", "", "", "", "", "", "", "", "YES", "YES", "YES", "YES", "YES", "YES", "YES", "YES", "", "YES", "YES", "", "YES", "", "YES", "", "", "", "YES", "", "YES", "YES", "YES", "YES", "YES", "", "YES", "", "", "", "", "", "YES", "YES", "", "YES", "", "YES", "YES", "YES", "YES", "", "YES", "", "YES", "YES", "", "", "", "", "YES", "", "", "YES", "", "", "", "", "", "", "YES", "YES", "", "YES", "YES", "YES", "", "", "YES", "", "", "", "", "YES", "", "", "", "", "", "", "YES", "YES", "YES", "YES", "YES", "YES", "", "", "", "", "", "YES", "", "", "", "", "", "", "", "", "YES", "YES", "YES", "YES"],
        "Hw201": ["YES", "YES", "YES", "", "", "YES", "", "", "", "YES", "", "YES", "YES", "YES", "", "", "", "", "", "", "", "", "", "", "", "", "", "YES", "", "", "", "", "", "", "", "", "YES", "YES", "", "YES", "YES", "YES", "YES", "", "", "", "", "", "", "YES", "", "", "", "", "", "", "", "", "", "", "", "YES", "", "YES", "YES", "YES", "YES", "", "", "", "", "YES", "YES", "YES", "YES", "YES", "YES", "", "YES", "YES", "YES", "", "YES", "", "YES", "", "", "", "YES", "", "YES", "", "YES", "YES", "", "YES", "YES", "YES", "YES", "", "", "", "", "YES", "", "YES", "", "", "YES", "", "", "", "", "", "", "", "YES", "YES", "YES", "YES", "YES", "YES", "YES", "YES", "", "YES", "YES", "", "YES", "", "YES", "", "", "", "YES", "", "YES", "YES", "YES", "YES", "YES", "", "YES", "", "", "", "", "", "YES", "YES", "", "YES", "", "YES", "YES", "YES", "YES", "", "YES", "", "YES", "YES", "", "", "", "", "YES", "", "", "YES", "", "", "", "", "", "", "YES", "YES", "", "YES", "YES", "YES", "", "", "YES", "", "", "", "", "YES", "", "", "", "", "", "", "YES", "YES", "YES", "YES", "YES", "YES", "", "", "", "", "", "YES", "", "", "", "", "", "", "", "", "", "YES", "YES", ""],
        "HW103": ["YES", "YES", "", "", "", "", "", "", "", "", "", "YES", "YES", "YES", "", "", "", "YES", "", "", "", "", "", "", "", "", "", "", "", "", "", "YES", "", "", "", "YES", "", "", "", "", "", "", "", "", "", "", "", "", "YES", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "YES", "", "", "", "", "YES", "", "", "", "", "YES", "", "", "", "", "", "", "", "", "YES", "", "", "YES", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "YES", "YES", "", "", "", "", "", "", "", "", "YES", "YES", "", "", "", "", "", "YES", "", "", "YES", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "YES", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "YES", "", ""],
        "HW302": ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "SBR", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "YES", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
        "HW310": ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
        "other": ["", "", "", "", "", "", "", "", "", "", "", "", "YES", "YES", "", "", "", "", "", "SBR", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "Yes", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "YES", "YES", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "SBR", "", ""]
    }

    # Temporary minimal fallback to avoid crash if user forgets to paste:
    st.warning("No DATA_FILE and no hardcoded data found. Using empty dataset.")
    df = pd.DataFrame(columns=[
        "S.NO", "MASON CODE", "MASON NAME", "CONTACT NUMBER",
        "DLR NAME", "Location", "DAY", "Category",
        "HW305", "HW101", "Hw201", "HW103", "HW302", "HW310", "other"
    ])
    return df



def init_filter(key: str, default):
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]


def df_filtered_by_all_except(df: pd.DataFrame, exclude: str):
    """
    For dynamic options: filter df by all current filter selections,
    except the one we're computing options for.
    """
    loc = st.session_state.get("f_location", "All Locations")
    dlr = st.session_state.get("f_dlr", "All DLRs")
    day = st.session_state.get("f_day", "All Days")
    cat = st.session_state.get("f_cat", "All Categories")
    visited = st.session_state.get("f_visited", "All")
    registered = st.session_state.get("f_registered", "All")
    selected_products = st.session_state.get("f_products", [])

    result = df.copy()

    if exclude != "location" and loc != "All Locations" and "Location" in result.columns:
        result = result[result["Location"] == loc]

    if exclude != "dlr" and dlr != "All DLRs" and "DLR NAME" in result.columns:
        result = result[result["DLR NAME"] == dlr]

    if exclude != "day" and day != "All Days" and "DAY" in result.columns:
        result = result[result["DAY"] == day]

    if exclude != "cat" and cat != "All Categories" and "Category" in result.columns:
        result = result[result["Category"] == cat]

    if exclude != "visited" and visited != "All":
        if visited == "Visited":
            result = result[result["Visited_Status"] == "Visited"]
        else:
            result = result[result["Visited_Status"] == ""]

    if exclude != "registered" and registered != "All":
        if registered == "Registered":
            result = result[result["Registered_Status"] == "Registered"]
        else:
            result = result[result["Registered_Status"] == ""]

    if exclude != "products" and selected_products:
        mask = pd.Series(True, index=result.index)
        for col in selected_products:
            if col in result.columns:
                mask = mask & result[col].astype(str).str.contains("YES", case=False)
        result = result[mask]

    return result


# =============================================================
# SESSION STATE INIT
# =============================================================
if "data" not in st.session_state:
    st.session_state["data"] = get_initial_dataset()
if "prev_data" not in st.session_state:
    st.session_state["prev_data"] = None

base_df = st.session_state["data"]

# =============================================================
# HEADER + IMPORT
# =============================================================
h1, h2 = st.columns([4, 1])
with h1:
    st.title("Mason Data Explorer")
    st.markdown(
        '<p class="app-intro">'
        "Use filters to narrow down the list and then tap <strong>Call</strong>, "
        "<strong>Visited</strong> or <strong>Registered</strong> while in the field."
        "</p>",
        unsafe_allow_html=True,
    )

with h2:
    up = st.file_uploader("Import Excel File", type=["xlsx", "xls"], label_visibility="collapsed")
    if up is not None and st.button("📥 Load Imported Excel"):
        new_df = load_excel_data(up)
        if new_df is not None:
            save_state_for_undo()
            for col in ["Visited_Status", "Visited_At", "Registered_Status", "Registered_At"]:
                if col not in new_df.columns:
                    new_df[col] = ""
            st.session_state["data"] = new_df
            st.session_state["data"].to_excel(DATA_FILE, index=False)
            st.success(f"Loaded {len(new_df)} rows.")
            st.experimental_rerun()
    with h2:
        st.write("**Template**")
        st.download_button(
            "📄 Download Blank Template",
            get_template_excel(),
            "mason_template.xlsx",
        )

# =============================================================
# DATA MANAGEMENT (TEMPLATE / ADD / UNDO)
# =============================================================
with st.expander("🛠️ Data Management (Template / Add / Undo)", expanded=False):

    if st.session_state["prev_data"] is not None:
        if st.button("↩️ Undo Last Change"):
            st.session_state["data"] = st.session_state["prev_data"]
            st.session_state["prev_data"] = None
            st.session_state["data"].to_excel(DATA_FILE, index=False)
            st.success("Restored previous version.")
            st.experimental_rerun()

    
    
    with h1:
        st.write("**Add Single Entry**")
        with st.form("add_form", clear_on_submit=True):
            a1, a2, a3 = st.columns(3)
            mason_code = a1.text_input("Mason Code")
            mason_name = a2.text_input("Mason Name")
            contact = a3.text_input("Contact Number")

            b1, b2, b3, b4 = st.columns(4)
            dlr_name = b1.text_input("DLR Name")
            location = b2.text_input("Location")
            day = b3.selectbox(
                "Day",
                ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"],
            )
            category = b4.selectbox("Category", ["E", "M", "Other"])

            st.write("**Products (YES)**")
            p1, p2, p3, p4, p5, p6 = st.columns(6)
            hw305 = p1.checkbox("HW305")
            hw101 = p2.checkbox("HW101")
            hw201 = p3.checkbox("Hw201")
            hw103 = p4.checkbox("HW103")
            hw302 = p5.checkbox("HW302")
            hw310 = p6.checkbox("HW310")

            other_notes = st.text_input("Other / Remarks")

            submitted = st.form_submit_button("Add Mason")
            if submitted:
                if not mason_name:
                    st.error("Mason Name is required.")
                else:
                    save_state_for_undo()
                    if "S.NO" in base_df.columns and not base_df.empty:
                        new_sno = base_df["S.NO"].max() + 1
                    else:
                        new_sno = 1

                    new_row = {
                        "S.NO": new_sno,
                        "MASON CODE": mason_code,
                        "MASON NAME": mason_name,
                        "CONTACT NUMBER": contact,
                        "DLR NAME": dlr_name,
                        "Location": location,
                        "DAY": day,
                        "Category": category,
                        "HW305": "YES" if hw305 else "",
                        "HW101": "YES" if hw101 else "",
                        "Hw201": "YES" if hw201 else "",
                        "HW103": "YES" if hw103 else "",
                        "HW302": "YES" if hw302 else "",
                        "HW310": "YES" if hw310 else "",
                        "other": other_notes,
                        "Visited_Status": "",
                        "Visited_At": "",
                        "Registered_Status": "",
                        "Registered_At": "",
                    }
                    st.session_state["data"] = pd.concat(
                        [st.session_state["data"], pd.DataFrame([new_row])],
                        ignore_index=True,
                    )
                    st.session_state["data"].to_excel(DATA_FILE, index=False)
                    st.success("Mason added & saved.")
                    st.experimental_rerun()
    

# =============================================================
# FILTERS – TRUE CASCADING / DYNAMIC
# =============================================================
st.markdown("### Filters")

# initialise filter state
init_filter("f_location", "All Locations")
init_filter("f_dlr", "All DLRs")
init_filter("f_day", "All Days")
init_filter("f_cat", "All Categories")
init_filter("f_visited", "All")
init_filter("f_registered", "All")
init_filter("f_products", [])

# compute options for each filter based on other filters' current values

# Location options
df_loc = df_filtered_by_all_except(base_df, exclude="location")
loc_values = (
    sorted([x for x in df_loc.get("Location", "").astype(str).unique() if x and x != "nan"])
    if not df_loc.empty
    else []
)
loc_options = ["All Locations"] + loc_values

# DLR options
df_dlr = df_filtered_by_all_except(base_df, exclude="dlr")
dlr_values = (
    sorted([x for x in df_dlr.get("DLR NAME", "").astype(str).unique() if x and x != "nan"])
    if not df_dlr.empty
    else []
)
dlr_options = ["All DLRs"] + dlr_values

# Day options
df_day = df_filtered_by_all_except(base_df, exclude="day")
day_values = (
    sorted([x for x in df_day.get("DAY", "").astype(str).unique() if x and x != "nan"])
    if not df_day.empty
    else []
)
day_options = ["All Days"] + day_values

# Category options
df_cat = df_filtered_by_all_except(base_df, exclude="cat")
cat_values = (
    sorted([x for x in df_cat.get("Category", "").astype(str).unique() if x and x != "nan"])
    if not df_cat.empty
    else []
)
cat_options = ["All Categories"] + cat_values

# row 1 – four dropdowns
f1, f2, f3, f4 = st.columns(4)

current_loc = st.session_state["f_location"]
if current_loc not in loc_options:
    current_loc = "All Locations"
st.session_state["f_location"] = f1.selectbox(
    "Location", loc_options, index=loc_options.index(current_loc)
)

current_dlr = st.session_state["f_dlr"]
if current_dlr not in dlr_options:
    current_dlr = "All DLRs"
st.session_state["f_dlr"] = f2.selectbox(
    "DLR Name", dlr_options, index=dlr_options.index(current_dlr)
)

current_day = st.session_state["f_day"]
if current_day not in day_options:
    current_day = "All Days"
st.session_state["f_day"] = f3.selectbox(
    "Day", day_options, index=day_options.index(current_day)
)

current_cat = st.session_state["f_cat"]
if current_cat not in cat_options:
    current_cat = "All Categories"
st.session_state["f_cat"] = f4.selectbox(
    "Category", cat_options, index=cat_options.index(current_cat)
)

# row 2 – products + visited / registered
p_col, s_col = st.columns([3, 2])

st.session_state["f_products"] = p_col.multiselect(
    "Products (YES in all selected)",
    product_columns,
    default=st.session_state["f_products"],
)

sv, sr = s_col.columns(2)
st.session_state["f_visited"] = sv.selectbox(
    "Visited", ["All", "Visited", "Not Visited"], index=["All", "Visited", "Not Visited"].index(
        st.session_state["f_visited"]
    ),
)
st.session_state["f_registered"] = sr.selectbox(
    "Registered",
    ["All", "Registered", "Not Registered"],
    index=["All", "Registered", "Not Registered"].index(
        st.session_state["f_registered"]
    ),
)

# =============================================================
# APPLY FILTERS TO GET DISPLAY DATA
# =============================================================
df_display = df_filtered_by_all_except(base_df, exclude="")  # apply all

# =============================================================
# METRICS (NOW USING FILTERED DATA)
# =============================================================
total_masons = len(base_df)
displaying = len(df_display)
locations_count = base_df["Location"].nunique() if "Location" in base_df.columns else 0
dlr_count = base_df["DLR NAME"].nunique() if "DLR NAME" in base_df.columns else 0

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-title">Total Masons</div>
            <div class="stat-value">{total_masons}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m2:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-title">Displaying</div>
            <div class="stat-value">{displaying}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m3:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-title">Locations</div>
            <div class="stat-value">{locations_count}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m4:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-title">DLRs</div>
            <div class="stat-value">{dlr_count}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# =============================================================
# MAIN TABS
# =============================================================
tab_cards, tab_graphs, tab_data = st.tabs(
    ["📇 Mason Cards", "📈 Analytics", "📝 Data Editor"]
)

# -------------------------------------------------------------
# TAB 1: CARDS
# -------------------------------------------------------------
with tab_cards:
    st.subheader("Mason List")

    if df_display.empty:
        st.info("No masons found with current filters.")
    else:
        for idx, row in df_display.iterrows():
            code = row.get("MASON CODE", "N/A")
            name = row.get("MASON NAME", "Unknown")
            cat = row.get("Category", "N/A") or "N/A"
            contact = str(row.get("CONTACT NUMBER", "")).replace(".0", "").strip()
            loc = row.get("Location", "") or "N/A"
            dlr = row.get("DLR NAME", "") or "N/A"
            day = row.get("DAY", "") or "N/A"

            visited_status = row.get("Visited_Status", "")
            registered_status = row.get("Registered_Status", "")

            prod_list = [
                col.upper()
                for col in product_columns
                if col in df_display.columns
                and isinstance(row.get(col, ""), str)
                and "YES" in row[col].upper()
            ]

            st.markdown('<div class="mason-card-container">', unsafe_allow_html=True)

            h1, h2 = st.columns([4, 1])
            with h1:
                st.markdown(f"**{name}**")
                st.caption(code)
            with h2:
                st.markdown(
                    f"<div style='text-align:right;'><span class='small-tag'>{cat}</span></div>",
                    unsafe_allow_html=True,
                )

            st.write(f"**Contact:** {contact}")
            st.write(f"**Location:** {loc}")
            st.write(f"**DLR:** {dlr}")
            st.write(f"**Day:**  :blue[{day}]")

            if prod_list:
                st.write("**Products:** " + ", ".join(prod_list))
            else:
                st.write("**Products:** _No products listed_")

            st.markdown("---")
            c1, c2, c3 = st.columns(3)

            # Call
            with c1:
                if contact and contact.lower() != "nan":
                    st.markdown(
                        f"<a href='tel:{contact}' class='call-btn'>📞 Call</a>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        "<div class='call-btn-disabled'>No Contact</div>",
                        unsafe_allow_html=True,
                    )

            # Visited
            with c2:
                v_label = "🧭 Visited" if not visited_status else "✅ Visited"
                if st.button(v_label, key=f"visit_{code}_{idx}"):
                    save_state_for_undo()
                    mask = st.session_state["data"]["MASON CODE"] == code
                    st.session_state["data"].loc[mask, "Visited_Status"] = "Visited"
                    st.session_state["data"].loc[mask, "Visited_At"] = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    st.session_state["data"].to_excel(DATA_FILE, index=False)
                    st.experimental_rerun()

            # Registered
            with c3:
                r_label = "📝 Registered" if not registered_status else "✅ Registered"
                if st.button(r_label, key=f"reg_{code}_{idx}"):
                    save_state_for_undo()
                    mask = st.session_state["data"]["MASON CODE"] == code
                    st.session_state["data"].loc[mask, "Registered_Status"] = "Registered"
                    st.session_state["data"].loc[
                        mask, "Registered_At"
                    ] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state["data"].to_excel(DATA_FILE, index=False)
                    st.experimental_rerun()

            st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 2: ANALYTICS
# -------------------------------------------------------------
with tab_graphs:
    st.subheader("Visual Analytics (Filtered Data)")
    if df_display.empty:
        st.info("No data to chart for current filters.")
    else:
        g1, g2 = st.columns(2)
        with g1:
            st.write("**Masons per Location**")
            if "Location" in df_display.columns:
                st.bar_chart(df_display["Location"].value_counts())
        with g2:
            st.write("**Masons per Day**")
            if "DAY" in df_display.columns:
                st.bar_chart(df_display["DAY"].value_counts())

        g3, g4 = st.columns(2)
        with g3:
            st.write("**Product Popularity**")
            avail = [c for c in product_columns if c in df_display.columns]
            if avail:
                counts = df_display[avail].apply(
                    lambda x: x.astype(str).str.contains("YES", case=False).sum()
                )
                st.bar_chart(counts)
        with g4:
            st.write("**Category Distribution**")
            if "Category" in df_display.columns:
                st.bar_chart(df_display["Category"].value_counts())

# -------------------------------------------------------------
# TAB 3: DATA EDITOR
# -------------------------------------------------------------
with tab_data:
    st.subheader("Raw Data (Filtered View, Editable)")

    edit_df = df_display.copy()
    if not edit_df.empty and "CONTACT NUMBER" in edit_df.columns:
        edit_df["CONTACT NUMBER"] = edit_df["CONTACT NUMBER"].astype(str)

    edited_df = st.data_editor(
        edit_df,
        num_rows="dynamic",
        use_container_width=True,
        height=450,
    )

    st.write("---")

   

    if not st.session_state["data"].empty:
        st.download_button(
            "📥 Download Full Current Report (All Masons)",
            to_excel(st.session_state["data"]),
            "mason_full_report.xlsx",
        )


