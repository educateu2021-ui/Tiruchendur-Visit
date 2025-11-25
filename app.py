import streamlit.components.v1 as components
import streamlit as st
import pandas as pd
from io import BytesIO
from pathlib import Path

# ------------ CONFIG ------------
st.set_page_config(page_title="Mason Data Manager", layout="wide")
st.title("Mason Data Management System")
st.markdown("""
<style>
/* Mason grid layout */
.mason-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    margin-top: 1rem;
}

/* Card style */
.mason-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    border-top: 4px solid #4f46e5;
    box-shadow: 0 10px 15px rgba(15, 23, 42, 0.08);
}

/* Mason name & header */
.mason-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 4px;
}

.mason-code {
    font-size: 0.8rem;
    color: #64748b;
    font-weight: 500;
}

.mason-tag {
    font-size: 0.75rem;
    padding: 3px 8px;
    border-radius: 6px;
    background: #f1f5f9;
    color: #475569;
}

/* Meta rows */
.mason-meta-row {
    display: flex;
    font-size: 0.85rem;
    margin-top: 4px;
}

.mason-meta-label {
    width: 80px;
    font-weight: 600;
    color: #64748b;
}

.mason-meta-value {
    color: #0f172a;
}

.mason-day {
    font-weight: 700;
    color: #1d4ed8;
}

/* Products */
.mason-section-title {
    margin-top: 8px;
    font-size: 0.75rem;
    text-transform: uppercase;
    font-weight: 600;
    color: #64748b;
}

.mason-products-empty {
    font-size: 0.75rem;
    font-style: italic;
    color: #94a3b8;
    margin-top: 2px;
}

/* Call button */
.mason-call-btn {
    margin-top: 12px;
    width: 100%;
    padding: 10px 16px;
    border-radius: 8px;
    background: #16a34a;
    color: #ffffff;
    font-size: 0.9rem;
    font-weight: 600;
    border: none;
    text-align: center;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background 0.15s ease;
}

.mason-call-btn:hover {
    background: #15803d;
}

.mason-call-icon {
    margin-right: 6px;
}
</style>
""", unsafe_allow_html=True)

DATA_FILE = "mason_data.xlsx"  # persistent storage file

# ------------ TAILWIND & CSS ------------
st.markdown("""
<script src="https://cdn.tailwindcss.com"></script>
<style>
    .stMarkdown {
        width: 100%;
    }
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1; 
    }
    ::-webkit-scrollbar-thumb {
        background: #c7c7c7; 
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8; 
    }
    .mason-grid {
        display: grid;
        grid-template-columns: repeat(1, minmax(0, 1fr));
        gap: 1.5rem;
    }
    @media (min-width: 768px) {
        .mason-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }
    @media (min-width: 1280px) {
        .mason-grid {
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }
    }
</style>
""", unsafe_allow_html=True)

# ------------ HELPERS ------------

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Standardizes dataframe: strips whitespace, handles NaNs, fixes S.NO."""
    df.columns = [str(c).strip() for c in df.columns]
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df.fillna("")
    if "S.NO" in df.columns:
        df["S.NO"] = pd.to_numeric(df["S.NO"], errors="coerce").fillna(0).astype(int)
    return df


def get_template_excel() -> bytes:
    """Generates an empty template file with correct headers."""
    columns = [
        "S.NO", "MASON CODE", "MASON NAME", "CONTACT NUMBER",
        "DLR NAME", "Location", "DAY", "Category",
        "HW305", "HW101", "Hw201", "HW103", "HW302", "HW310", "other"
    ]
    df_template = pd.DataFrame(columns=columns)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_template.to_excel(writer, index=False, sheet_name="Template")
    return output.getvalue()


def load_excel_data(uploaded_file) -> pd.DataFrame | None:
    """Helper to read excel."""
    try:
        df = pd.read_excel(uploaded_file)
        return clean_dataframe(df)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None


def save_state_for_undo():
    """Saves the current dataframe to history before making changes."""
    st.session_state["prev_data"] = st.session_state["data"].copy()


def to_excel(df: pd.DataFrame) -> bytes:
    """Convert DF to Excel bytes."""
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


# ------------ SESSION STATE INIT ------------

if "data" not in st.session_state:
    st.session_state["data"] = get_initial_dataset()

if "prev_data" not in st.session_state:
    st.session_state["prev_data"] = None

# ------------ DATA MANAGEMENT EXPANDER ------------

with st.expander("🛠️ Data Management (Import / Add / Undo)", expanded=False):

    # Undo
    if st.session_state["prev_data"] is not None:
        if st.button("↩️ Undo Last Change", type="primary"):
            st.session_state["data"] = st.session_state["prev_data"]
            st.session_state["prev_data"] = None
            # persist undo
            st.session_state["data"].to_excel(DATA_FILE, index=False)
            st.success("Restored previous version!")
            st.rerun()

    op_tab1, op_tab2 = st.tabs(["📂 Import Excel", "➕ Add Single Entry"])

    # --- IMPORT TAB ---
    with op_tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.info("Step 1: Download Template")
            st.download_button(
                label="📄 Download Blank Excel Template",
                data=get_template_excel(),
                file_name="mason_data_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        with col2:
            st.info("Step 2: Upload Data")
            uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
            if uploaded_file is not None:
                if st.button("Load Data"):
                    new_data = load_excel_data(uploaded_file)
                    if new_data is not None:
                        save_state_for_undo()
                        st.session_state["data"] = new_data
                        # persist
                        st.session_state["data"].to_excel(DATA_FILE, index=False)
                        st.success(f"Loaded {len(new_data)} rows and saved to {DATA_FILE}!")
                        st.rerun()

    # --- ADD ENTRY TAB ---
    with op_tab2:
        with st.form("entry_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                mason_code = st.text_input("Mason Code")
            with c2:
                mason_name = st.text_input("Mason Name")
            with c3:
                contact_number = st.text_input("Contact Number")

            c4, c5, c6, c7 = st.columns(4)
            with c4:
                dlr_name = st.text_input("DLR Name")
            with c5:
                location = st.text_input("Location")
            with c6:
                day = st.selectbox(
                    "Day",
                    [
                        "MONDAY",
                        "TUESDAY",
                        "WEDNESDAY",
                        "THURSDAY",
                        "FRIDAY",
                        "SATURDAY",
                        "SUNDAY",
                    ],
                )
            with c7:
                category = st.selectbox("Category", ["E", "M", "Other"])

            st.write("**Products (Check box for YES)**")
            pc1, pc2, pc3, pc4, pc5, pc6 = st.columns(6)
            with pc1:
                hw305 = st.checkbox("HW305")
            with pc2:
                hw101 = st.checkbox("HW101")
            with pc3:
                hw201 = st.checkbox("Hw201")
            with pc4:
                hw103 = st.checkbox("HW103")
            with pc5:
                hw302 = st.checkbox("HW302")
            with pc6:
                hw310 = st.checkbox("HW310")

            other_notes = st.text_input("Other / Remarks")
            submitted = st.form_submit_button("Add Line Item")

            if submitted:
                if not mason_name:
                    st.error("Mason Name is required!")
                else:
                    save_state_for_undo()
                    if "S.NO" in st.session_state["data"].columns:
                        new_sno = (
                            st.session_state["data"]["S.NO"].max() + 1
                            if not st.session_state["data"].empty
                            else 1
                        )
                    else:
                        new_sno = 1

                    new_row = {
                        "S.NO": new_sno,
                        "MASON CODE": mason_code,
                        "MASON NAME": mason_name,
                        "CONTACT NUMBER": contact_number,
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
                    }

                    st.session_state["data"] = pd.concat(
                        [st.session_state["data"], pd.DataFrame([new_row])],
                        ignore_index=True,
                    )
                    # persist
                    st.session_state["data"].to_excel(DATA_FILE, index=False)

                    st.success("Entry added & saved!")
                    st.rerun()

# ------------ FILTER SECTION ------------

with st.expander("🔍 Filter Data", expanded=True):
    df_display = st.session_state["data"].copy()

    fc1, fc2, fc3, fc4 = st.columns(4)

    with fc1:
        locs = [str(x) for x in df_display.get("Location", "").unique() if str(x)]
        locations = ["All"] + sorted(locs)
        selected_location = st.selectbox("📍 Location", locations)

    with fc2:
        days_list = [str(x) for x in df_display.get("DAY", "").unique() if str(x)]
        days = ["All"] + sorted(days_list)
        selected_day = st.selectbox("📅 Day", days)

    with fc3:
        cats_raw = [
            str(x)
            for x in df_display.get("Category", "").unique()
            if pd.notna(x) and str(x).strip() != ""
        ]
        cats = ["All"] + sorted(cats_raw) + ["Blank / Uncategorized"]
        selected_cat = st.selectbox("🏷️ Category", cats)

    with fc4:
        st.write("**Product Visibility**")
        show_only_products = st.checkbox("Has Products")
        show_no_products = st.checkbox("No Products")

# Apply filters
if not df_display.empty:
    if selected_location != "All":
        df_display = df_display[df_display["Location"] == selected_location]

    if selected_day != "All":
        df_display = df_display[df_display["DAY"] == selected_day]

    if selected_cat == "Blank / Uncategorized":
        df_display = df_display[
            df_display["Category"].isna() | (df_display["Category"] == "")
        ]
    elif selected_cat != "All":
        df_display = df_display[df_display["Category"] == selected_cat]

    hw_cols = ["HW305", "HW101", "Hw201", "HW103", "HW302", "HW310"]

    if show_only_products:
        mask = df_display[hw_cols].apply(
            lambda x: x.astype(str).str.contains("YES", case=False).any(), axis=1
        )
        df_display = df_display[mask]

    if show_no_products:
        mask = df_display[hw_cols].apply(
            lambda x: not x.astype(str).str.contains("YES", case=False).any(), axis=1
        )
        df_display = df_display[mask]

# ------------ METRICS ------------

st.markdown("### 📊 Dashboard Overview")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Masons", len(st.session_state["data"]))
m2.metric("Visible Rows", len(df_display))
m3.metric(
    "Unique Locations",
    df_display["Location"].nunique() if "Location" in df_display.columns else 0,
)
m4.metric(
    "Unique DLRs",
    df_display["DLR NAME"].nunique() if "DLR NAME" in df_display.columns else 0,
)

st.divider()

# ------------ MAIN TABS ------------

tab_cards, tab_graphs, tab_data = st.tabs(
    ["📇 Mason Cards", "📈 Analytics", "📝 Data Editor"]
)

import streamlit.components.v1 as components  # at top of file

# ----- CARDS TAB -----
with tab_cards:
    st.subheader("Mason Directory")

    if not df_display.empty:
        html = '<div class="mason-grid">'

        for _, row in df_display.iterrows():
            name = row.get("MASON NAME", "Unknown")
            code = row.get("MASON CODE", "N/A")
            cat = row.get("Category", "N/A") or "N/A"

            contact = str(row.get("CONTACT NUMBER", "")).replace(".0", "").strip()
            loc = row.get("Location", "") or "N/A"
            dlr = row.get("DLR NAME", "") or "N/A"
            day = row.get("DAY", "") or "N/A"

            # Products
            hw_cols = ["HW305", "HW101", "Hw201", "HW103", "HW302", "HW310"]
            product_badges = []
            for p in hw_cols:
                if p in row and isinstance(row[p], str) and "YES" in row[p].upper():
                    product_badges.append(p.upper())

            if product_badges:
                products_html = " ".join(
                    f'<span class="mason-tag">{p}</span>' for p in product_badges
                )
            else:
                products_html = '<span class="mason-products-empty">No products listed</span>'

            # Call button
            if contact and contact.lower() != "nan":
                call_html = f'''
                    <a href="tel:{contact}" class="mason-call-btn">
                        <span class="mason-call-icon">📞</span> Call Now
                    </a>
                '''
            else:
                call_html = '''
                    <button class="mason-call-btn" style="background:#cbd5f5;cursor:not-allowed;">
                        No Contact
                    </button>
                '''

            card_html = f"""
            <div class="mason-card">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                    <div>
                        <div class="mason-name">{name}</div>
                        <div class="mason-code">{code}</div>
                    </div>
                    <span class="mason-tag">{cat}</span>
                </div>

                <div>
                    <div class="mason-meta-row">
                        <div class="mason-meta-label">Contact:</div>
                        <div class="mason-meta-value">{contact}</div>
                    </div>
                    <div class="mason-meta-row">
                        <div class="mason-meta-label">Location:</div>
                        <div class="mason-meta-value">{loc}</div>
                    </div>
                    <div class="mason-meta-row">
                        <div class="mason-meta-label">DLR:</div>
                        <div class="mason-meta-value">{dlr}</div>
                    </div>
                    <div class="mason-meta-row">
                        <div class="mason-meta-label">Day:</div>
                        <div class="mason-meta-value mason-day">{day}</div>
                    </div>
                </div>

                <hr style="border:none;border-top:1px solid #e2e8f0;margin:12px 0 6px 0;">

                <div>
                    <div class="mason-section-title">Products:</div>
                    <div style="margin-top:4px;">{products_html}</div>
                </div>

                {call_html}
            </div>
            """

            html += card_html

        html += "</div>"

        # Render inside Streamlit (no script, just HTML+CSS)
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("No masons found matching filters.")


# ----- ANALYTICS TAB -----
with tab_graphs:
    st.subheader("Visual Analytics")
    if not df_display.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Masons per Location**")
            if "Location" in df_display.columns:
                st.bar_chart(df_display["Location"].value_counts())
        with col2:
            st.write("**Masons per Day**")
            if "DAY" in df_display.columns:
                st.bar_chart(df_display["DAY"].value_counts())

        col3, col4 = st.columns(2)
        with col3:
            st.write("**Product Popularity**")
            hw_cols = ["HW305", "HW101", "Hw201", "HW103", "HW302", "HW310"]
            available = [c for c in hw_cols if c in df_display.columns]
            if available:
                counts = df_display[available].apply(
                    lambda x: x.astype(str)
                    .str.contains("YES", case=False)
                    .sum()
                )
                st.bar_chart(counts)
        with col4:
            st.write("**Category Distribution**")
            if "Category" in df_display.columns:
                st.bar_chart(df_display["Category"].value_counts())

# ----- DATA EDITOR TAB -----
with tab_data:
    st.subheader("Raw Data Table (Editable)")

    column_config = {
        "CONTACT NUMBER": st.column_config.TextColumn("Contact"),
        "HW305": st.column_config.TextColumn("HW305", width="small"),
        "HW101": st.column_config.TextColumn("HW101", width="small"),
        "Hw201": st.column_config.TextColumn("Hw201", width="small"),
        "HW103": st.column_config.TextColumn("HW103", width="small"),
        "HW302": st.column_config.TextColumn("HW302", width="small"),
        "HW310": st.column_config.TextColumn("HW310", width="small"),
    }

    # Show the currently filtered data for editing
    edit_df = df_display.copy()
    if not edit_df.empty and "CONTACT NUMBER" in edit_df.columns:
        edit_df["CONTACT NUMBER"] = edit_df["CONTACT NUMBER"].astype(str)

    edited_df = st.data_editor(
        edit_df,
        num_rows="dynamic",
        use_container_width=True,
        height=500,
        column_config=column_config,
    )

    st.write("---")

    # ✅ Save back changes to MAIN DATA (session_state + Excel file)
    if st.button("💾 Save Changes to Main Data"):
        if "S.NO" in edited_df.columns and "S.NO" in st.session_state["data"].columns:
            save_state_for_undo()
            base = st.session_state["data"].set_index("S.NO")
            updated = edited_df.set_index("S.NO")
            base.update(updated)
            st.session_state["data"] = base.reset_index()
            # persist to Excel
            st.session_state["data"].to_excel(DATA_FILE, index=False)
            st.success("Changes saved to main dataset and Excel file!")
        else:
            st.error("Column 'S.NO' not found. Cannot map edited rows back to main data.")

    # 🆕 Download FULL current report (not filtered)
    if not st.session_state["data"].empty:
        st.download_button(
            "📥 Download Full Current Report (All Masons)",
            to_excel(st.session_state["data"]),
            "mason_full_report.xlsx",
        )
