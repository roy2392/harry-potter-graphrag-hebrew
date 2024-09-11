import streamlit as st
import requests
import json
from PIL import Image

# Set page config
st.set_page_config(page_title="Hogwarts Knowledge Seeker", page_icon="🧙‍♂️", layout="wide")

# Custom CSS for Harry Potter theme
st.markdown("""
<style>
    body {
        background-color: #2a2d34;
        color: #ffd700;
        font-family: 'Luminari', fantasy;
    }
    .stButton>button {
        background-color: #7f0909;
        color: #ffd700;
    }
    .stTextInput>div>div>input {
        background-color: #4a4a4a;
        color: #ffd700;
    }
    .stRadio>label {
        color: #ffd700;
    }
</style>
""", unsafe_allow_html=True)

# Load and display Hogwarts logo
logo = Image.open("hogwarts_logo.png")  # Make sure to have this image in your project directory
st.image(logo, width=200)

st.title("Hogwarts Knowledge Seeker")

# Search type selection
search_type = st.radio("Select Search Type:", ("Global", "Local"))

# User input
user_query = st.text_input("Ask your question about the wizarding world:", "")

if st.button("Seek Knowledge"):
    if user_query:
        # Determine which API endpoint to use based on search type
        if search_type == "Global":
            url = "http://localhost:8000/search/global"
        else:
            url = "http://localhost:8000/search/local"
        
        # Make API request
        try:
            response = requests.get(url, params={"query": user_query})
            response.raise_for_status()
            result = response.json()
            
            # Extract and display the answer
            answer = json.loads(result['response'])['choices'][0]['message']['content']
            st.markdown("### 📜 The Ancient Texts Reveal:")
            st.write(answer)
            
            # Display additional information
            with st.expander("View Magical Details"):
                st.write(f"🕰️ Divination Time: {result['completion_time']:.2f} seconds")
                st.write(f"🔮 Crystal Ball Gazes: {result['llm_calls']}")
                st.write(f"📚 Scrolls Consulted: {result['prompt_tokens']}")
        
        except requests.RequestException as e:
            st.error(f"Alas! The owls couldn't deliver your message. Error: {e}")
    else:
        st.warning("Please enter a question, young wizard!")

# Footer
st.markdown("---")
st.markdown("*\"Help will always be given at Hogwarts to those who ask for it.\"* - Albus Dumbledore")