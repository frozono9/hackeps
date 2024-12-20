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
        st.markdown(
            """
            <div style="
                background-color: rgba(255, 255, 0, 0.1); 
                border-radius: 10px; 
                padding: 10px; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                width: 100%;
                margin: 10px 0;
            ">
                ⚠️ <span style="margin-left: 10px;">Aquest tràmit no esta disponible ara mateix</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
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

# Initialize the session state for storing previously searched Tramits and results
if 'searched_tramits' not in st.session_state:
    st.session_state.searched_tramits = []
if 'result' not in st.session_state:
    st.session_state.result = []

# Layout
st.set_page_config(layout="wide")

col1, col2 = st.columns([1, 3])

with col1:
    st.header("Historial de Cerca")
    for tramit in reversed(st.session_state.searched_tramits):
        st.write(tramit)

with col2:
    st.header("Selecciona un Tràmit")
    options = ['Selecciona un Tràmit'] + tramits_df['Titol'].tolist()
    st.selectbox('Selecciona un Tràmit', options, key='tramit_input_title', on_change=on_select_change)
    
    st.caption("Suggerencies")
    if st.session_state.result:
        for r in st.session_state.result:
            st.button(r, on_click=on_button_click, args=(r,))

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
