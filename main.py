import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="Google Sheet App", layout="wide")

st.title("Google Sheet Connection Test")

# --- Auth ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(credentials)

# --- Open Sheet ---
SHEET_NAME = "School_Master_Serial_Number_Capture"
worksheet = client.open(SHEET_NAME).sheet1

data = worksheet.get_all_records()
df = pd.DataFrame(data)

st.success("Connected to Google Sheet successfully ✅")
st.dataframe(df)
