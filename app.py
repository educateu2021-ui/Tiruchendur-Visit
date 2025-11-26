import streamlit as st
import pandas as pd
from io import BytesIO
from pathlib import Path
from datetime import datetime

# ------------ CONFIG ------------
st.set_page_config(page_title="Mason Data Explorer", layout="wide", page_icon="🧱")

DATA_FILE = "mason_data.xlsx"  # persistent storage file

# ------------ THEME & CSS (TAILWIND + OVERRIDES) ------------
st.markdown("""
<script src="https://cdn.tailwindcss.com"></script>
<style>
    /* 1. Reset Streamlit Default Backgrounds */
    .stApp {
        background-color: #f8fafc; /* slate-50 */
    }
    
    /* 2. Hide Default Streamlit Elements to match HTML clean look */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 0rem;
        padding-bottom: 5rem;
        max-width: 100%;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* 3. Card Styling Helper Classes for Streamlit Containers */
    .mason-card-container {
        background-color: white;
        border-radius: 0.5rem; /* rounded-lg */
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1); /* shadow */
        padding: 1.25rem; /* p-5 */
        border-top: 4px solid #6366f1; /* border-indigo-500 */
        margin-bottom: 1.5rem;
    }
    
    /* 4. Filter Box Styling */
    div[data-testid="stExpander"] {
        background-color: white;
        border: none;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        color: #334155; /* slate-700 */
    }
    div[data-testid="stExpander"] details summary {
        color: #334155; /* slate-700 */
        font-weight: 600;
    }

    /* 5. Button Overrides to match Indigo/Green theme */
    div.stButton > button {
        border-radius: 0.375rem;
        font-weight: 500;
        border: none;
        width: 100%;
    }
    /* Primary/Call buttons are handled via inline logic, but general tweaks here */
    
    /* 6. Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border: none;
        color: #64748b; /* slate-500 */
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #4338ca; /* indigo-700 */
        border-bottom: 2px solid #4338ca;
    }
</style>
""", unsafe_allow_html=True)

# ------------ HELPERS ------------

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).strip() for c in df.columns]
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df.fillna("")
    if "S.NO" in df.columns:
        df["S.NO"] = pd.to_numeric(df["S.NO"], errors="coerce").fillna(0).astype(int)
    return df

def get_template_excel() -> bytes:
    columns = [
        "S.NO", "MASON CODE", "MASON NAME", "CONTACT NUMBER",
        "DLR NAME", "Location", "DAY", "Category",
        "HW305", "HW101", "Hw201", "HW103", "HW302", "HW310", "other",
        "Visited_Status", "Visited_At", "Registered_Status", "Registered_At"
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

# ------------ INITIAL DATA ------------

def get_initial_dataset() -> pd.DataFrame:
    if Path(DATA_FILE).exists():
        df = pd.read_excel(DATA_FILE)
        return clean_dataframe(df)

    # Fallback structure if file doesn't exist
    df = pd.DataFrame(columns=[
        "S.NO", "MASON CODE", "MASON NAME", "CONTACT NUMBER",
        "DLR NAME", "Location", "DAY", "Category",
        "HW305", "HW101", "Hw201", "HW103", "HW302", "HW310", "other",
        "Visited_Status", "Visited_At", "Registered_Status", "Registered_At"
    ])
    return df

# ------------ SESSION STATE INIT ------------

if "data" not in st.session_state:
    st.session_state["data"] = get_initial_dataset()

if "prev_data" not in st.session_state:
    st.session_state["prev_data"] = None

for col in ["Visited_Status", "Visited_At", "Registered_Status", "Registered_At"]:
    if col not in st.session_state["data"].columns:
        st.session_state["data"][col] = ""

# --- filter-related session defaults ---
keys = ["filter_day", "filter_location", "filter_cat", "filter_visit_status", 
        "filter_reg_status", "filter_mobile_input", "filter_mobile_query", 
        "filter_only_products", "filter_no_products", "reset_filters"]

for k in keys:
    if k not in st.session_state:
        if "only_products" in k or "no_products" in k or "reset" in k:
            st.session_state[k] = False
        elif "mobile" in k:
            st.session_state[k] = ""
        else:
            st.session_state[k] = "All"

# --- apply reset ---
if st.session_state.get("reset_filters", False):
    st.session_state["filter_day"] = "All"
    st.session_state["filter_location"] = "All"
    st.session_state["filter_cat"] = "All"
    st.session_state["filter_visit_status"] = "All"
    st.session_state["filter_reg_status"] = "All"
    st.session_state["filter_only_products"] = False
    st.session_state["filter_no_products"] = False
    st.session_state["filter_mobile_input"] = ""
    st.session_state["filter_mobile_query"] = ""
    st.session_state["reset_filters"] = False

# ==============================================================================
# HTML HEADER
# ==============================================================================
st.markdown("""
<header class="bg-white shadow-md w-full sticky top-0 z-50 mb-8">
    <div class="container mx-auto px-4 py-4 md:px-8 flex flex-col md:flex-row justify-between items-center gap-4">
        <h1 class="text-3xl font-bold text-indigo-700">Mason Data Explorer</h1>
        <div class="flex items-center gap-2">
            <span class="text-xs text-slate-500 italic hidden md:block">System Active</span>
        </div>
    </div>
</header>
<div class="container mx-auto px-4 md:px-8">
""", unsafe_allow_html=True)

# ==============================================================================
# DATA FILTERING LOGIC (Prep for Display)
# ==============================================================================
df_display = st.session_state["data"].copy()

if not df_display.empty:
    # 1. Day
    if st.session_state["filter_day"] != "All":
        df_display = df_display[df_display["DAY"] == st.session_state["filter_day"]]
    
    # 2. Location
    if st.session_state["filter_location"] != "All":
        df_display = df_display[df_display["Location"] == st.session_state["filter_location"]]
    
    # 3. Category
    if st.session_state["filter_cat"] == "Blank / Uncategorized":
        df_display = df_display[df_display["Category"].isna() | (df_display["Category"] == "")]
    elif st.session_state["filter_cat"] != "All":
        df_display = df_display[df_display["Category"] == st.session_state["filter_cat"]]
    
    # 4. Visit Status
    if "Visited_Status" in df_display.columns:
        if st.session_state["filter_visit_status"] == "Visited":
            df_display = df_display[df_display["Visited_Status"] == "Visited"]
        elif st.session_state["filter_visit_status"] == "Not Visited":
            df_display = df_display[(df_display["Visited_Status"].isna()) | (df_display["Visited_Status"] == "")]

    # 5. Reg Status
    if "Registered_Status" in df_display.columns:
        if st.session_state["filter_reg_status"] == "Registered":
            df_display = df_display[df_display["Registered_Status"] == "Registered"]
        elif st.session_state["filter_reg_status"] == "Not Registered":
            df_display = df_display[(df_display["Registered_Status"].isna()) | (df_display["Registered_Status"] == "")]

    # 6. Products
    hw_cols = ["HW305", "HW101", "Hw201", "HW103", "HW302", "HW310"]
    if st.session_state["filter_only_products"]:
        mask = df_display[hw_cols].apply(lambda x: x.astype(str).str.contains("YES", case=False).any(), axis=1)
        df_display = df_display[mask]
    if st.session_state["filter_no_products"]:
        mask = df_display[hw_cols].apply(lambda x: not x.astype(str).str.contains("YES", case=False).any(), axis=1)
        df_display = df_display[mask]

    # 7. Mobile
    if st.session_state["filter_mobile_query"] and "CONTACT NUMBER" in df_display.columns:
        contact_str = df_display["CONTACT NUMBER"].astype(str).str.replace(".0", "", regex=False)
        df_display = df_display[contact_str.str.contains(st.session_state["filter_mobile_query"], case=False, na=False)]

# ==============================================================================
# HTML-STYLE METRICS GRID
# ==============================================================================

total_masons = len(st.session_state["data"])
displaying = len(df_display)
loc_count = df_display["Location"].nunique() if "Location" in df_display.columns else 0
dlr_count = df_display["DLR NAME"].nunique() if "DLR NAME" in df_display.columns else 0

st.markdown(f"""
<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
    <div class="bg-white p-5 rounded-lg shadow text-center">
        <h3 class="text-sm font-semibold text-slate-500 uppercase">Total Masons</h3>
        <p class="text-4xl font-bold text-indigo-600">{total_masons}</p>
    </div>
    <div class="bg-white p-5 rounded-lg shadow text-center">
        <h3 class="text-sm font-semibold text-slate-500 uppercase">Displaying</h3>
        <p class="text-4xl font-bold text-indigo-600">{displaying}</p>
    </div>
    <div class="bg-white p-5 rounded-lg shadow text-center">
        <h3 class="text-sm font-semibold text-slate-500 uppercase">Locations</h3>
        <p class="text-4xl font-bold text-indigo-600">{loc_count}</p>
    </div>
    <div class="bg-white p-5 rounded-lg shadow text-center">
        <h3 class="text-sm font-semibold text-slate-500 uppercase">DLRs</h3>
        <p class="text-4xl font-bold text-indigo-600">{dlr_count}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# FILTERS SECTION
# ==============================================================================
# Wrap in a container styled like the HTML white box
with st.expander("🔍 Filters & Data Controls", expanded=True):
    base_df = st.session_state["data"].copy()
    
    # Row 1: Selects
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.caption("Day")
        days_list = [str(x).strip() for x in base_df.get("DAY", "").unique() if str(x).strip()]
        days = ["All"] + sorted(set(days_list))
        st.selectbox("", days, key="filter_day", label_visibility="collapsed")
    
    # Filter logic for cascades
    df_loc = base_df[base_df["DAY"] == st.session_state["filter_day"]] if st.session_state["filter_day"] != "All" else base_df
    
    with c2:
        st.caption("Location")
        locs = [str(x).strip() for x in df_loc.get("Location", "").unique() if str(x).strip()]
        locations = ["All"] + sorted(set(locs))
        st.selectbox("", locations, key="filter_location", label_visibility="collapsed")

    df_cat = df_loc[df_loc["Location"] == st.session_state["filter_location"]] if st.session_state["filter_location"] != "All" else df_loc

    with c3:
        st.caption("Category")
        cats_raw = [str(x).strip() for x in df_cat.get("Category", "").unique() if str(x).strip() != ""]
        cats = ["All"] + sorted(set(cats_raw))
        if (df_cat.get("Category", "") == "").any(): cats.append("Blank / Uncategorized")
        st.selectbox("", cats, key="filter_cat", label_visibility="collapsed")

    with c4:
        st.caption("Status Filters")
        st.selectbox("Visited Status", ["All", "Visited", "Not Visited"], key="filter_visit_status", label_visibility="collapsed")

    st.markdown("---")
    
    # Row 2: Products & Mobile
    rc1, rc2 = st.columns([1, 1])
    with rc1:
        st.caption("Product Rules")
        col_p1, col_p2 = st.columns(2)
        col_p1.checkbox("Has Products", key="filter_only_products")
        col_p2.checkbox("No Products", key="filter_no_products")
    
    with rc2:
        st.caption("Search Mobile")
        sm1, sm2, sm3 = st.columns([2,1,1])
        with sm1:
            st.text_input("", placeholder="Number...", key="filter_mobile_input", label_visibility="collapsed")
        with sm2:
            if st.button("Search"):
                st.session_state["filter_mobile_query"] = st.session_state["filter_mobile_input"].strip()
                st.rerun()
        with sm3:
            if st.button("Reset"):
                st.session_state["reset_filters"] = True
                st.rerun()

# ==============================================================================
# MAIN TABS
# ==============================================================================
st.markdown("<div class='mb-6'></div>", unsafe_allow_html=True) # Spacer

tab_cards, tab_graphs, tab_editor, tab_import = st.tabs(
    ["📇 Mason Directory", "📈 Visualizations", "📝 Data Editor", "🛠️ Import/Add"]
)

# ----- TAB 1: MASON CARDS (STYLED LIKE HTML) -----
with tab_cards:
    if df_display.empty:
        st.markdown("""
        <div class="text-center bg-white p-10 rounded-lg shadow">
            <p class="text-2xl font-semibold text-slate-700">No Masons Found</p>
            <p class="text-slate-500 mt-2">Try adjusting your filter criteria.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # We need to iterate and create "Cards". 
        # Streamlit requires buttons to be outside HTML strings.
        # Design Strategy: Use Markdown for the Card Body, Streamlit columns for buttons, wrapped in a white BG style.
        
        # Grid layout using columns is tricky with dynamic heights, so we iterate rows.
        # We will do a 2-column layout for the cards.
        
        cols = st.columns(2)
        
        for idx, (index, row) in enumerate(df_display.iterrows()):
            # Select column (0 or 1)
            col_ptr = cols[idx % 2]
            
            # Prepare Data
            code = row.get("MASON CODE", "N/A")
            name = row.get("MASON NAME", "Unknown")
            cat = row.get("Category", "N/A") or "N/A"
            contact = str(row.get("CONTACT NUMBER", "")).replace(".0", "").strip()
            loc = row.get("Location", "") or "N/A"
            dlr = row.get("DLR NAME", "") or "N/A"
            day = row.get("DAY", "") or "N/A"
            
            # Product Pills
            hw_cols = ["HW305", "HW101", "Hw201", "HW103", "HW302", "HW310"]
            prod_list = [p.upper() for p in hw_cols if p in row and isinstance(row[p], str) and "YES" in row[p].upper()]
            
            prod_html = ""
            if prod_list:
                for p in prod_list:
                    prod_html += f'<span class="inline-block bg-indigo-100 text-indigo-800 text-xs font-medium px-2.5 py-0.5 rounded-full border border-indigo-200 mr-1 mb-1">{p}</span>'
            else:
                prod_html = '<span class="text-xs text-slate-400 italic">No products listed</span>'
            
            # Status Logic
            visited = row.get("Visited_Status", "") == "Visited"
            registered = row.get("Registered_Status", "") == "Registered"
            
            status_html = ""
            if visited: status_html += '<span class="text-green-600 font-bold text-xs mr-2">✓ Visited</span>'
            if registered: status_html += '<span class="text-blue-600 font-bold text-xs">✓ Registered</span>'

            # Render Card in the specific column
            with col_ptr:
                # We start a container that we will style visually using the CSS class defined at top
                with st.container():
                    # Card Header & Info HTML
                    st.markdown(f"""
                    <div class="bg-white rounded-lg shadow p-5 flex flex-col border-t-4 border-indigo-500 mb-2 h-full">
                        <div class="mb-3">
                            <h3 class="text-xl font-bold text-slate-800">{name}</h3>
                            <div class="flex justify-between items-center mt-1">
                                <p class="text-sm text-slate-500 font-medium">{code}</p>
                                <span class="bg-slate-100 text-slate-600 text-xs px-2 py-1 rounded">{cat}</span>
                            </div>
                        </div>
                        <div class="space-y-2 text-sm text-slate-700 mb-4 flex-grow">
                            <p class="flex items-start"><span class="w-24 font-semibold text-slate-500">Contact:</span> {contact}</p>
                            <p class="flex items-start"><span class="w-24 font-semibold text-slate-500">Location:</span> {loc}</p>
                            <p class="flex items-start"><span class="w-24 font-semibold text-slate-500">DLR:</span> {dlr}</p>
                            <p class="flex items-start"><span class="w-24 font-semibold text-slate-500">Day:</span> <span class="font-semibold text-indigo-700">{day}</span></p>
                            <div class="mt-2">{status_html}</div>
                        </div>
                        <div class="pt-3 border-t border-slate-200">
                            <h4 class="text-xs font-semibold text-slate-600 mb-2">Products:</h4>
                            <div class="flex flex-wrap gap-1 mb-3">
                                {prod_html}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Action Buttons (Streamlit Native)
                    # We place them "inside" the card visual flow by minimizing margin
                    b1, b2, b3 = st.columns(3)
                    with b1:
                        if contact and contact.lower() != "nan":
                            st.markdown(f'<a href="tel:{contact}" target="_self" class="inline-flex items-center justify-center w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md no-underline">📞 Call</a>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="inline-flex items-center justify-center w-full px-4 py-2 bg-slate-300 text-slate-500 text-sm font-medium rounded-md">No #</div>', unsafe_allow_html=True)
                    
                    with b2:
                        label_v = "Undo Visit" if visited else "Mark Visit"
                        type_v = "secondary" if visited else "primary"
                        if st.button(label_v, key=f"vis_{index}"):
                            save_state_for_undo()
                            new_status = "" if visited else "Visited"
                            st.session_state["data"].at[index, "Visited_Status"] = new_status
                            st.session_state["data"].at[index, "Visited_At"] = datetime.now().strftime("%Y-%m-%d")
                            st.session_state["data"].to_excel(DATA_FILE, index=False)
                            st.rerun()

                    with b3:
                        label_r = "Undo Reg" if registered else "Mark Reg"
                        if st.button(label_r, key=f"reg_{index}"):
                            save_state_for_undo()
                            new_status = "" if registered else "Registered"
                            st.session_state["data"].at[index, "Registered_Status"] = new_status
                            st.session_state["data"].at[index, "Registered_At"] = datetime.now().strftime("%Y-%m-%d")
                            st.session_state["data"].to_excel(DATA_FILE, index=False)
                            st.rerun()
                    
                    st.markdown("<div class='mb-6'></div>", unsafe_allow_html=True)

# ----- TAB 2: VISUALIZATIONS (STYLED CONTAINERS) -----
with tab_graphs:
    st.markdown('<h2 class="text-2xl font-bold text-slate-800 mb-6 text-center">Data Visualizations</h2>', unsafe_allow_html=True)
    
    if not df_display.empty:
        g1, g2 = st.columns(2)
        with g1:
            st.markdown('<div class="bg-white p-5 rounded-lg shadow h-full">', unsafe_allow_html=True)
            st.markdown('<h3 class="text-lg font-semibold text-slate-700 text-center mb-4">Masons per Location</h3>', unsafe_allow_html=True)
            if "Location" in df_display.columns:
                st.bar_chart(df_display["Location"].value_counts(), color="#6366f1")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with g2:
            st.markdown('<div class="bg-white p-5 rounded-lg shadow h-full">', unsafe_allow_html=True)
            st.markdown('<h3 class="text-lg font-semibold text-slate-700 text-center mb-4">Masons per Day</h3>', unsafe_allow_html=True)
            if "DAY" in df_display.columns:
                st.bar_chart(df_display["DAY"].value_counts(), color="#6366f1")
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        g3, g4 = st.columns(2)
        with g3:
            st.markdown('<div class="bg-white p-5 rounded-lg shadow h-full">', unsafe_allow_html=True)
            st.markdown('<h3 class="text-lg font-semibold text-slate-700 text-center mb-4">Product Popularity</h3>', unsafe_allow_html=True)
            hw_cols = ["HW305", "HW101", "Hw201", "HW103", "HW302", "HW310"]
            available = [c for c in hw_cols if c in df_display.columns]
            if available:
                counts = df_display[available].apply(lambda x: x.astype(str).str.contains("YES", case=False).sum())
                st.bar_chart(counts, color="#6366f1")
            st.markdown('</div>', unsafe_allow_html=True)

        with g4:
            st.markdown('<div class="bg-white p-5 rounded-lg shadow h-full">', unsafe_allow_html=True)
            st.markdown('<h3 class="text-lg font-semibold text-slate-700 text-center mb-4">Category Distribution</h3>', unsafe_allow_html=True)
            if "Category" in df_display.columns:
                st.bar_chart(df_display["Category"].value_counts(), color="#6366f1")
            st.markdown('</div>', unsafe_allow_html=True)

# ----- TAB 3: EDITOR -----
with tab_editor:
    st.markdown('<div class="bg-white p-5 rounded-lg shadow">', unsafe_allow_html=True)
    st.subheader("Raw Data Table")
    
    column_config = {
        "CONTACT NUMBER": st.column_config.TextColumn("Contact"),
        "HW305": st.column_config.TextColumn("HW305", width="small"),
        "HW101": st.column_config.TextColumn("HW101", width="small"),
        "Hw201": st.column_config.TextColumn("Hw201", width="small"),
        "HW103": st.column_config.TextColumn("HW103", width="small"),
        "HW302": st.column_config.TextColumn("HW302", width="small"),
        "HW310": st.column_config.TextColumn("HW310", width="small"),
    }
    
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
    
    st.markdown("---")
    st.download_button(
        "📥 Download Full Report",
        to_excel(st.session_state["data"]),
        "mason_full_report.xlsx",
        type="primary"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ----- TAB 4: IMPORT/ADD -----
with tab_import:
    st.markdown('<div class="bg-white p-5 rounded-lg shadow">', unsafe_allow_html=True)
    
    # Undo
    if st.session_state["prev_data"] is not None:
        if st.button("↩️ Undo Last Change"):
            st.session_state["data"] = st.session_state["prev_data"]
            st.session_state["prev_data"] = None
            st.session_state["data"].to_excel(DATA_FILE, index=False)
            st.success("Restored previous version!")
            st.rerun()
        st.markdown("---")

    sub_t1, sub_t2 = st.tabs(["Add Single Entry", "Import Excel"])
    
    with sub_t2:
        st.info("Step 1: Download Template, Step 2: Upload Filled Excel")
        st.download_button(
            label="📄 Download Template",
            data=get_template_excel(),
            file_name="mason_data_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
        if uploaded_file is not None:
            if st.button("Load Data to System"):
                new_data = load_excel_data(uploaded_file)
                if new_data is not None:
                    save_state_for_undo()
                    st.session_state["data"] = new_data
                    # ensure cols
                    for col in ["Visited_Status", "Visited_At", "Registered_Status", "Registered_At"]:
                        if col not in st.session_state["data"].columns:
                            st.session_state["data"][col] = ""
                    st.session_state["data"].to_excel(DATA_FILE, index=False)
                    st.success(f"Loaded {len(new_data)} rows!")
                    st.rerun()

    with sub_t1:
        with st.form("entry_form"):
            c1, c2, c3 = st.columns(3)
            with c1: mason_code = st.text_input("Mason Code")
            with c2: mason_name = st.text_input("Mason Name")
            with c3: contact_number = st.text_input("Contact Number")

            c4, c5, c6, c7 = st.columns(4)
            with c4: dlr_name = st.text_input("DLR Name")
            with c5: location = st.text_input("Location")
            with c6: day_val = st.selectbox("Day", ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"])
            with c7: category = st.selectbox("Category", ["E", "M", "Other"])

            st.write("**Products**")
            pc1, pc2, pc3, pc4, pc5, pc6 = st.columns(6)
            hw305 = pc1.checkbox("HW305")
            hw101 = pc2.checkbox("HW101")
            hw201 = pc3.checkbox("Hw201")
            hw103 = pc4.checkbox("HW103")
            hw302 = pc5.checkbox("HW302")
            hw310 = pc6.checkbox("HW310")

            other_notes = st.text_input("Other / Remarks")
            submitted = st.form_submit_button("Add Entry")

            if submitted:
                if not mason_name:
                    st.error("Mason Name is required!")
                else:
                    save_state_for_undo()
                    new_sno = (st.session_state["data"]["S.NO"].max() + 1) if not st.session_state["data"].empty and "S.NO" in st.session_state["data"].columns else 1
                    
                    new_row = {
                        "S.NO": new_sno, "MASON CODE": mason_code, "MASON NAME": mason_name,
                        "CONTACT NUMBER": contact_number, "DLR NAME": dlr_name, "Location": location,
                        "DAY": day_val, "Category": category,
                        "HW305": "YES" if hw305 else "", "HW101": "YES" if hw101 else "",
                        "Hw201": "YES" if hw201 else "", "HW103": "YES" if hw103 else "",
                        "HW302": "YES" if hw302 else "", "HW310": "YES" if hw310 else "",
                        "other": other_notes, "Visited_Status": "", "Visited_At": "", "Registered_Status": "", "Registered_At": ""
                    }
                    st.session_state["data"] = pd.concat([st.session_state["data"], pd.DataFrame([new_row])], ignore_index=True)
                    st.session_state["data"].to_excel(DATA_FILE, index=False)
                    st.success("Entry added!")
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    
st.markdown('</div>', unsafe_allow_html=True) # Close container
