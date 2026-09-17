import os
import streamlit as st
import time
import tensorflow as tf
import numpy as np
from PIL import Image
import pandas as pd
from datetime import datetime, date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.parse
import hashlib
import plotly.express as px

st.set_page_config(page_title="KrishiRakshak - Plant Doctor AI", page_icon="🌿", layout="wide")
if os.path.exists("logo.jpeg"):
    st.sidebar.image("logo.jpeg", use_column_width=True)

# --- CONFIG ---
SENDER_EMAIL = "suryaprakashrana302@gmail.com"
SENDER_APP_PASSWORD = "qdfo hezx jang fkmb"
ADMIN_EMAIL = "admin@krishirakshak.com"
ADMIN_PASS_HASH = hashlib.sha256("admin123".encode()).hexdigest()

DOCTORS = [
    {"name": "Dr. R. K. Sharma", "degree": "Ph.D. Plant Pathology", "specialization": "Potato & Tomato Diseases", "experience": "15 Years", "hospital": "ICAR - IIHR, Hessarghatta", "location": "Bangalore", "contact": "+91 7061060726", "whatsapp": "917061060726", "email": "suryaprakashrana302@gmail.com", "fee": "₹500"},
    {"name": "Dr. Priya Nair", "degree": "Ph.D Agri Entomology", "specialization": "Crop Disease Management", "experience": "12 Years", "hospital": "UAS, GKVK", "location": "Bangalore", "contact": "+91 9353819967", "whatsapp": "919353819967", "email": "suryaprakashrana302@gmail.com", "fee": "₹400"},
    {"name": "Dr. Sunil Kumar Reddy", "degree": "Doctor of Plant Medicine", "specialization": "Potato Blight Specialist", "experience": "10 Years", "hospital": "KVK, Chikkaballapur", "location": "Chikkaballapur", "contact": "+91 8296015343", "whatsapp": "918296015343", "email": "suryaprakashrana302@gmail.com", "fee": "₹300"},
    {"name": "Dr. Anjali Patel", "degree": "Ph.D. Plant Protection", "specialization": "Tomato Diseases", "experience": "8 Years", "hospital": "Green Field Agri Clinic", "location": "Jayanagar, Bangalore", "contact": "+91 9353991423", "whatsapp": "919353991423", "email": "suryaprakashrana302@gmail.com", "fee": "₹350"},
    {"name": "Dr. Mohan Gowda", "degree": "Ph.D Horticulture", "specialization": "Organic Disease Control", "experience": "20 Years", "hospital": "State Agriculture Dept", "location": "Koramangala, Bangalore", "contact": "+91 9177161922", "whatsapp": "919177161922", "email": "suryaprakashrana302@gmail.com", "fee": "₹250"}
]

def hash_password(p): return hashlib.sha256(p.encode()).hexdigest()

def check_user(email, password):
    if email == ADMIN_EMAIL and hash_password(password) == ADMIN_PASS_HASH:
        return "admin"
    if not os.path.exists("users.csv"): return False
    df = pd.read_csv("users.csv")
    hashed = hash_password(password)
    user = df[(df['email'] == email) & (df['password'] == hashed)]
    return "user" if not user.empty else False

def save_user(name, email, password, phone):
    hashed = hash_password(password)
    pd.DataFrame([{"name": name, "email": email, "password": hashed, "phone": phone, "joined": str(date.today())}]).to_csv("users.csv", mode='a', header=not os.path.exists("users.csv"), index=False)

def send_email_to_doctor(doctor_email, farmer_details, disease):
    try:
        if SENDER_EMAIL == "your_email@gmail.com": return False
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = doctor_email
        msg['Subject'] = f"New Appointment - {disease} - {farmer_details['name']}"
        body = f"Farmer: {farmer_details['name']}\nPhone: {farmer_details['phone']}\nLocation: {farmer_details['location']}\nDisease: {disease}\nDate: {farmer_details['appt_date']} {farmer_details['time']}\nBooking ID: {farmer_details['booking_id']}"
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except: return False

@st.cache_resource
def load_model():
    model = tf.keras.models.load_model("plant_model.h5", compile=False)
    return model

CLASS_NAMES = ['Potato___Early_blight', 'Potato___healthy', 'Potato___Late_blight', 'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___healthy', 'Tomato___Late_blight', 'Tomato___Leaf_Mold']

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_name = ""
    st.session_state.role = ""

# --- LOGIN PAGE ---
if not st.session_state.logged_in:
    st.title("🌿 KrishiRakshak - Plant Doctor AI")
    st.markdown("#### AI-Based Disease Detection with Doctor Consultation")

    if "auth_tab" not in st.session_state:
        st.session_state.auth_tab = "🔐 User Login"
    if "signup_done" not in st.session_state:
        st.session_state.signup_done = False

    auth_choice = st.radio(
        "Select", ["🔐 User Login", "📝 Sign Up", "🛡️ Admin Login"],
        horizontal=True, label_visibility="collapsed", key="auth_tab"
    )

    if auth_choice == "🔐 User Login":
        if st.session_state.signup_done:
            st.success("✅ Account Created! Please login now.")
            st.session_state.signup_done = False
        email = st.text_input("Email", key="u_email")
        password = st.text_input("Password", type="password", key="u_pass")
        if st.button("Login as User", use_container_width=True, type="primary"):
            role = check_user(email, password)
            if role == "user":
                df = pd.read_csv("users.csv")
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.user_name = df[df['email']==email].iloc[0]['name']
                st.session_state.role = "user"
                st.rerun()
            else: st.error("Invalid credentials. Sign up first.")

    elif auth_choice == "📝 Sign Up":
        name = st.text_input("Full Name*")
        phone = st.text_input("Phone*")
        new_email = st.text_input("Email*")
        new_pass = st.text_input("Create Password*", type="password")
        confirm_pass = st.text_input("Confirm Password*", type="password")
        if st.button("Create Account", use_container_width=True):
            if not name or not new_email or not new_pass: st.warning("Fill all *")
            elif new_pass!= confirm_pass: st.error("Passwords don't match")
            elif os.path.exists("users.csv") and new_email in pd.read_csv("users.csv")['email'].values: st.error("Email exists")
            else:
                save_user(name, new_email, new_pass, phone)
                st.session_state.signup_done = True
                st.success("Account Created! Redirecting to Login...")
                st.balloons()
                time.sleep(1)
                st.session_state.auth_tab = "🔐 User Login"
                st.rerun()

    else:
        st.warning("For Project Admin Only")
        a_email = st.text_input("Admin Email", key="a_email")
        a_pass = st.text_input("Admin Password", type="password", key="a_pass")
        if st.button("Login as Admin", use_container_width=True):
            if check_user(a_email, a_pass) == "admin":
                st.session_state.logged_in = True
                st.session_state.user_email = a_email
                st.session_state.user_name = "Admin"
                st.session_state.role = "admin"
                st.rerun()
            else: st.error("Invalid Admin Credentials")
        st.caption(f"Demo: {ADMIN_EMAIL} / admin123")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.title(f"Hi, {st.session_state.user_name} 👋")
    st.write(f"Role: {st.session_state.role.upper()}")
    st.markdown("---")
    if st.session_state.role == "admin":
        menu = st.radio("Admin Panel", ["📊 Admin Dashboard", "👥 All Users", "📋 All Appointments", "👨‍⚕️ Manage Doctors", "🔬 Test Model", "🚪 Logout"])
    else:
        menu = st.radio("Navigation", ["📊 Dashboard", "🔬 Detect Disease", "👨‍⚕️ Doctors & Booking", "📋 My Appointments", "🚪 Logout"])

# --- ADMIN & USER PANEL (rest same as yours) ---
if st.session_state.role == "admin":
    if menu == "📊 Admin Dashboard":
        st.title("🛡️ Admin Dashboard")
        c1, c2, c3, c4 = st.columns(4)
        total_users = len(pd.read_csv("users.csv")) if os.path.exists("users.csv") else 0
        total_appts = len(pd.read_csv("appointments.csv")) if os.path.exists("appointments.csv") else 0
        c1.metric("Total Farmers", total_users)
        c2.metric("Total Appointments", total_appts)
        c3.metric("Doctors", len(DOCTORS))
        c4.metric("Diseases", len(CLASS_NAMES))
        if os.path.exists("appointments.csv"):
            df = pd.read_csv("appointments.csv")
            st.bar_chart(df['Crop_Disease'].value_counts())
            fig = px.pie(df, names='Crop_Disease', title='Disease Distribution')
            st.plotly_chart(fig)

    elif menu == "👥 All Users":
        st.title("👥 Registered Farmers")
        if os.path.exists("users.csv"):
            st.dataframe(pd.read_csv("users.csv"), use_container_width=True)

    elif menu == "📋 All Appointments":
        st.title("📋 All Appointments")
        if os.path.exists("appointments.csv"):
            st.dataframe(pd.read_csv("appointments.csv"), use_container_width=True)

    elif menu == "👨‍⚕️ Manage Doctors":
        st.title("👨‍⚕️ Doctors")
        for doc in DOCTORS:
            with st.container(border=True):
                st.subheader(doc['name'])
                st.write(f"{doc['specialization']} | {doc['hospital']} | {doc['fee']}")

    elif menu == "🔬 Test Model":
        st.title("🔬 Test Model (Admin)")
        uploaded = st.file_uploader("Upload leaf", type=["jpg","jpeg","png"])
        if uploaded:
            image = Image.open(uploaded).convert("RGB")
            st.image(image, use_container_width=True)
            img = image.resize((128,128))
            arr = np.expand_dims(np.array(img)/255.0, axis=0)
            model = load_model()
            pred = model.predict(arr)
            st.success(f"Prediction: {CLASS_NAMES[np.argmax(pred)]} {np.max(pred)*100:.2f}%")

else:
    if menu == "📊 Dashboard":
        st.title("📊 My Dashboard")
        st.info("Go to Detect Disease to start!")

    elif menu == "🔬 Detect Disease":
        st.title("🔬 Detect Disease")
        if "disease" not in st.session_state: st.session_state.disease = None
        uploaded = st.file_uploader("Choose leaf", type=["jpg","jpeg","png"])
        if uploaded:
            image = Image.open(uploaded).convert("RGB")
            st.image(image, use_container_width=True)
            img = image.resize((128,128))
            arr = np.expand_dims(np.array(img)/255.0, axis=0)
            model = load_model()
            pred = model.predict(arr)
            label = CLASS_NAMES[np.argmax(pred)]
            st.session_state.disease = label
            st.success(f"{label} - {np.max(pred)*100:.2f}%")

    elif menu == "👨‍⚕️ Doctors & Booking":
        st.title("👨‍⚕️ Book Doctor")
        disease = st.session_state.get("disease", "Upload leaf first")
        st.info(f"Disease: {disease}")
        if "last_booking" not in st.session_state: st.session_state.last_booking = None
        with st.form("booking"):
            doc_name = st.selectbox("Select Doctor", [d["name"] for d in DOCTORS])
            farmer_name = st.text_input("Farmer Name", value=st.session_state.user_name)
            farmer_phone = st.text_input("Phone*")
            farmer_loc = st.text_input("Location*")
            appt_date = st.date_input("Date", min_value=date.today())
            appt_time = st.selectbox("Time", ["10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM"])
            problem = st.text_area("Problem", f"Disease: {disease}")
            submit = st.form_submit_button("✅ Book & Notify", type="primary")
            if submit:
                if not farmer_phone or not farmer_loc: st.warning("Fill phone & location")
                else:
                    doctor_obj = next(d for d in DOCTORS if d["name"]==doc_name)
                    booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    details = {"name": farmer_name, "phone": farmer_phone, "location": farmer_loc, "appt_date": str(appt_date), "time": appt_time, "booking_id": booking_id, "problem": problem}
                    pd.DataFrame([{"Booking_ID": booking_id, "User_Email": st.session_state.user_email, "Farmer_Name": farmer_name, "Phone": farmer_phone, "Location": farmer_loc, "Crop_Disease": disease, "Doctor": doc_name, "Appointment_Date": str(appt_date), "Time_Slot": appt_time, "Status": "Confirmed"}]).to_csv("appointments.csv", mode='a', header=not os.path.exists("appointments.csv"), index=False)
                    st.session_state.last_booking = (doctor_obj, details, disease)
                    st.success(f"Booked! {booking_id}")
                    st.balloons()
        if st.session_state.last_booking:
            doctor_obj, details, disease = st.session_state.last_booking
            wa_text = f"*Appointment* ID:{details['booking_id']} Farmer:{details['name']} Phone:{details['phone']} Disease:{disease} Date:{details['appt_date']} {details['time']}"
            wa_url = f"https://wa.me/{doctor_obj['whatsapp']}?text={urllib.parse.quote(wa_text)}"
            sent = send_email_to_doctor(doctor_obj['email'], details, disease)
            c1, c2 = st.columns(2)
            c1.link_button("💬 WhatsApp Doctor", wa_url, use_container_width=True, type="primary")
            if sent: c2.success(f"✅ Email sent")

    elif menu == "📋 My Appointments":
        st.title("📋 My Appointments")
        if os.path.exists("appointments.csv"):
            df = pd.read_csv("appointments.csv")
            my_df = df[df['User_Email']==st.session_state.user_email] if 'User_Email' in df.columns else df
            st.dataframe(my_df, use_container_width=True)
        else: st.info("No appointments")

if menu == "🚪 Logout":
    st.session_state.logged_in = False
    st.session_state.role = ""
    st.rerun()