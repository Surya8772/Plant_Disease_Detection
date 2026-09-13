import os
import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import pandas as pd
from datetime import datetime, date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.parse

# --- CONFIGURE YOUR EMAIL HERE ---
SENDER_EMAIL = "suryaprakashrana302@gmail.com"  # << CHANGE THIS
SENDER_APP_PASSWORD = "qdfo hezx jang fkmb"  # << CHANGE THIS (see note below)

# --- DOCTOR DATA ---
DOCTORS = [
    {"name": "Dr. R. K. Sharma", "degree": "Ph.D. Plant Pathology", "specialization": "Potato & Tomato Diseases", "experience": "15 Years", "hospital": "ICAR - IIHR, Hessarghatta", "location": "Bangalore", "contact": "+91 7061060726", "whatsapp": "917061060726", "email": "suryaprakashrana302@gmail.com", "fee": "₹500"},
    {"name": "Dr. Priya Nair", "degree": "Ph.D Agri Entomology", "specialization": "Crop Disease Management", "experience": "12 Years", "hospital": "UAS, GKVK", "location": "Bangalore", "contact": "+91 9353819967", "whatsapp": "919353819967", "email": "suryaprakashrana302@gmail.com", "fee": "₹400"},
    {"name": "Dr. Sunil Kumar Reddy", "degree": "Doctor of Plant Medicine", "specialization": "Potato Blight Specialist", "experience": "10 Years", "hospital": "KVK, Chikkaballapur", "location": "Chikkaballapur", "contact": "+91 8296015343", "whatsapp": "918296015343", "email": "suryaprakashrana302@gmail.com", "fee": "₹300"},
    {"name": "Dr. Anjali Patel", "degree": "Ph.D. Plant Protection", "specialization": "Tomato Diseases", "experience": "8 Years", "hospital": "Green Field Agri Clinic", "location": "Jayanagar, Bangalore", "contact": "+91 9353991423", "whatsapp": "919353991423", "email": "suryaprakashrana302@gmail.com", "fee": "₹350"},
    {"name": "Dr. Mohan Gowda", "degree": "Ph.D Horticulture", "specialization": "Organic Disease Control", "experience": "20 Years", "hospital": "State Agriculture Dept", "location": "Koramangala, Bangalore", "contact": "+91 9177161922", "whatsapp": "919177161922", "email": "suryaprakashrana302@gmail.com", "fee": "₹250"}
]

def send_email_to_doctor(doctor_email, farmer_details, disease):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = doctor_email
        msg['Subject'] = f"New Appointment - {disease} - Farmer {farmer_details['name']}"

        body = f"""
        Namaste Doctor,

        You have a new appointment booking from Plant Disease Detection System.

        FARMER DETAILS:
        Name: {farmer_details['name']}
        Phone: {farmer_details['phone']}
        Location: {farmer_details['location']}
        Crop/Disease Detected: {disease}
        Problem: {farmer_details['problem']}

        APPOINTMENT:
        Date: {farmer_details['appt_date']}
        Time: {farmer_details['time']}
        Booking ID: {farmer_details['booking_id']}

        Please contact the farmer.

        Regards,
        Plant Disease Detection System
        """
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email Error: {e}")
        return False

CLASS_NAMES = sorted(os.listdir("dataset/train"))

@st.cache_resource
def load_model():
    return tf.keras.models.load_model("plant_model.h5")
model = load_model()

st.title("🌿 Plant Disease Detection")
uploaded = st.file_uploader("Choose leaf image", type=["jpg","jpeg","png"])

if "disease" not in st.session_state:
    st.session_state.disease = None
if "last_booking" not in st.session_state:
    st.session_state.last_booking = None

if uploaded is not None:
    image = Image.open(uploaded).convert("RGB")
    st.image(image, caption="Uploaded Leaf", use_container_width=True)
    img = image.resize((128,128))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    pred = model.predict(img_array)
    label = CLASS_NAMES[np.argmax(pred)]
    st.session_state.disease = label
    st.success(f"**Prediction: {label}** - {np.max(pred)*100:.2f}%")

if st.session_state.disease:
    label = st.session_state.disease
    st.markdown("---")
    st.header("👨‍⚕️ Recommended Doctors")
    for doc in DOCTORS:
        with st.container(border=True):
            st.subheader(f"{doc['name']} | {doc['experience']}")
            st.write(f"🎓 {doc['degree']} | 🌱 {doc['specialization']}")
            st.write(f"🏥 {doc['hospital']} | 📞 {doc['contact']} | 💰 {doc['fee']}")

    st.markdown("---")
    st.header("📅 Book Appointment")

    with st.form("appointment_form"):
        selected_doctor_name = st.selectbox("Select Doctor", [d["name"] for d in DOCTORS])
        c1, c2 = st.columns(2)
        with c1:
            farmer_name = st.text_input("Farmer Name*")
            farmer_phone = st.text_input("Phone Number*")
        with c2:
            farmer_location = st.text_input("Village / Location*")
            crop_type = st.text_input("Crop Type", value=label)

        c3, c4 = st.columns(2)
        with c3:
            appt_date = st.date_input("Appointment Date", min_value=date.today())
        with c4:
            appt_time = st.selectbox("Time Slot", ["10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM"])

        problem_desc = st.text_area("Describe Problem", f"My crop detected with {label}. Need consultation.")
        submit = st.form_submit_button("✅ Confirm & Notify Doctor", use_container_width=True)

        if submit:
            if not farmer_name or not farmer_phone or not farmer_location:
                st.warning("Fill all * fields")
            else:
                doctor_obj = next(d for d in DOCTORS if d["name"] == selected_doctor_name)
                booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
                farmer_details = {
                    "name": farmer_name, "phone": farmer_phone, "location": farmer_location,
                    "problem": problem_desc, "appt_date": str(appt_date), "time": appt_time,
                    "booking_id": booking_id
                }
                
                # Save to CSV
                pd.DataFrame([{
                    "Booking_ID": booking_id, "Date": str(datetime.now()),
                    "Farmer_Name": farmer_name, "Phone": farmer_phone, "Location": farmer_location,
                    "Crop_Disease": crop_type, "Doctor": selected_doctor_name,
                    "Appointment_Date": str(appt_date), "Time_Slot": appt_time, "Status": "Confirmed"
                }]).to_csv("appointments.csv", mode='a', header=not os.path.exists("appointments.csv"), index=False)

                # Store for WhatsApp/Email buttons
                st.session_state.last_booking = (doctor_obj, farmer_details, label)
                st.success(f"🎉 Booking Confirmed! ID: {booking_id}")
                st.balloons()

    # SHOW WHATSAPP + EMAIL AFTER BOOKING
    if st.session_state.last_booking:
        doctor_obj, farmer_details, disease = st.session_state.last_booking
        
        st.markdown("### 📲 Notify Doctor Now (2-Way)")

        # 1. WhatsApp Message
        wa_text = f"""*New Appointment - Plant Disease System*

Namaste {doctor_obj['name']},

New booking:
*Booking ID:* {farmer_details['booking_id']}
*Farmer:* {farmer_details['name']} ({farmer_details['phone']})
*Location:* {farmer_details['location']}
*Disease:* {disease}
*Date:* {farmer_details['appt_date']} at {farmer_details['time']}
*Problem:* {farmer_details['problem']}

Please contact farmer.
"""
        wa_url = f"https://wa.me/{doctor_obj['whatsapp']}?text={urllib.parse.quote(wa_text)}"

        # 2. Email
        email_sent = False
        if SENDER_EMAIL != "your_email@gmail.com":
            email_sent = send_email_to_doctor(doctor_obj['email'], farmer_details, disease)

        col1, col2 = st.columns(2)
        with col1:
            st.link_button("💬 Send WhatsApp to Doctor", wa_url, use_container_width=True, type="primary")
        with col2:
            if email_sent:
                st.success(f"✅ Email sent to {doctor_obj['email']}")
                st.info("Doctor notified via Email successfully!")
            else:
                st.error("❌ Auto-Email not configured")
                st.code(f"Doctor Email: {doctor_obj['email']}\nSubject: Appointment {farmer_details['booking_id']}")
                st.caption("Add your Gmail App Password at the top of app.py to enable auto-email.")

        if not email_sent and SENDER_EMAIL == "your_email@gmail.com":
            st.warning("⚙️ To enable automatic email: Add your Gmail + App Password at top of app.py")

    if os.path.exists("appointments.csv"):
        with st.expander("📋 View All Bookings"):
            st.dataframe(pd.read_csv("appointments.csv"))