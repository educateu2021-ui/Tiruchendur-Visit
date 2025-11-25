import streamlit as st
import pandas as pd
from io import BytesIO

# Set page configuration
st.set_page_config(page_title="Mason Data Manager", layout="wide")

st.title("Mason Data Management System")

# --- TAILWIND CSS & CUSTOM STYLES ---
# We inject Tailwind via CDN to match the HTML design exactly
st.markdown("""
<script src="https://cdn.tailwindcss.com"></script>
<style>
    /* Ensure the grid container works well within Streamlit */
    .stMarkdown {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---

def get_template_excel():
    """Generates an empty template file with correct headers"""
    columns = [
        "S.NO", "MASON CODE", "MASON NAME", "CONTACT NUMBER", 
        "DLR NAME", "Location", "DAY", "Category", 
        "HW305", "HW101", "Hw201", "HW103", "HW302", "HW310", "other"
    ]
    df_template = pd.DataFrame(columns=columns)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_template.to_excel(writer, index=False, sheet_name='Template')
    return output.getvalue()

def load_excel_data(uploaded_file):
    """Helper to read excel and standardize columns"""
    try:
        df = pd.read_excel(uploaded_file)
        df = df.fillna("")
        if "S.NO" in df.columns:
            df["S.NO"] = pd.to_numeric(df["S.NO"], errors='coerce').fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def save_state_for_undo():
    """Saves the current dataframe to history before making changes"""
    st.session_state['prev_data'] = st.session_state['data'].copy()

# --- Session State Initialization ---
if 'data' not in st.session_state:
    # Initialize with SAMPLE DATA
    sample_data = [
        {"S.NO": 1, "MASON CODE": "M100258", "MASON NAME": "C.PRABHAKARAN", "CONTACT NUMBER": "9487049215", "DLR NAME": "RAJA TRADERS", "Location": "TIRUCHENDUR", "DAY": "MONDAY", "Category": "E", "HW305": "YES", "HW101": "YES", "Hw201": "YES", "HW103": "YES", "HW302": "", "HW310": "", "other": ""},
        {"S.NO": 2, "MASON CODE": "M100259", "MASON NAME": "C.SUDHAKARAN", "CONTACT NUMBER": "9443460152", "DLR NAME": "RAJA TRADERS", "Location": "TIRUCHENDUR", "DAY": "MONDAY", "Category": "E", "HW305": "YES", "HW101": "YES", "Hw201": "YES", "HW103": "YES", "HW302": "", "HW310": "", "other": ""},
        {"S.NO": 3, "MASON CODE": "M100260", "MASON NAME": "PECHIMUTHU", "CONTACT NUMBER": "9842120938", "DLR NAME": "SRI VALLI AGENCY", "Location": "ALWARTHIRUNAGIRI", "DAY": "SATURDAY", "Category": "E", "HW305": "YES", "HW101": "YES", "Hw201": "YES", "HW103": "", "HW302": "", "HW310": "", "other": ""},
        {"S.NO": 6, "MASON CODE": "M100263", "MASON NAME": "PERUMAL", "CONTACT NUMBER": "9486204932", "DLR NAME": "SUNDER RAJ HARDWARES", "Location": "PEIKULAM", "DAY": "FRIDAY", "Category": "E", "HW305": "YES", "HW101": "YES", "Hw201": "YES", "HW103": "", "HW302": "", "HW310": "", "other": ""},
        {"S.NO": 9, "MASON CODE": "M100266", "MASON NAME": "THANGARAJ", "CONTACT NUMBER": "9976110550", "DLR NAME": "PERUMAL KONAR SONS", "Location": "SRIVAIGUNDAM", "DAY": "THURSDAY", "Category": "E", "HW305": "YES", "HW101": "YES", "Hw201": "", "HW103": "", "HW302": "", "HW310": "", "other": ""}
    ]
    st.session_state['data'] = pd.DataFrame(sample_data)

if 'prev_data' not in st.session_state:
    st.session_state['prev_data'] = None

# --- TOP SECTION: Data Operations (Collapsible) ---
with st.expander("🛠️ Data Management (Import / Add / Undo)", expanded=False):
    
    if st.session_state['prev_data'] is not None:
        if st.button("↩️ Undo Last Change", type="primary"):
            st.session_state['data'] = st.session_state['prev_data']
            st.session_state['prev_data'] = None 
            st.success("Restored previous version!")
            st.rerun()
    
    op_tab1, op_tab2 = st.tabs(["📂 Import Excel", "➕ Add Single Entry"])
    
    with op_tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.info("Step 1: Download Template")
            st.download_button(
                label="📄 Download Blank Excel Template",
                data=get_template_excel(),
                file_name='mason_data_template.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        with col2:
            st.info("Step 2: Upload Data")
            uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls'])
            if uploaded_file is not None:
                if st.button("Load Data"):
                    new_data = load_excel_data(uploaded_file)
                    if new_data is not None:
                        save_state_for_undo()
                        st.session_state['data'] = new_data
                        st.success(f"Loaded {len(new_data)} rows!")
                        st.rerun()
    
    with op_tab2:
        with st.form("entry_form"):
            c1, c2, c3 = st.columns(3)
            with c1: mason_code = st.text_input("Mason Code")
            with c2: mason_name = st.text_input("Mason Name")
            with c3: contact_number = st.text_input("Contact Number")
            
            c4, c5, c6, c7 = st.columns(4)
            with c4: dlr_name = st.text_input("DLR Name")
            with c5: location = st.text_input("Location")
            with c6: day = st.selectbox("Day", ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"])
            with c7: category = st.selectbox("Category", ["E", "M", "Other"])
            
            st.write("**Products (Check box for YES)**")
            pc1, pc2, pc3, pc4, pc5, pc6 = st.columns(6)
            with pc1: hw305 = st.checkbox("HW305")
            with pc2: hw101 = st.checkbox("HW101")
            with pc3: hw201 = st.checkbox("Hw201")
            with pc4: hw103 = st.checkbox("HW103")
            with pc5: hw302 = st.checkbox("HW302")
            with pc6: hw310 = st.checkbox("HW310")
            
            other_notes = st.text_input("Other / Remarks")
            submitted = st.form_submit_button("Add Line Item")

            if submitted:
                if not mason_name:
                    st.error("Mason Name is required!")
                else:
                    save_state_for_undo()
                    new_sno = len(st.session_state['data']) + 1 if 'S.NO' in st.session_state['data'].columns else 1
                    new_row = {
                        "S.NO": new_sno, "MASON CODE": mason_code, "MASON NAME": mason_name, "CONTACT NUMBER": contact_number,
                        "DLR NAME": dlr_name, "Location": location, "DAY": day, "Category": category,
                        "HW305": "YES" if hw305 else "", "HW101": "YES" if hw101 else "", "Hw201": "YES" if hw201 else "",
                        "HW103": "YES" if hw103 else "", "HW302": "YES" if hw302 else "", "HW310": "YES" if hw310 else "",
                        "other": other_notes
                    }
                    st.session_state['data'] = pd.concat([st.session_state['data'], pd.DataFrame([new_row])], ignore_index=True)
                    st.success("Entry added!")
                    st.rerun()

# --- FILTER SECTION (Collapsible) ---
with st.expander("🔍 Filter Data", expanded=True):
    df_display = st.session_state['data'].copy()
    fc1, fc2, fc3, fc4 = st.columns(4)
    
    with fc1:
        locations = ["All"] + sorted(list(df_display["Location"].unique())) if "Location" in df_display.columns else ["All"]
        selected_location = st.selectbox("📍 Location", locations)
        
    with fc2:
        days = ["All"] + sorted(list(df_display["DAY"].unique())) if "DAY" in df_display.columns else ["All"]
        selected_day = st.selectbox("📅 Day", days)
        
    with fc3:
        cats = ["All"] + sorted(list(df_display["Category"].unique())) if "Category" in df_display.columns else ["All"]
        selected_cat = st.selectbox("🏷️ Category", cats)
        
    with fc4:
        st.write("**Product Visibility**")
        show_only_products = st.checkbox("Has Products")
        show_no_products = st.checkbox("No Products")

# --- Apply Filters Logic ---
if not df_display.empty:
    if selected_location != "All": df_display = df_display[df_display["Location"] == selected_location]
    if selected_day != "All": df_display = df_display[df_display["DAY"] == selected_day]
    if selected_cat != "All": df_display = df_display[df_display["Category"] == selected_cat]
        
    hw_cols = ["HW305", "HW101", "Hw201", "HW103", "HW302", "HW310"]
    if show_only_products:
        mask = df_display[hw_cols].apply(lambda x: x.astype(str).str.contains('YES', case=False).any(), axis=1)
        df_display = df_display[mask]
    if show_no_products:
        mask = df_display[hw_cols].apply(lambda x: not x.astype(str).str.contains('YES', case=False).any(), axis=1)
        df_display = df_display[mask]

# --- Metrics Section ---
st.markdown("### 📊 Dashboard Overview")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Masons", len(st.session_state['data']))
m2.metric("Visible Rows", len(df_display))
m3.metric("Unique Locations", df_display["Location"].nunique() if "Location" in df_display.columns else 0)
m4.metric("Unique DLRs", df_display["DLR NAME"].nunique() if "DLR NAME" in df_display.columns else 0)

st.divider()

# --- Main Tabs ---
tab_cards, tab_graphs, tab_data = st.tabs(["📇 Mason Cards", "📈 Analytics", "📝 Data Editor"])

with tab_cards:
    if not df_display.empty:
        # Start the Grid Container using Tailwind classes
        html_content = '<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">'
        
        for index, row in df_display.iterrows():
            # Data Extraction
            name = row.get("MASON NAME", "Unknown")
            code = row.get("MASON CODE", "N/A")
            cat = row.get("Category", "N/A")
            contact = str(row.get("CONTACT NUMBER", "")).replace(".0", "").strip()
            loc = row.get("Location", "")
            dlr = row.get("DLR NAME", "")
            day = row.get("DAY", "")
            
            # Products Badge Logic
            products_html = ""
            hw_cols = ["HW305", "HW101", "Hw201", "HW103", "HW302", "HW310"]
            has_prod = False
            for p in hw_cols:
                if p in row and 'YES' in str(row[p]).upper():
                    products_html += f'<span class="inline-block bg-indigo-100 text-indigo-800 text-xs font-medium px-2.5 py-0.5 rounded-full border border-indigo-200 mr-1 mb-1">{p}</span>'
                    has_prod = True
            
            if not has_prod:
                products_html = '<span class="text-xs text-slate-400 italic">No products listed</span>'

            # Call Button Logic
            if contact and contact.lower() != "nan" and contact != "":
                call_btn = f"""
                <a href="tel:{contact}" class="inline-flex items-center justify-center w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md transition-colors mt-3">
                    <span class="mr-2">📞</span> Call Now
                </a>
                """
            else:
                call_btn = """
                <button disabled class="inline-flex items-center justify-center w-full px-4 py-2 bg-slate-300 text-slate-500 text-sm font-medium rounded-md mt-3 cursor-not-allowed">
                    No Contact
                </button>
                """

            # Exact HTML Structure from Reference
            card = f"""
            <div class="bg-white rounded-lg shadow p-5 flex flex-col transition-all duration-300 hover:shadow-lg border-t-4 border-indigo-500">
                <div class="mb-3">
                    <h3 class="text-xl font-bold text-slate-800">{name}</h3>
                    <div class="flex justify-between items-center">
                        <p class="text-sm text-slate-500 font-medium">{code}</p>
                        <span class="bg-slate-100 text-slate-600 text-xs px-2 py-1 rounded">{cat}</span>
                    </div>
                </div>
                <div class="space-y-2 text-sm text-slate-700 mb-4 flex-grow">
                    <p class="flex items-start"><span class="w-24 font-semibold text-slate-500">Contact:</span> {contact}</p>
                    <p class="flex items-start"><span class="w-24 font-semibold text-slate-500">Location:</span> {loc}</p>
                    <p class="flex items-start"><span class="w-24 font-semibold text-slate-500">DLR:</span> {dlr}</p>
                    <p class="flex items-start"><span class="w-24 font-semibold text-slate-500">Day:</span> <span class="font-semibold text-indigo-700">{day}</span></p>
                </div>
                <div class="mt-auto pt-3 border-t border-slate-200">
                    <h4 class="text-xs font-semibold text-slate-600 mb-2">Products:</h4>
                    <div class="flex flex-wrap gap-2 mb-3">
                        {products_html}
                    </div>
                    {call_btn}
                </div>
            </div>
            """
            html_content += card
            
        html_content += "</div>"
        st.markdown(html_content, unsafe_allow_html=True)
    else:
        st.info("No masons found matching filters.")

with tab_graphs:
    st.subheader("Visual Analytics")
    if not df_display.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Masons per Location**")
            if "Location" in df_display.columns: st.bar_chart(df_display["Location"].value_counts())
        with col2:
            st.write("**Masons per Day**")
            if "DAY" in df_display.columns: st.bar_chart(df_display["DAY"].value_counts())

        col3, col4 = st.columns(2)
        with col3:
            st.write("**Product Popularity**")
            hw_cols = ["HW305", "HW101", "Hw201", "HW103", "HW302", "HW310"]
            available = [c for c in hw_cols if c in df_display.columns]
            if available:
                counts = df_display[available].apply(lambda x: x.astype(str).str.contains('YES', case=False).sum())
                st.bar_chart(counts)
        with col4:
            st.write("**Category Distribution**")
            if "Category" in df_display.columns: st.bar_chart(df_display["Category"].value_counts())

with tab_data:
    st.subheader("Raw Data Table (Editable)")
    column_config = {
        "CONTACT NUMBER": st.column_config.LinkColumn("Contact", display_text=r"(\+?[0-9]*)"),
        "HW305": st.column_config.TextColumn("HW305", width="small"),
        "HW101": st.column_config.TextColumn("HW101", width="small"),
        "Hw201": st.column_config.TextColumn("Hw201", width="small"),
        "HW103": st.column_config.TextColumn("HW103", width="small"),
        "HW302": st.column_config.TextColumn("HW302", width="small"),
        "HW310": st.column_config.TextColumn("HW310", width="small"),
    }
    if not df_display.empty and "CONTACT NUMBER" in df_display.columns:
        df_display["CONTACT NUMBER"] = df_display["CONTACT NUMBER"].astype(str)

    edited_df = st.data_editor(df_display, num_rows="dynamic", use_container_width=True, height=500, column_config=column_config)

    st.write("---")
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='MasonData')
        return output.getvalue()
    if not df_display.empty:
        st.download_button("📥 Export Filtered Data to Excel", to_excel(df_display), 'mason_data_export.xlsx')
