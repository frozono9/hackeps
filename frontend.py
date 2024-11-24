from backend import call_function
import streamlit as st
import pandas as pd

# Load the CSV file
tramits_df = pd.read_csv('tramits.csv')

# Create a dictionary to map Titol to Sequence
titol_to_sequence = dict(zip(tramits_df['Titol'], tramits_df['Sequence']))

# Function to handle the selection change
def on_select_change():
    tramit_input_title = st.session_state.tramit_input_title
    if tramit_input_title == "Selecciona un Tràmit":
        return
    tramit_row = tramits_df[tramits_df['Titol'] == tramit_input_title]
    if not tramit_row['Vigent'].values[0]:
        st.session_state.warning = True
    else:
        st.session_state.warning = False
        # Add the selected tramit to the list of previously searched Tramits
        if tramit_input_title not in st.session_state.searched_tramits:
            st.session_state.searched_tramits.append(tramit_input_title)
            # Keep only the last 5 elements
            if len(st.session_state.searched_tramits) > 5:
                st.session_state.searched_tramits.pop(0)
        
        # Prepare the input for the model
        tramit_input = [titol_to_sequence[title] for title in st.session_state.searched_tramits]
        result = call_function(tramit_input)
        
        # Check if any prediction is the same as the input
        result = ["Repetir tràmit: " + tramit_input_title if r == tramit_input_title else r for r in result]
        st.session_state.result = result

# Function to handle button click
def on_button_click(tramit_title):
    if tramit_title.startswith("Repetir tràmit: "):
        tramit_title = tramit_title.replace("Repetir tràmit: ", "")
    st.session_state.tramit_input_title = tramit_title
    st.session_state.searched_tramits.append(tramit_title)
    # Keep only the last 5 elements
    if len(st.session_state.searched_tramits) > 5:
        st.session_state.searched_tramits.pop(0)
    on_select_change()

# Initialize session state
if 'searched_tramits' not in st.session_state:
    st.session_state.searched_tramits = []
if 'result' not in st.session_state:
    st.session_state.result = []
if 'warning' not in st.session_state:
    st.session_state.warning = False

# Layout
st.set_page_config(layout="wide")

# Custom CSS for full background containers
st.markdown(
    """
    <style>
    body {
        background-color: #1e1e1e;
        color: white;
    }
    .section-container {
        background-color: #2c2c2c;
        padding: 20px;
        border-radius: 15px;
        margin: 10px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
    }
    .section-title {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .content-item {
        font-size: 16px;
        margin-bottom: 10px;
    }
    .warning-box {
        background-color: rgba(255, 255, 0, 0.1);
        color: #ffd700;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 15px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h1 style='text-align: center;'>Seleccionador de Tràmits</h1>", unsafe_allow_html=True)

# Columns
col1, col2 = st.columns([1, 3])

with col1:
    # Historial de Cerca container
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Historial de Cerca</div>', unsafe_allow_html=True)
    if st.session_state.searched_tramits:
        for tramit in reversed(st.session_state.searched_tramits):
            st.markdown(f'<div class="content-item">{tramit}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="content-item">Cap tràmit cercat.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Selecciona un Tràmit container
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Selecciona un Tràmit</div>', unsafe_allow_html=True)
    
    # Warning message for invalid tramit
    if st.session_state.warning:
        st.markdown('<div class="warning-box">⚠️ Aquest tràmit no està disponible ara mateix</div>', unsafe_allow_html=True)
    
    # Dropdown
    options = ['Selecciona un Tràmit'] + tramits_df['Titol'].tolist()
    st.selectbox('Selecciona un Tràmit', options, key='tramit_input_title', on_change=on_select_change)
    
    # Suggested results
    st.caption("Suggerencies")
    if st.session_state.result:
        for r in st.session_state.result:
            st.button(r, on_click=on_button_click, args=(r,))
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown(
    """
    <hr style="margin-top: 50px; margin-bottom: 20px;">
    <div style="text-align: center; font-size: 14px; color: grey;">
        <p>
            <strong>Projecte Seleccionador de Tràmits</strong><br>
            Desenvolupat per l'equip <span style="color: grey;">Porks in Paris</span> per la LleidaHack 2024.<br>
            Aquest projecte facilita la cerca i gestió dels tràmits administratius de forma eficient i interactiva.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
