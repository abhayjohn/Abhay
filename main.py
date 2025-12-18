import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image
import pytesseract

# -----------------------
# Google Sheets Setup
# -----------------------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

GSHEET_NAME = "School_Master_Serial_Number_Capture"

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"],
    SCOPE
)

client = gspread.authorize(creds)
sheet_master = client.open(GSHEET_NAME).worksheet("school_master")
sheet_serials = client.open(GSHEET_NAME).worksheet("smartboard_serials")

# -----------------------
# UI
# -----------------------
st.title("Smartboard Serial Number Collection")

for key in [
    "udise", "school", "devices", "selected_device",
    "serial_number", "user_email"
]:
    st.session_state.setdefault(key, "")

# Search School
udise = st.text_input("Enter UDISE", st.session_state.udise)

if st.button("Search"):
    st.session_state.udise = udise.strip()
    rows = sheet_master.get_all_records()

    devices = []
    school = ""

    for r in rows:
        if str(r["UDISE"]) == st.session_state.udise and r["Status"] != "Inactive":
            devices.append(r["Device Name"])
            school = r["School"]

    st.session_state.devices = devices
    st.session_state.school = school
    st.session_state.selected_device = ""
    st.session_state.serial_number = ""

# Show School
if st.session_state.school:
    st.success(f"School: {st.session_state.school}")

    device = st.selectbox(
        "Select Device",
        st.session_state.devices
    )

    image = st.file_uploader("Upload Serial Image (optional)", ["jpg", "png"])

    if image:
        img = Image.open(image)
        st.image(img, width=250)
        st.session_state.serial_number = pytesseract.image_to_string(img).strip()

    st.session_state.serial_number = st.text_input(
        "Serial Number",
        st.session_state.serial_number
    )

    st.session_state.user_email = st.text_input(
        "Your Email",
        st.session_state.user_email
    )

    if st.button("Submit"):
        if not st.session_state.serial_number or not st.session_state.user_email:
            st.error("Serial number and email are required")
        else:
            sheet_serials.append_row([
                st.session_state.udise,
                st.session_state.school,
                device,
                st.session_state.serial_number,
                st.session_state.user_email
            ])
            st.success("Serial saved successfully")
            st.session_state.serial_number = ""
