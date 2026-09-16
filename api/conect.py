import os
import bcchapi
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

api_token = st.secrets.get("API_TOKEN", os.getenv("API_TOKEN"))
siete = bcchapi.Siete(token=api_token)


