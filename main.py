import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image
import pytesseract

# -----------------------
# OPTIONAL: Tesseract path (Streamlit Cloud uses this)
# -----------------------
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# -----------------------
# Google Sheets Setup
# -----------------------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

GSHEET_NAME = "School_Master_Serial_Number_Capture"

# Load credentials from Streamlit Secrets
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"],
    SCOPE
)

client = gspread.authorize(creds)
sheet_master = client.open(GSHEET_NAME).worksheet("school_master")
sheet_serials = client.open(GSHEET_NAME).worksheet("smartboard_serials")

# -----------------------
# Streamlit UI
# -----------------------
st.title("Smartboard Serial Number Collection")

# Initialize session state
for key in [
    "udise",
    "school",
    "devices",
    "selected_device",
    "serial_number",
    "user_email"
]:
    if key not in st.session_state:
        st.session_state[key] = ""

# -----------------------
# Step 1: Search School
# -----------------------
udise_input = st.text_input("Enter UDISE", st.session_state.udise)

if st.button("Search School"):
    st.session_state.udise = udise_input.strip()

    master_data = sheet_master.get_all_records()
    devices = []
    school_name = ""

    for row in master_data:
        if str(row["UDISE"]) == st.session_state.udise and row["Status"] != "Inactive":
            devices.append(row["Device Name"])
            school_name = row["School"]

    st.session_state.devices = devices
    st.session_state.school = school_name
    st.session_state.selected_device = ""
    st.session_state.serial_number = ""

# -----------------------
# Step 2: Show School & Devices
# -----------------------
if st.session_state.school:
    st.success(f"School: {st.session_state.school}")

    if st.session_state.devices:
        st.session_state.selected_device = st.selectbox(
            "Select Device",
            st.session_state.devices
        )

        # -----------------------
        # Upload Image (Optional)
        # -----------------------
        uploaded_file = st.file_uploader(
            "Upload Serial Number Image (optional)",
            type=["jpg", "jpeg", "png"]
        )

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, width=250)

            extracted_text = pytesseract.image_to_string(image)
            st.session_state.serial_number = extracted_text.strip()

        # -----------------------
        # Manual Serial Entry
        # -----------------------
        st.session_state.serial_number = st.text_input(
            "Serial Number",
            st.session_state.serial_number
        )

        # -----------------------
        # Email Capture
        # -----------------------
        st.session_state.user_email = st.text_input(
            "Updated By (Email)",
            st.session_state.user_email
        )

        # -----------------------
        # Submit
        # -----------------------
        if st.button("Submit"):
            if not st.session_state.serial_number:
                st.warning("Please enter or upload serial number")
            elif not st.session_state.user_email:
                st.warning("Please enter email")
            else:
                existing = sheet_serials.get_all_records()
                duplicate = any(
                    str(r["UDISE"]) == st.session_state.udise and
                    r["Device Name"] == st.session_state.selected_device
                    for r in existing
                )

                if duplicate:
                    st.error("Serial already submitted for this device")
                else:
                    sheet_serials.append_row([
                        st.session_state.udise,
                        st.session_state.school,
                        st.session_state.selected_device,
                        st.session_state.serial_number,
                        st.session_state.user_email
                    ])

                    st.success("Serial number saved successfully ✅")

                    # Reset after save
                    st.session_state.selected_device = ""
                    st.session_state.serial_number = ""
