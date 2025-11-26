import streamlit as st
import streamlit.components.v1 as components  # still available if you need later
import pandas as pd
from io import BytesIO
from pathlib import Path
from datetime import datetime

# ------------ CONFIG ------------
st.set_page_config(page_title="Mason Data Manager", layout="wide")
st.markdown(
    """
    <h1 style="margin-bottom:0.2rem;">Mason Data Management System</h1>
    <p style="color:#6b7280;margin-bottom:1.2rem;">
        Track visits, registrations & product usage across your field operations.
    </p>
    """,
    unsafe_allow_html=True,
)

DATA_FILE = "mason_data.xlsx"  # persistent storage file

# ------------ GLOBAL CSS ------------
st.markdown("""
<style>
/* Overall page background + content container */
body {
    background-color: #f3f4f6;
}
.main, .block-container {
    background: #f3f4f6;
}
.block-container {
    max-width: 1180px;
    padding-top: 1rem;
    padding-bottom: 3rem;
}

/* Expander look */
.streamlit-expanderHeader {
    font-weight: 600;
    color: #111827 !important;
}
.streamlit-expanderHeader > div {
    padding: 0.75rem 0.85rem !important;
}
.css-1n76uvr, .css-1v3fvcr {
    border-radius: 12px !important;
}

/* General card look if you want to use HTML later */
.mason-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    margin-top: 1rem;
}
.mason-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    border-top: 4px solid #4f46e5;
    box-shadow: 0 10px 15px rgba(15, 23, 42, 0.08);
}

/* Style all Streamlit buttons a bit nicer */
div.stButton > button {
    border-radius: 8px;
    padding: 0.45rem 0.9rem;
    font-weight: 600;
}

/* Metrics alignment */
[data-testid="metric-container"] {
    background: #ffffff;
    border-radius: 12px;
    padding: 0.8rem 0.9rem;
    box-shadow: 0 8px 16px rgba(15, 23, 42, 0.04);
}

/* Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #f1f1f1; }
::-webkit-scrollbar-thumb { background: #c7c7c7; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #a8a8a8; }
</style>
""", unsafe_allow_html=True)

# ------------ TAILWIND (optional, still loaded) ------------
st.markdown("""
<script src="https://cdn.tailwindcss.com"></script>
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

# ------------ INITIAL DATA (HARD-CODED + PERSISTENCE) ------------

def get_initial_dataset() -> pd.DataFrame:
    """
    1. If mason_data.xlsx exists -> load & return.
    2. Else -> build from your big hardcoded dict, save to file, return.
    """
    if Path(DATA_FILE).exists():
        df = pd.read_excel(DATA_FILE)
        return clean_dataframe(df)

    # NOTE: your huge `data = { ... }` dict is kept exactly as before.
    data = {  # truncated here in explanation – keep your full dict unchanged
        "S.NO": range(1, 216),
        # ... all your existing columns ...
    }

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

# ✅ Ensure status columns exist even for older files
for col in ["Visited_Status", "Visited_At", "Registered_Status", "Registered_At"]:
    if col not in st.session_state["data"].columns:
        st.session_state["data"][col] = ""

# --- filter-related session defaults ---
if "filter_day" not in st.session_state:
    st.session_state["filter_day"] = "All"
if "filter_location" not in st.session_state:
    st.session_state["filter_location"] = "All"
if "filter_cat" not in st.session_state:
    st.session_state["filter_cat"] = "All"
if "filter_visit_status" not in st.session_state:
    st.session_state["filter_visit_status"] = "All"
if "filter_reg_status" not in st.session_state:
    st.session_state["filter_reg_status"] = "All"
if "filter_mobile_input" not in st.session_state:
    st.session_state["filter_mobile_input"] = ""
if "filter_mobile_query" not in st.session_state:
    st.session_state["filter_mobile_query"] = ""
if "filter_only_products" not in st.session_state:
    st.session_state["filter_only_products"] = False
if "filter_no_products" not in st.session_state:
    st.session_state["filter_no_products"] = False
if "reset_filters" not in st.session_state:
    st.session_state["reset_filters"] = False

# --- apply reset BEFORE widgets are created ---
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

# ------------ DATA MANAGEMENT EXPANDER ------------

with st.expander("🛠️ Data Management (Import / Add / Undo)", expanded=False):

    # Undo
    if st.session_state["prev_data"] is not None:
        if st.button("↩️ Undo Last Change", type="primary"):
            st.session_state["data"] = st.session_state["prev_data"]
            st.session_state["prev_data"] = None
            st.session_state["data"].to_excel(DATA_FILE, index=False)
            st.success("Restored previous version!")
            st.rerun()

    op_tab1, op_tab2 = st.tabs(["➕ Add Single Entry", "📂 Import Excel"])

    # --- IMPORT TAB ---
    with op_tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.info("Step 2: Upload Data")
            uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
            if uploaded_file is not None:
                if st.button("Load Data"):
                    new_data = load_excel_data(uploaded_file)
                    if new_data is not None:
                        save_state_for_undo()
                        st.session_state["data"] = new_data
                        for col in ["Visited_Status", "Visited_At", "Registered_Status", "Registered_At"]:
                            if col not in st.session_state["data"].columns:
                                st.session_state["data"][col] = ""
                        st.session_state["data"].to_excel(DATA_FILE, index=False)
                        st.success(f"Loaded {len(new_data)} rows and saved to {DATA_FILE}!")
                        st.rerun()

    # --- ADD ENTRY TAB ---
    with op_tab1:
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
                    ["MONDAY", "TUESDAY", "WEDNESDAY",
                     "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"],
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

                    st.success("Entry added & saved!")
                    st.rerun()
        with col2:
            st.info("Step 1: Download Template")
            st.download_button(
                label="📄 Download Blank Excel Template",
                data=get_template_excel(),
                file_name="mason_data_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

# ------------ FILTER SECTION ------------

with st.expander("🔍 Filter Data", expanded=True):
    base_df = st.session_state["data"].copy()

    # --- FIRST ROW: Day, Location, Category, Product flags ---
    fc1, fc2, fc3, fc4 = st.columns(4)

    # Day (drives cascading)
    with fc1:
        st.markdown("**📅 Day**")
        days_list = [
            str(x).strip()
            for x in base_df.get("DAY", "").unique()
            if str(x).strip()
        ]
        days = ["All"] + sorted(set(days_list))
        selected_day = st.selectbox(
            "",
            days,
            key="filter_day",
        )

    # Filtered df for next-level cascading (Location)
    df_for_location = base_df.copy()
    if selected_day != "All":
        df_for_location = df_for_location[df_for_location["DAY"] == selected_day]

    # Location depends on Day
    with fc2:
        st.markdown("**📍 Location**")
        locs = [
            str(x).strip()
            for x in df_for_location.get("Location", "").unique()
            if str(x).strip()
        ]
        locations = ["All"] + sorted(set(locs))
        selected_location = st.selectbox(
            "",
            locations,
            key="filter_location",
        )

    # Filtered df for Category
    df_for_category = df_for_location.copy()
    if selected_location != "All":
        df_for_category = df_for_category[df_for_category["Location"] == selected_location]

    with fc3:
        st.markdown("**🏷️ Category**")
        cats_raw = [
            str(x).strip()
            for x in df_for_category.get("Category", "").unique()
            if str(x).strip() != ""
        ]
        cats = ["All"] + sorted(set(cats_raw))
        has_blank = (df_for_category.get("Category", "") == "").any()
        if has_blank:
            cats.append("Blank / Uncategorized")

        selected_cat = st.selectbox(
            "",
            cats,
            key="filter_cat",
        )

    with fc4:
        st.markdown("**📦 Product Visibility**")
        show_only_products = st.checkbox(
            "Has Products",
            key="filter_only_products",
        )
        show_no_products = st.checkbox(
            "No Products",
            key="filter_no_products",
        )

    # --- SECOND ROW: Visited / Registered ---
    vc1, vc2 = st.columns(2)
    with vc1:
        st.markdown("**🧭 Visited Status**")
        visit_filter = st.selectbox(
            "",
            ["All", "Visited", "Not Visited"],
            key="filter_visit_status",
        )
    with vc2:
        st.markdown("**📝 Registered Status**")
        reg_filter = st.selectbox(
            "",
            ["All", "Registered", "Not Registered"],
            key="filter_reg_status",
        )

    # --- THIRD ROW: Mobile Search + Buttons ---
    mc1, mc2, mc3 = st.columns([3, 1, 1])
    with mc1:
        st.markdown("**📱 Search by Mobile Number**")
        st.session_state["filter_mobile_input"] = st.text_input(
            "",
            value=st.session_state.get("filter_mobile_input", ""),
            placeholder="Enter full or partial number...",
        )
    with mc2:
        st.markdown("&nbsp;", unsafe_allow_html=True)
        if st.button("Search", key="btn_mobile_search"):
            st.session_state["filter_mobile_query"] = st.session_state["filter_mobile_input"].strip()
            st.rerun()
    with mc3:
        st.markdown("&nbsp;", unsafe_allow_html=True)
        if st.button("🔄 Reset Filters", key="btn_reset_filters"):
            st.session_state["reset_filters"] = True
            st.rerun()

# Now apply filters to a fresh copy for display
df_display = st.session_state["data"].copy()

if not df_display.empty:
    # Day filter
    selected_day = st.session_state.get("filter_day", "All")
    if selected_day != "All":
        df_display = df_display[df_display["DAY"] == selected_day]

    # Location filter
    selected_location = st.session_state.get("filter_location", "All")
    if selected_location != "All":
        df_display = df_display[df_display["Location"] == selected_location]

    # Category filter
    selected_cat = st.session_state.get("filter_cat", "All")
    if selected_cat == "Blank / Uncategorized":
        df_display = df_display[
            df_display["Category"].isna() | (df_display["Category"] == "")
        ]
    elif selected_cat != "All":
        df_display = df_display[df_display["Category"] == selected_cat]

    # Visited filter
    visit_filter = st.session_state.get("filter_visit_status", "All")
    if "Visited_Status" in df_display.columns:
        if visit_filter == "Visited":
            df_display = df_display[df_display["Visited_Status"] == "Visited"]
        elif visit_filter == "Not Visited":
            df_display = df_display[
                (df_display["Visited_Status"].isna()) |
                (df_display["Visited_Status"] == "")
            ]

    # Registered filter
    reg_filter = st.session_state.get("filter_reg_status", "All")
    if "Registered_Status" in df_display.columns:
        if reg_filter == "Registered":
            df_display = df_display[df_display["Registered_Status"] == "Registered"]
        elif reg_filter == "Not Registered":
            df_display = df_display[
                (df_display["Registered_Status"].isna()) |
                (df_display["Registered_Status"] == "")
            ]

    # Product filters
    hw_cols = ["HW305", "HW101", "Hw201", "HW103", "HW302", "HW310"]
    show_only_products = st.session_state.get("filter_only_products", False)
    show_no_products = st.session_state.get("filter_no_products", False)

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

    # Mobile (contact) search filter
    mobile_query = st.session_state.get("filter_mobile_query", "")
    if mobile_query and "CONTACT NUMBER" in df_display.columns:
        contact_str = df_display["CONTACT NUMBER"].astype(str).str.replace(".0", "", regex=False)
        df_display = df_display[
            contact_str.str.contains(mobile_query, case=False, na=False)
        ]

# ------------ METRICS ------------

st.markdown("### 📊 Dashboard Overview")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Masons", len(st.session_state["data"]))
m2.metric("Visible Rows", len(df_display))
m3.metric(
    "Unique Locations (Filtered)",
    df_display["Location"].nunique() if "Location" in df_display.columns else 0,
)
m4.metric(
    "Unique DLRs (Filtered)",
    df_display["DLR NAME"].nunique() if "DLR NAME" in df_display.columns else 0,
)

st.divider()

# ------------ MAIN TABS ------------

tab_cards, tab_graphs, tab_data = st.tabs(
    ["📇 Mason Cards", "📈 Analytics", "📝 Data Editor"]
)

# ----- CARDS TAB (WITH ACTION BUTTONS) -----
with tab_cards:
    st.subheader("Mason Directory")

    df_cards = df_display.copy()

    if df_cards.empty:
        st.info("No masons found matching filters.")
    else:
        for idx, row in df_cards.iterrows():
            code = row.get("MASON CODE", "N/A")
            name = row.get("MASON NAME", "Unknown")
            cat = row.get("Category", "N/A") or "N/A"
            contact = str(row.get("CONTACT NUMBER", "")).replace(".0", "").strip()
            loc = row.get("Location", "") or "N/A"
            dlr = row.get("DLR NAME", "") or "N/A"
            day = row.get("DAY", "") or "N/A"

            visited_status = row.get("Visited_Status", "")
            registered_status = row.get("Registered_Status", "")

            hw_cols = ["HW305", "HW101", "Hw201", "HW103", "HW302", "HW310"]
            prod_list = [
                p.upper()
                for p in hw_cols
                if p in row and isinstance(row[p], str) and "YES" in row[p].upper()
            ]

            with st.container(border=True):
                header_cols = st.columns([4, 1])
                with header_cols[0]:
                    st.markdown(f"**{name}**")
                    st.caption(code)
                with header_cols[1]:
                    st.markdown(
                        f"<div style='text-align:right;'><span style='font-size:0.75rem;padding:3px 8px;border-radius:6px;background:#e5e7eb;color:#374151;'>{cat}</span></div>",
                        unsafe_allow_html=True,
                    )

                st.write(f"**Contact:**  {contact}")
                st.write(f"**Location:**  {loc}")
                st.write(f"**DLR:**  {dlr}")
                st.write(f"**Day:**  :blue[{day}]")

                st.write(
                    "**Products:** "
                    + (", ".join(prod_list) if prod_list else "_No products listed_")
                )

                # Show current status on card
                status_line = []
                if visited_status:
                    status_line.append("🧭 Visited")
                if registered_status:
                    status_line.append("📝 Registered")
                if status_line:
                    st.caption("Status: " + ", ".join(status_line))

                st.markdown("---")

                b_call, b_visit, b_reg = st.columns(3)

                # CALL BUTTON (HTML link, color #813405)
                with b_call:
                    if contact and contact.lower() != "nan":
                        st.markdown(
                            f"""
                            <a href="tel:{contact}" style="
                                display:inline-flex;
                                justify-content:center;
                                align-items:center;
                                width:100%;
                                padding:0.5rem 0.9rem;
                                border-radius:8px;
                                background:#813405;
                                color:#ffffff;
                                font-weight:600;
                                text-decoration:none;
                            ">
                                📲 Call
                            </a>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            """
                            <div style="
                                width:100%;
                                padding:0.5rem 0.9rem;
                                border-radius:8px;
                                background:#cbd5f5;
                                color:#4b5563;
                                font-weight:600;
                                text-align:center;
                            ">
                                No Contact
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                # VISITED BUTTON (Streamlit)
                with b_visit:
                    label = "🧭 Visited" if not visited_status else "✅ Visited"
                    if st.button(label, key=f"visit_{code}_{idx}"):
                        save_state_for_undo()
                        mask = st.session_state["data"]["MASON CODE"] == code
                        st.session_state["data"].loc[mask, "Visited_Status"] = "Visited"
                        st.session_state["data"].loc[mask, "Visited_At"] = datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        st.session_state["data"].to_excel(DATA_FILE, index=False)
                        st.success(f"Marked {name} as visited.")
                        st.rerun()

                # REGISTERED BUTTON (Streamlit)
                with b_reg:
                    label = "📝 Registered" if not registered_status else "✅ Registered"
                    if st.button(label, key=f"reg_{code}_{idx}"):
                        save_state_for_undo()
                        mask = st.session_state["data"]["MASON CODE"] == code
                        st.session_state["data"].loc[mask, "Registered_Status"] = "Registered"
                        st.session_state["data"].loc[mask, "Registered_At"] = datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        st.session_state["data"].to_excel(DATA_FILE, index=False)
                        st.success(f"Marked {name} as registered.")
                        st.rerun()

# ----- ANALYTICS TAB -----
with tab_graphs:
    st.subheader("Visual Analytics")
    if not df_display.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Masons per Location (Filtered)**")
            if "Location" in df_display.columns:
                st.bar_chart(df_display["Location"].value_counts())
        with col2:
            st.write("**Masons per Day (Filtered)**")
            if "DAY" in df_display.columns:
                st.bar_chart(df_display["DAY"].value_counts())

        col3, col4 = st.columns(2)
        hw_cols = ["HW305", "HW101", "Hw201", "HW103", "HW302", "HW310"]
        with col3:
            st.write("**Product Popularity**")
            available = [c for c in hw_cols if c in df_display.columns]
            if available:
                counts = df_display[available].apply(
                    lambda x: x.astype(str).str.contains("YES", case=False).sum()
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

    if not st.session_state["data"].empty:
        st.download_button(
            "📥 Download Full Current Report (All Masons)",
            to_excel(st.session_state["data"]),
            "mason_full_report.xlsx",
        )
