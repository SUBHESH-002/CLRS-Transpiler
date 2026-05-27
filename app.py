import streamlit as st
import transpiler
from traceback import format_exc

# Set page config
st.set_page_config(page_title="CLRS Transpiler", layout="wide")

# Inject Custom Cyberpunk CSS
st.markdown("""
    <style>
    /* Background and global elements */
    .stApp {
        background-color: #000000 !important;
    }
    
    /* Font configurations and overrides */
    h1, h2, h3, h4, h5, h6, p, span, label, div[data-testid="stMarkdownContainer"] {
        color: #00FF41 !important;
        font-family: 'Courier New', Courier, monospace !important;
    }

    /* Container overrides to block default white background themes */
    [data-testid="stVerticalBlock"] {
        background-color: #000000 !important;
    }

    /* Streamlit Button Overrides */
    div.stButton > button {
        background-color: #000000 !important;
        color: #00FF41 !important;
        border: 1px solid #00FF41 !important;
        box-shadow: 0 0 10px #00FF41 !important;
        font-family: 'Fira Code', monospace !important;
        font-weight: bold !important;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        background-color: #00FF41 !important;
        color: #000000 !important;
        box-shadow: 0 0 20px #00FF41 !important;
    }
    div.stButton > button:active {
        box-shadow: 0 0 5px #00FF41 !important;
    }
    
    hr {
        border-color: #00FF41 !important;
        box-shadow: 0 0 5px #00FF41 !important;
    }
    
    /* Native TextArea Overrides */
    .stTextArea textarea {
        background-color: #000000 !important;
        color: #00FF41 !important;
        border: 1px solid #00FF41 !important;
        box-shadow: 0 0 10px #00FF41 !important;
        font-family: 'Fira Code', 'Courier New', monospace !important;
        border-radius: 0 !important;
    }
    .stTextArea textarea:focus {
        box-shadow: 0 0 20px #00FF41 !important;
        border: 1px solid #00FF41 !important;
    }
    .stTextArea textarea:disabled {
        background-color: #051505 !important;
        color: #00FF41 !important;
    }
    </style>
""", unsafe_allow_html=True)


st.title("📟 CLRS Pseudocode Transpiler")
st.markdown("---")

initial_code = """for j = 2 to n
    key = A[j]
    i = j - 1
    while i > 0 and A[i] > key
        A[i + 1] = A[i]
        i = i - 1
    A[i + 1] = key"""

if 'input_code' not in st.session_state:
    st.session_state.input_code = initial_code

if 'output_code' not in st.session_state:
    st.session_state.output_code = ""

def run_translation(code):
    if not code.strip():
        return ""
    try:
        return transpiler.translate(code)
    except Exception as e:
        return f"[ SYSTEM ERROR ]\n{str(e)}\n\nTraceback:\n{format_exc()}"

# Layout Strategy
col1, col2 = st.columns(2)

with col1:
    st.markdown("### CLRS Pseudocode (Input)")
    # Using robust native text area ensures connection stability
    clrs_code = st.text_area(
        "Pseudo Input",
        value=st.session_state.input_code,
        height=400,
        label_visibility="collapsed"
    )
    
    # Run trigger Button
    if st.button("[ RUN_TRANSPILER ]", use_container_width=True):
        st.session_state.output_code = run_translation(clrs_code)

with col2:
    st.markdown("### Executable Python (Output)")
    
    # Read-only Native TextArea for Output
    st.text_area(
        "Python Output",
        value=st.session_state.output_code,
        height=400,
        disabled=True,
        label_visibility="collapsed"
    )
    
    # Custom HTML/JS Copy Button
    escaped_code = st.session_state.output_code.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
    copy_html = f"""
    <div onclick="navigator.clipboard.writeText(`{escaped_code}`); this.innerText='[ COPIED! ]'" 
         style="background-color: #000000; color: #00FF41; border: 1px solid #00FF41; padding: 0.5rem; text-align: center; cursor: pointer; box-shadow: 0 0 10px #00FF41; box-sizing: border-box; font-family: 'Fira Code', 'Courier New', monospace; font-weight: bold; width: 100%; transition: all 0.2s ease-in-out; border-radius: 0.5rem;"
         onmouseover="this.style.backgroundColor='#00FF41'; this.style.color='#000000'; this.style.boxShadow='0 0 20px #00FF41';"
         onmouseout="this.style.backgroundColor='#000000'; this.style.color='#00FF41'; this.style.boxShadow='0 0 10px #00FF41'; this.innerText='[ COPY_CODE ]'">
    [ COPY_CODE ]
    </div>
    """
    st.markdown(copy_html, unsafe_allow_html=True)
