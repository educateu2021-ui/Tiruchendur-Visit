import streamlit as st
import pandas as pd
from io import BytesIO

# Set page configuration must be the first streamlit command
st.set_page_config(page_title="Mason Data Manager", layout="wide")

st.title("Mason Data Management System")

# --- TAILWIND CSS & CUSTOM STYLES ---
st.markdown("""
<script src="https://cdn.tailwindcss.com"></script>
<style>
    /* Ensure the grid container works well within Streamlit */
    .stMarkdown {
        width: 100%;
    }
    /* Custom Scrollbar for better aesthetics */
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
        # Normalize headers (remove extra spaces like 'Category ')
        df.columns = [c.strip() for c in df.columns]
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

# --- PRE-LOADED DATA (From your test 1.xlsx) ---
# This function loads the data you provided so it's always there on startup.
def get_initial_dataset():
    # We construct the dataframe directly. 
    # NOTE: I am loading the full CSV data structure here.
    data = {
        "S.NO": range(1, 216),
        "MASON CODE": ["M100258", "M100259", "M100260", "M100261", "M100262", "M100263", "M100264", "M100265", "M100266", "M100267", "M100268", "M100270", "M100271", "M100272", "M100273", "M100276", "M100290", "M103410", "M103411", "M103412", "M103413", "M103414", "M103415", "M103416", "M103417", "M103418", "M103419", "M103420", "M103421", "M103422", "M103423", "M103424", "M103425", "M103426", "M103411", "M103427", "M103429", "M104009", "M104011", "M104012", "M105830", "M105831", "M105835", "M106738", "M106739", "M106740", "M106741", "M106752", "M109420", "M112390", "M115196", "M115197", "M115198", "M115199", "M115200", "M115201", "M116145", "M119871", "M121996", "M123673", "M123689", "M129493", "M131585", "M131586", "M131587", "M131759", "M131760", "M131762", "M131916", "M132228", "M133092", "M133208", "M142615", "M144358", "M144601", "M146156", "M146159", "M146786", "M148793", "M149919", "M150738", "M151271", "M152371", "M152481", "M152661", "M152737", "M152857", "M153518", "M154050", "M154051", "M154753", "M154805", "M154848", "M154891", "M154994", "M155379", "M155380", "M155990", "M155995", "M156233", "M156476", "M156578", "M156800", "M157794", "M158421", "M158609", "M158901", "M159030", "M159036", "M159089", "M159008", "M159040", "M159143", "M159179", "M159221", "M159239", "M159495", "M159587", "M159588", "M159858", "M159866", "M156191", "M160161", "M160198", "M160442", "M160497", "M161240", "M161747", "M162303", "M162629", "M163111", "M163154", "M163263", "M163264", "M163299", "M163833", "M163849", "M163991", "M164049", "M164076", "M164217", "M164424", "M164685", "M164686", "M166022", "M166074", "M166076", "M166668", "M167243", "M167757", "M168106", "M168106", "M168677", "M168850", "M168963", "M169303", "M169393", "M169418", "M169600", "M169684", "M169685", "M169701", "M169703", "M169709", "M170017", "M171007", "M171434", "M171461", "M171484", "M172171", "M172592", "M172925", "M172926", "M176313", "M176331", "M176333", "M176334", "M176336", "M176424", "M176494", "M176512", "M176513", "M176514", "M176519", "M176520", "M176521", "M176528", "M176529", "M176530", "M176533", "M176544", "M176545", "M176551", "M176555", "M178257", "M178566", "M179206", "M179361", "M179767", "M180309", "M180889", "M181502", "M181503", "M181504", "M181505", "M181506", "M181507", "M181508", "M181509", "M181511", "M181512", "M182130", "M182217", "M182246", "M182392"],
        "MASON NAME": ["C.PRABHAKARAN", "C.SUDHAKARAN", "PECHIMUTHU", "E.ENAMUTHU", "K.MURUGAN", "PERUMAL", "M.KALIMUTHU", "T.ANTONY", "THANGARAJ", "A.SUBRAMANIAN", "M.SENTHIL KUMAR", "S.MUTHURMMAN", "M.MUTHUKUMAR", "THEIVENDRAN", "SUBRAMANIAN", "J.SIVA", "D. Antonyraj", "kartheesan", "Sivasubramaniyan. m", "Laxmanan. m", "Kumar. D", "Vettumpermal", "Rajan. G", "Laxshman. N", "Sakthikumar. k", "Mariappan.N", "Chinnadurai. p", "Shunmugavel.S", "Patturaja.M", "Raja.N", "esakkimuthu", "Senthi. M", "iyyappan. b", "Muthupandi.s", "mshaik mohaned salih. M", "Esakkimuthu", "Muthusamy.P", "Arumugasundram. N", "Paramasivan. m", "Easkimuthu. V", "Balasubramani.R", "Thanjar.S", "Muniysamy.K", "Nagamani", "Kombiah", "Chandur", "Natarajan", "Balamurugan", "Raja M", "Thirumani", "Murugan", "Chinnadurai", "Sudalaikannu", "Nallasivan", "Mariappan", "Venkatesan", "Johnson Israel selvaraj", "Arumugasundaram", "Marimuthu", "Abdul Jalil", "Syed masood", "Sankarapandi", "Arunachalam", "Ravi", "Gunasekar", "Manikandan", "Thirumal", "Velmurugan", "Mr. Dharmaraj", "Mr. Kumaresan", "Radhakrishnan", "S. Kalimuthu", "Mohamed Salim Ibrahim", "Parvathinadhan", "Perinbaraj Mose", "Suresh", "Vijayakumar", "Elangamani", "Ramar", "muthukarupan", "esaki", "sulthanfarook ali", "kalidoss", "chinnadurai", "sudalai muthu", "ANTONY VISUWAAS BREEN", "Jeyanth joel", "JACOB JOHNSON", "ESAKKIMUTHU", "VAIRAVAN", "Murugan", "Narayana perumal", "sandhanamariappan", "Arumugam", "P.JERAVIN", "Muthuraman", "Jenifer", "Dhamothara pandiyan", "Kanagaraj g", "Santhanamariappan", "Marimuthu v", "Jebaraj", "Thadikaran", "Poovudira pandi", "Vandimalaiyan s", "Perumal", "Arumugam p", "Ananthababu R", "Rathakrishnan", "Gayathri", "MUTHUKUMAR", "PHILAVENDRIRARAJ", "BERLIN K", "Arumugam", "IMMANUEL", "PALANANDAVAR", "Diwkar M", "ROBISTON THOMMAI JESUVA", "ANTONY MICHAELRAJ", "Dharmalingam", "Kalimuthu", "Suresh", "Johnson", "SEBASTIN AJESH P", "GNANAKKAN G", "Rethinaraj", "Antony Ramesh", "Kantharaj", "Palpandi i", "Antony", "Murugan", "AYYAPPAN", "Sudalai", "Sundhar", "korkaimaran", "CHANDUR", "MUTHUKRISHNAN", "Mundasamy", "Rajan", "K.GURUNATHAN", "Ravuthan", "Sivan Perumal", "Arulwilson", "Sivasubramanian", "Antony john simon britto", "Sudalaikan N", "Raja v", "Periyasam", "Mohamed meera sahib nibra", "Ramesh durai", "Antony raj", "Nainar k", "Krishnan", "Eswaran", "Ramakrishnan", "Krishnakumar", "Velmurugan", "Muthumalai", "Selvan", "Stephenson", "Muthumalai", "Patturai", "Patturai", "M Murali", "Selvakumar", "Mariyappan", "Ramanathan", "Sudalaimuthu", "Madasamy", "Sankar", "Ganesh", "Kannan", "Prabagar", "Perumal", "Sivasubramanian", "suyambulingam", "Jeya jothilingam", "murugan", "Aavalara san", "Ithatyappan", "Muppidadhi", "Senthilkumaran", "Muthukumar", "Senthilkumaran", "Ruban", "Manikandan", "Manikandan", "Malaiyandi", "Ramasamy", "Kuthalingam", "Mohamed seyed", "Issac micheal", "Abulthahcer.h", "Ganesan", "Palanselvam U", "Selvakumar T", "N Kali", "G.NILAGL P", "Jegandhan", "Edwin", "Terrilkalmaida", "CHITHIRAVEL", "THANGARAJ", "CHINNADURAI", "MURUGAN", "MURUGAN", "KANNAN", "NAMACHIVAYAM", "KARUPPSWAMY", "MADASAMY", "APPADURAI", "VADIVEL", "Thanaseelan s", "Mudisuttumperumal", "Kannan", "Balasubramanian"],
        "CONTACT NUMBER": ["9487049215", "9443460152", "9842120938", "9952873843", "9842367551", "9486204932", "8526525676", "9944329680", "9976110550", "9659517567", "9600989040", "9894025362", "9442908007", "9965908507", "9786143454", "9943791775", "9944694668", "9750165050", "8189846659", "9965464055", "9698258998", "9865989322", "8612119932", "9442356467", "9698950226", "95242637893", "9787124426", "9488961827", "9047628631", "9894480025", "9865783829", "9750182977", "9585851996", "9944386811", "9942746446", "9626685356", "9976068541", "9489410950", "9442293406", "9655658959", "9043413513", "9791655909", "9940935692", "9840782301", "9659555993", "8015809804", "9698885610", "9943270921", "9715113576", "9486760671", "9488474675", "9715337465", "9003848557", "9842680193", "9787179090", "8760241158", "9442913255", "9488106172", "8903154860", "8344717293", "9965022538", "9942202475", "9715605434", "9952272101", "9788340001", "8248048528", "9715966606", "6369554643", "9698846828", "8300859385", "7695906977", "9942777426", "7598361730", "9965306692", "9965099475", "9566885201", "9791654823", "9842271456", "9486213434", "7639597727", "6381137857", "9944765793", "9442274010", "9486551486", "6379202929", "9361685257", "9361878528", "9003080311", "9342394625", "9585563209", "9843912991", "9443422071", "9486471385", "9965856279", "7502020617", "9345892154", "9629898388", "9789254424", "9486658242", "8248024869", "7548870404", "9659741949", "9361037308", "9489430263", "9865010809", "9787259588", "8946050345", "9842391346", "9677509731", "6380749992", "9500962322", "8973977016", "7010907798", "8925150192", "9715005282", "9751916964", "9486475883", "9442834087", "9442834086", "6381734359", "8526309288", "9578582874", "9442002380", "8056969040", "6379075538", "6381533004", "9486881401", "9791060379", "9677010133", "7373922692", "9500347110", "97896489123", "9787599944", "8778262410", "9942031354", "8610605582", "9944027933", "9488681750", "9597107206", "9965344057", "8124837467", "9486450347", "9894774196", "9442061725", "9842616545", "9751455767", "9789247946", "9585934531", "9994433889", "6385220023", "9487835495", "9676136127", "8220758537", "9047466137", "7530052711", "9940918154", "9976939927", "9790309708", "9442886674", "9003670350", "8508588820", "9976636262", "8015150354", "7708462080", "9788732335", "8778226346", "9047440050", "7708369210", "9688951686", "7538811718", "9786195253", "9789449732", "9976785554", "8122248503", "8883634414", "9688102493", "9965659766", "9095737053", "9345070510", "9976071454", "9751009175", "6381832038", "9486379177", "9788131437", "9786355657", "8610960582", "9489913543", "9080296416", "7373359984", "9976921232", "9943232912", "9942923441", "7449259203", "9688107678", "8122248503", "9025416873", "8883634414", "9944445980", "9092371148", "9944835972", "6380667977", "9790309281", "9600713737", "9578785380", "9578785380", "9865511557", "8870300205", "9488680011", "9788695344", "9626550340", "9976233341", "8940012944", "9941714172", "7010286796"],
        "DLR NAME": ["RAJA TRADERS", "RAJA TRADERS", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "SUNDER RAJ HARDWARES", "SUNDER RAJ HARDWARES", "", "PERUMAL KONAR SONS", "SRI SAKTHI ELECTRICALS", "SRI SAKTHI ELECTRICALS", "MM TRADERS", "PERUMAL KONAR SONS", "PERUMAL KONAR SONS", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "", "RAJA TRADERS", "SRI VALLI AGENCY", "SRI MUTHUMALAIMMAN HARDWARES", "SRI VALLI AGENCY", "JANAKIRAM STORES", "JANAKIRAM STORES", "JANAKIRAM STORES", "PERUMAL KONAR SONS", "", "", "SUNDER RAJ HARDWARES", "SHRI MATHI ENTERPRISES", "BISMILLAH AGENCIES", "", "BAMBIAH STORES", "MM TRADERS", "MM TRADERS", "BISMILLAH AGENCIES", "SHP AGENCY", "SRI SAKTHI ELECTRICALS", "SUNDER RAJ HARDWARES", "", "SRI SAKTHI ELECTRICALS", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "SRI MUTHUMALAIMMAN HARDWARES", "SRI VALLI AGENCY", "", "", "PANDIYAN HARDWARES", "", "ANNAM AGENCY", "", "PAPPA HARDWARES", "SRI SAKTHI ELECTRICALS", "SRI SAKTHI ELECTRICALS", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "JANAKIRAM STORES", "PAPPA HARDWARES", "", "JANAKIRAM STORES", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "SRI SAKTHI ELECTRICALS", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "SUNDER RAJ HARDWARES", "SRI MUTHUMALAIMMAN HARDWARES", "PM TRADERS", "PERUMAL KONAR SONS", "JANAKIRAM STORES", "THIRUMAL HARDWARES", "", "ANNAM AGENCY", "BISMILLAH AGENCIES", "SRI VALLI AGENCY", "PM TRADERS", "SHRI MATHI ENTERPRISES", "PM TRADERS", "PERUMAL KONAR SONS", "PM TRADERS", "SRI VALLI AGENCY", "SRI SAKTHI ELECTRICALS", "SRI MUTHUMALAIMMAN HARDWARES", "SUNDER RAJ HARDWARES", "ANNAM AGENCY", "ANNAM AGENCY", "BISMILLAH AGENCIES", "SHRI MATHI ENTERPRISES", "PM TRADERS", "SRI MUTHUMALAIMMAN HARDWARES", "SUNDER RAJ HARDWARES", "PM TRADERS", "SHRI MATHI ENTERPRISES", "PM TRADERS", "PERUMAL KONAR SONS", "SRI SAKTHI ELECTRICALS", "SHRI MATHI ENTERPRISES", "GTM TRADERS", "JAGATHA TRADERS", "PM TRADERS", "SUNDER RAJ HARDWARES", "SRI MUTHUMALAIMMAN HARDWARES", "JANAKIRAM STORES", "PM TRADERS", "THIRUMAL HARDWARES", "PERUMAL KONAR SONS", "THIRUMAL HARDWARES", "THIRUMAL HARDWARES", "PM TRADERS", "SRI MATHI ENTERPRISES", "RAJA TRADERS", "SRI SAKTHI ELECTRICALS", "PM TRADERS", "THIRUMAL HARDWARES", "SHRI MATHI ENTERPRISES", "PM TRADERS", "SRI MUTHUMALAIMMAN HARDWARES", "PM TRADERS", "SR AGENCY", "SR AGENCY", "SR AGENCY", "SR AGENCY", "PM TRADERS", "SR AGENCY", "PERUMAL KONAR SONS", "SHRI MATHI ENTERPRISES", "SR AGENCY", "SRI MATHI ENTERPRISES", "SR AGENCY", "SR AGENCY", "SR AGENCY", "SRI SAKTHI ELECTRICALS", "DHASWAN SAI ENTERPRISES", "SUNDER RAJ HARDWARES", "PERUMAL KONAR SONS", "SRI MUTHUMALAIMMAN HARDWARES", "SRI SAKTHI ELECTRICALS", "SRI MUTHUMALAIMMAN HARDWARES", "JANAKIRAM STORES", "ANNAM AGENCY", "", "SUNDER RAJ HARDWARES", "BAMBIAH STORES", "SHRIMATHI ENTERPRISES", "SRI SAKTHI ELECTRICALS", "PM TRADERS", "SRI VALLI AGENCY", "PANDIYAN HARDWARES", "SRI MUTHUMALAIMMAN HARDWARES", "SRI MATHI ENTERPRISES", "PERUMAL KONAR SONS", "PERUMAL KONAR SONS", "THIRUMAL HARDWARES", "SELVAM HARDWARES", "SR AGENCY", "SR AGENCY", "SRI SAKTHI ELECTRICALS", "SRI VALLI AGENCY", "RAJAMANI TRADERS", "", "PM TRADERS", "SHRI MATHI ENTERPRISES", "SHRI MATHI ENTERPRISES", "PERUMAL KONAR SONS", "PM TRADERS", "SHRI MATHI ENTERPRISES", "PANDIYAN HARDWARES", "PERUMAL KONAR SONS", "ASES TRADERS", "PERUMAL KONAR SONS", "SRI MUTHUMALAIMMAN HARDWARES", "PERUMAL KONAR SONS", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "RAJA TRADERS", "", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "SRI MUTHUMALAIMMAN HARDWARES", "GTM TRADERS", "SHRI MATHI ENTERPRISES", "PERUMAL KONAR SONS", "RAJAMANI TRADERS", "GTM TRADERS", "GTM TRADERS", "SHRI MATHI ENTERPRISES", "ANNAM AGENCY", "PERUMAL KONAR SONS", "GTM TRADERS", "RAJAMANI TRADERS", "SRI VALLI AGENCY", "PM TRADERS", "SRI VALLI AGENCY", "SRI VALLI AGENCY", "SUNDER RAJ HARDWARES", "RAJA TRADERS", "RAJA TRADERS", "", "", "PERUMAL KONAR SONS", "PERUMAL KONAR SONS", "SRI MATHI ENTERPRISES", "PERUMAL KONAR SONS", "PERUMAL KONAR SONS", "ANNAM AGENCY", "ASES", "ASES", "ASES", "ASES", "PERUMAL KONAR SONS", "PERUMAL KONAR SONS", "PERUMAL KONAR SONS", "ANNAM AGENCY ", "PERUMAL KONAR SONS", "SRI VALLI AGENCY", "PERUMAL KONAR SONS"],
        "Location": ["TIRUCHENDUR", "TIRUCHENDUR", "ALWARTHIRUNAGIRI", "ALWARTHIRUNAGIRI", "ALWARTHIRUNAGIRI", "PEIKULAM", "PEIKULAM", "KAYALPATNAM", "SRIVAIGUNDAM", "SEIDHUNGANALLUR", "SEIDHUNGANALLUR", "ERAL", "RAMANUJAMPUTHUR", "RAMANUJAMPUTHUR", "ALWARTHIRUNAGIRI", "AATHUR", "", "TIRUCHENDUR", "ALWARTHIRUNAGIRI", "NAZARATH", "NAZARATH", "NAZARATH", "NAZARATH", "NAZARATH", "SRIVAIGUNDAM", "NAZARATH", "", "PEIKULAM", "ARUMUGANERI", "ARUMUGANERI", "TIRUCHENDUR", "AATHUR", "ERAL", "ERAL", "KAYALPATNAM", "KAYALPATNAM", "SEIDHUNGANALLUR", "PEIKULAM", "", "SEIDHUNGANALLUR", "ALWARTHIRUNAGIRI", "ALWARTHIRUNAGIRI", "NAZARATH", "ALWARTHIRUNAGIRI", "ALWARTHIRUNAGIRI", "ALWARTHIRUNAGIRI", "SONAKANVILAI", "", "ADAIKALAPURAM", "", "KARUNGULAM", "SEIDHUNGANALLUR", "SEIDHUNGANALLUR", "ALWARTHIRUNAGIRI", "ALWARTHIRUNAGIRI", "NAZARATH", "KARUNGULAM", "", "NAZARATH", "TIRUCHENDUR", "KAYALPATNAM", "SEIDHUNGANALLUR", "", "ALWARTHIRUNAGIRI", "MEINGANAPURAM", "ALWARTHIRUNAGIRI", "ALWARTHIRUNAGIRI", "NAZARATH", "NAZARATH", "UDANGUDI", "", "UDANGUDI", "KAYALPATNAM", "ALWARTHIRUNAGIRI", "MUDHALUR", "KAYALPATNAM", "TIRUCHENDUR", "TIRUCHENDUR", "UDANGUDI", "SRIVAIGUNDAM", "SEIDHUNGANALLUR", "NAZARATH", "PEIKULAM", "UDANGUDI", "RAMANUJAMPUTHUR", "KAYALPATNAM", "KAYALPATNAM", "SATHANKULAM", "ERAL", "PEIKULAM", "SATHANKULAM", "MEINGANAPURAM", "MEINGANAPURAM", "SRIVAIGUNDAM", "TIRUCHENDUR", "ARUMUGANERI", "MUDHALUR", "PERIYATHAZHAI", "KAYALPUR", "PEIKULAM", "ERAL", "NAZARATH", "TIRUCHENDUR", "SRIVAIGUNDAM", "KULASEGARAPATNAM", "KULASEGARAPATNAM", "PARAMAKURICHI", "MUDHALUR", "TIRUCHENDUR", "TIRUCHENDUR", "PEIKULAM", "TIRUCHENDUR", "UDANGUDI", "KULASEGARAPATNAM", "MUDHALUR", "ERAL", "ERAL", "KURUMBUR", "KURUMBUR", "KURUMBUR", "KURUMBUR", "SATHANKULAM", "KURUMBUR", "KARUNGULAM", "PARAMAKURICHI", "SATHANKULAM", "ADAIKALAPURAM", "KURUMBUR", "SATHANKULAM", "SATHANKULAM", "SEIDHUNGANALLUR", "KARUNGULAM", "PEIKULAM", "SEIDHUNGANALLUR", "ERAL", "SEIDHUNGANALLUR", "ERAL", "NAZARATH", "NAZARATH", "ALWARTHIRUNAGIRI", "PEIKULAM", "AATHUR", "ARUMUGANERI", "SEIDHUNGANALLUR", "SATHANKULAM", "SONAKANVILAI", "SONAKANVILAI", "NAZARATH", "SRIVAIGUNDAM", "TIRUCHENDUR", "UDANGUDI", "MEINGANAPURAM", "KURUMBUR", "KURUMBUR", "SRIVAIGUNDAM", "ALWARTHIRUNAGIRI", "PEIKULAM", "", "MUDHALUR", "TIRUCHENDUR", "TIRUCHENDUR", "SRIVAIGUNDAM", "MUDHALUR", "KAYALPATNAM", "ARUMUGANERI", "RAMANUJAMPUTHUR", "SRIVAIGUNDAM", "PEIKULAM", "ERAL", "SRIVAIGUNDAM", "TIRUCHENDUR", "ALWARTHIRUNAGIRI", "TIRUCHENDUR", "", "ALWARTHIRUNAGIRI", "UDANGUDI", "NAZARATH", "SATHANKULAM", "SEIDHUNGANALLUR", "RAMANUJAMPUTHUR", "PEIKULAM", "MUDHALUR", "SATHANKULAM", "SATHANKULAM", "UDANGUDI", "SRIVAIGUNDAM", "SATHANKULAM", "ALWARTHIRUNAGIRI", "ALWARTHIRUNAGIRI", "KAYALPATNAM", "KAYALPATNAM", "TIRUCHENDUR", "TIRUCHENDUR", "TIRUCHENDUR", "TIRUCHENDUR", "ALWARTHIRUNAGIRI", "", "SEIDHUNGANALLUR", "THURSDAY", "SRIVAIGUNDAM", "SRIVAIGUNDAM", "TIRUCHENDUR", "UDANGUDI", "SRIVAIGUNDAM", "SRIVAIGUNDAM", "SRIVAIGUNDAM", "SRIVAIGUNDAM", "SRIVAIGUNDAM", "KARUNGULAM", "SRIVAIGUNDAM", "MEINGANAPURAM", "KURUMBUR", "TIRUCHENDUR", "TIRUCHENDUR"],
        "DAY": ["MONDAY", "MONDAY", "SATURDAY", "SATURDAY", "SATURDAY", "FRIDAY", "FRIDAY", "TUESDAY", "THURSDAY", "THURSDAY", "THURSDAY", "TUESDAY", "FRIDAY", "FRIDAY", "SATURDAY", "TUESDAY", "", "MONDAY", "SATURDAY", "SATURDAY", "SATURDAY", "SATURDAY", "SATURDAY", "SATURDAY", "THURSDAY", "SATURDAY", "", "FRIDAY", "MONDAY", "TUESDAY", "MONDAY", "TUESDAY", "TUESDAY", "TUESDAY", "TUESDAY", "TUESDAY", "THURSDAY", "FRIDAY", "", "THURSDAY", "SATURDAY", "SATURDAY", "SATURDAY", "SATURDAY", "SATURDAY", "SATURDAY", "WEDNESDAY", "", "MONDAY", "", "THURSDAY", "THURSDAY", "THURSDAY", "SATURDAY", "SATURDAY", "SATURDAY", "THURSDAY", "FRIDAY", "SATURDAY", "MONDAY", "TUESDAY", "THURSDAY", "", "SATURDAY", "WEDNESDAY", "SATURDAY", "SATURDAY", "SATURDAY", "SATURDAY", "WEDNESDAY", "", "WEDNESDAY", "TUESDAY", "SATURDAY", "MONDAY", "MONDAY", "MONDAY", "WEDNESDAY", "THURSDAY", "THURSDAY", "SATURDAY", "FRIDAY", "WEDNESDAY", "FRIDAY", "TUESDAY", "FRIDAY", "FRIDAY", "WEDNESDAY", "WEDNESDAY", "THURSDAY", "MONDAY", "MONDAY", "WEDNESDAY", "WEDNESDAY", "MONDAY", "FRIDAY", "TUESDAY", "SATURDAY", "MONDAY", "THURSDAY", "WEDNESDAY", "WEDNESDAY", "WEDNESDAY", "WEDNESDAY", "MONDAY", "MONDAY", "FRIDAY", "MONDAY", "WEDNESDAY", "WEDNESDAY", "WEDNESDAY", "TUESDAY", "TUESDAY", "TUESDAY", "TUESDAY", "WEDNESDAY", "TUESDAY", "THURSDAY", "WEDNESDAY", "MONDAY", "MONDAY", "THURSDAY", "SATURDAY", "SATURDAY", "THURSDAY", "THURSDAY", "FRIDAY", "THURSDAY", "TUESDAY", "THURSDAY", "SATURDAY", "SATURDAY", "SATURDAY", "FRIDAY", "TUESDAY", "MONDAY", "THURSDAY", "FRIDAY", "SATURDAY", "MONDAY", "WEDNESDAY", "THURSDAY", "THURSDAY", "WEDNESDAY", "TUESDAY", "TUESDAY", "THURSDAY", "SATURDAY", "FRIDAY", "", "WEDNESDAY", "MONDAY", "MONDAY", "THURSDAY", "WEDNESDAY", "FRIDAY", "MONDAY", "FRIDAY", "THURSDAY", "FRIDAY", "TUESDAY", "THURSDAY", "MONDAY", "SATURDAY", "MONDAY", "", "SATURDAY", "WEDNESDAY", "SATURDAY", "FRIDAY", "THURSDAY", "FRIDAY", "WEDNESDAY", "FRIDAY", "FRIDAY", "WEDNESDAY", "FRIDAY", "FRIDAY", "SATURDAY", "SATURDAY", "TUESDAY", "TUESDAY", "SATURDAY", "MONDAY", "MONDAY", "MONDAY", "", "", "THURSDAY", "MONDAY", "THURSDAY", "MONDAY", "MONDAY", "WEDNESDAY", "THURSDAY", "THURSDAY", "THURSDAY", "THURSDAY", "THURSDAY", "THURSDAY", "THURSDAY", "WEDNESDAY", "TUESDAY", "MONDAY", "MONDAY"],
        "Category": ["E", "E", "E", "E", "E", "E", "M", "M", "E", "E", "E", "E", "E", "E", "E", "E", "", "E", "E", "E", "E", "M", "M", "M", "M", "M", "", "E", "E", "M", "E", "E", "M", "M", "M", "E", "E", "E", "", "E", "E", "E", "E", "E", "M", "E", "", "", "E", "", "E", "E", "E", "M", "M", "M", "M", "", "E", "E", "M", "M", "", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "M", "M", "E", "E", "M", "E", "M", "E", "E", "E", "E", "M", "E", "E", "E", "E", "E", "E", "M", "E", "E", "M", "E", "M", "M", "M", "M", "E", "M", "E", "E", "M", "E", "M", "E", "M", "M", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "M", "M", "M", "E", "E", "M", "M", "E", "E", "E", "E", "E", "E", "E", "E", "E", "", "E", "E", "E", "E", "M", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "M", "E", "M", "E", "M", "M", "E", "E", "E", "E", "E", "E", "M", "M", "E", "M", "M", "M", "E", "E", "E", "M", "E", "M", "M", "M", "M", "M", "M", "M", "M", "M", "M", "E", "E", "E"],
        "HW305": ["YES", "YES", "YES", "", "", "YES", "", "", "YES", "", "YES", "YES", "YES", "YES", "YES", "", "", "YES", "", "", "", "", "", "", "", "", "", "YES", "YES", "", "", "YES", "", "", "YES", "", "YES", "YES", "", "YES", "YES", "YES", "YES", "", "", "", "", "", "YES", "YES", "", "", "", "", "", "", "", "", "", "", "", "YES", "", "YES", "YES", "YES", "YES", "YES", "YES", "", "", "YES", "YES", "YES", "YES", "YES", "YES", "", "YES", "YES", "YES", "", "YES", "", "YES", "", "", "", "YES", "", "YES", "", "YES", "YES", "", "YES", "YES", "YES", "YES", "", "", "", "", "YES", "", "YES", "", "", "YES", "", "", "", "", "", "", "", "YES", "YES", "YES", "YES", "YES", "YES", "YES", "YES", "", "YES", "YES", "", "YES", "", "YES", "", "", "", "YES", "", "YES", "YES", "YES", "YES", "YES", "", "YES", "", "", "", "", "", "YES", "YES", "", "YES", "", "YES", "YES", "YES", "YES", "", "YES", "", "YES", "YES", "", "", "", "", "YES", "", "", "YES", "", "", "", "", "", "", "YES", "YES", "", "YES", "YES", "YES", "", "", "YES", "", "", "", "", "YES", "", "", "", "", "", "", "YES", "YES", "YES", "YES", "YES", "YES", "", "", "", "", "", "YES", "", "", "", "", "", "", "", "", "YES", "YES", "YES", "YES"],
        "HW101": ["YES", "YES", "YES", "", "", "YES", "", "", "YES", "", "YES", "YES", "YES", "YES", "YES", "", "", "", "", "YES", "", "", "", "", "", "", "", "YES", "", "", "", "", "", "", "YES", "YES", "YES", "YES", "", "YES", "YES", "YES", "YES", "", "", "", "", "", "", "YES", "", "", "", "", "", "", "", "", "", "", "", "YES", "", "YES", "YES", "YES", "YES", "", "", "", "", "YES", "YES", "YES", "YES", "YES", "YES", "", "YES", "YES", "YES", "", "YES", "", "YES", "", "", "", "YES", "", "YES", "", "YES", "YES", "", "YES", "YES", "YES", "YES", "", "", "", "", "YES", "", "YES", "", "", "YES", "", "", "", "", "", "", "", "YES", "YES", "YES", "YES", "YES", "YES", "YES", "YES", "", "YES", "YES", "", "YES", "", "YES", "", "", "", "YES", "", "YES", "YES", "YES", "YES", "YES", "", "YES", "", "", "", "", "", "YES", "YES", "", "YES", "", "YES", "YES", "YES", "YES", "", "YES", "", "YES", "YES", "", "", "", "", "YES", "", "", "YES", "", "", "", "", "", "", "YES", "YES", "", "YES", "YES", "YES", "", "", "YES", "", "", "", "", "YES", "", "", "", "", "", "", "YES", "YES", "YES", "YES", "YES", "YES", "", "", "", "", "", "YES", "", "", "", "", "", "", "", "", "YES", "YES", "YES", "YES"],
        "Hw201": ["YES", "YES", "YES", "", "", "YES", "", "", "", "YES", "", "YES", "YES", "YES", "", "", "", "", "", "", "", "", "", "", "", "", "", "YES", "", "", "", "", "", "", "", "", "YES", "YES", "", "YES", "YES", "YES", "YES", "", "", "", "", "", "", "YES", "", "", "", "", "", "", "", "", "", "", "", "YES", "", "YES", "YES", "YES", "YES", "", "", "", "", "YES", "YES", "YES", "YES", "YES", "YES", "", "YES", "YES", "YES", "", "YES", "", "YES", "", "", "", "YES", "", "YES", "", "YES", "YES", "", "YES", "YES", "YES", "YES", "", "", "", "", "YES", "", "YES", "", "", "YES", "", "", "", "", "", "", "", "YES", "YES", "YES", "YES", "YES", "YES", "YES", "YES", "", "YES", "YES", "", "YES", "", "YES", "", "", "", "YES", "", "YES", "YES", "YES", "YES", "YES", "", "YES", "", "", "", "", "", "YES", "YES", "", "YES", "", "YES", "YES", "YES", "YES", "", "YES", "", "YES", "YES", "", "", "", "", "YES", "", "", "YES", "", "", "", "", "", "", "YES", "YES", "", "YES", "YES", "YES", "", "", "YES", "", "", "", "", "YES", "", "", "", "", "", "", "YES", "YES", "YES", "YES", "YES", "YES", "", "", "", "", "", "YES", "", "", "", "", "", "", "", "", "", "YES", "YES", ""],
        "HW103": ["YES", "YES", "", "", "", "", "", "", "", "", "", "YES", "YES", "YES", "", "", "", "YES", "", "", "", "", "", "", "", "", "", "", "", "", "", "YES", "", "", "", "YES", "", "", "", "", "", "", "", "", "", "", "", "", "YES", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "YES", "", "", "", "", "YES", "", "", "", "", "YES", "", "", "", "", "", "", "", "", "YES", "", "", "YES", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "YES", "YES", "", "", "", "", "", "", "", "", "YES", "YES", "", "", "", "", "", "YES", "", "", "YES", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "YES", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "YES", "", ""],
        "HW302": ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "SBR", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "YES", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
        "HW310": ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
        "other": ["", "", "", "", "", "", "", "", "", "", "", "", "YES", "YES", "", "", "", "", "", "SBR", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "Yes", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "YES", "YES", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "SBR", "", ""]
    }
    return pd.DataFrame(data)

# --- Session State Initialization ---
if 'data' not in st.session_state:
    st.session_state['data'] = get_initial_dataset()

if 'prev_data' not in st.session_state:
    st.session_state['prev_data'] = None

# --- TOP SECTION: Data Operations (Collapsible) ---
with st.expander("🛠️ Data Management (Import / Add / Undo)", expanded=False):
    
    # Global Undo Button
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
    
    # 4 Columns for Filters
    fc1, fc2, fc3, fc4 = st.columns(4)
    
    with fc1:
        # Sort locations, handle blanks
        locs = [str(x) for x in df_display["Location"].unique() if x]
        locations = ["All"] + sorted(locs)
        selected_location = st.selectbox("📍 Location", locations)
        
    with fc2:
        days_list = [str(x) for x in df_display["DAY"].unique() if x]
        days = ["All"] + sorted(days_list)
        selected_day = st.selectbox("📅 Day", days)
        
    with fc3:
        # Handle Category Blanks specifically
        # Get unique values, filtering out nan/empty strings
        cats_raw = [str(x) for x in df_display["Category"].unique() if pd.notna(x) and str(x).strip() != '']
        cats = ["All"] + sorted(cats_raw) + ["Blank / Uncategorized"]
        selected_cat = st.selectbox("🏷️ Category", cats)
        
    with fc4:
        st.write("**Product Visibility**")
        show_only_products = st.checkbox("Has Products")
        show_no_products = st.checkbox("No Products")

# --- Apply Filters Logic ---
if not df_display.empty:
    # 1. Location
    if selected_location != "All": 
        df_display = df_display[df_display["Location"] == selected_location]
    
    # 2. Day
    if selected_day != "All": 
        df_display = df_display[df_display["DAY"] == selected_day]
    
    # 3. Category (Handle Blanks)
    if selected_cat == "Blank / Uncategorized":
        # Filter where Category is NaN or Empty String
        df_display = df_display[df_display["Category"].isna() | (df_display["Category"] == "")]
    elif selected_cat != "All": 
        df_display = df_display[df_display["Category"] == selected_cat]
        
    # 4. Products
    hw_cols = ["HW305", "HW101", "Hw201", "HW103", "HW302", "HW310"]
    # Check for 'YES' in any of these columns (case insensitive)
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
# Mason Cards is first (Default)
tab_cards, tab_graphs, tab_data = st.tabs(["📇 Mason Cards", "📈 Analytics", "📝 Data Editor"])

with tab_cards:
    if not df_display.empty:
        # Start the Grid Container using Tailwind classes
        html_content = '<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">'
        
        for index, row in df_display.iterrows():
            # Data Extraction with fallbacks
            name = row.get("MASON NAME", "Unknown")
            code = row.get("MASON CODE", "N/A")
            cat = row.get("Category", "N/A")
            if not cat: cat = "N/A" # Handle empty strings
            
            contact = str(row.get("CONTACT NUMBER", "")).replace(".0", "").strip()
            loc = row.get("Location", "")
            dlr = row.get("DLR NAME", "")
            day = row.get("DAY", "")
            
            # Products Badge Logic
            products_html = ""
            hw_cols = ["HW305", "HW101", "Hw201", "HW103", "HW302", "HW310"]
            has_prod = False
            for p in hw_cols:
                # Check column existence + check for YES
                if p in row and isinstance(row[p], str) and 'YES' in row[p].upper():
                    # Clean up badge text (e.g. Hw201 -> HW201)
                    p_clean = p.upper()
                    products_html += f'<span class="inline-block bg-indigo-100 text-indigo-800 text-xs font-medium px-2.5 py-0.5 rounded-full border border-indigo-200 mr-1 mb-1">{p_clean}</span>'
                    has_prod = True
            
            if not has_prod:
                products_html = '<span class="text-xs text-slate-400 italic">No products listed</span>'

            # Call Button Logic
            if contact and contact.lower() != "nan" and contact != "":
                call_btn = f"""
                <a href="tel:{contact}" target="_blank" class="inline-flex items-center justify-center w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md transition-colors mt-3 no-underline">
                    <span class="mr-2">📞</span> Call {contact}
                </a>
                """
            else:
                call_btn = """
                <button disabled class="inline-flex items-center justify-center w-full px-4 py-2 bg-slate-300 text-slate-500 text-sm font-medium rounded-md mt-3 cursor-not-allowed">
                    No Contact
                </button>
                """

            # HTML Card Structure
            card = f"""
            <div class="bg-white rounded-lg shadow p-5 flex flex-col transition-all duration-300 hover:shadow-lg border-t-4 border-indigo-500">
                <div class="mb-3">
                    <h3 class="text-xl font-bold text-slate-800">{name}</h3>
                    <div class="flex justify-between items-center mt-1">
                        <p class="text-sm text-slate-500 font-medium">{code}</p>
                        <span class="bg-slate-100 text-slate-600 text-xs px-2 py-1 rounded border border-slate-200">{cat}</span>
                    </div>
                </div>
                <div class="space-y-2 text-sm text-slate-700 mb-4 flex-grow">
                    <p class="flex items-start"><span class="w-24 font-semibold text-slate-500 shrink-0">Location:</span> {loc}</p>
                    <p class="flex items-start"><span class="w-24 font-semibold text-slate-500 shrink-0">DLR:</span> {dlr}</p>
                    <p class="flex items-start"><span class="w-24 font-semibold text-slate-500 shrink-0">Day:</span> <span class="font-semibold text-indigo-700">{day}</span></p>
                </div>
                <div class="mt-auto pt-3 border-t border-slate-200">
                    <h4 class="text-xs font-semibold text-slate-600 mb-2">Products:</h4>
                    <div class="flex flex-wrap gap-1 mb-3">
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
            # Filter available columns
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
