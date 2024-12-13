import pandas as pd
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for  # Import url_for here
from datetime import datetime, timedelta

app = Flask(__name__)

# Check current working directory
print("Current Working Directory:", os.getcwd())

# Check if the CSV file exists
file_path = 'symptoms_diseases.csv'
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Required file '{file_path}' not found. Please ensure it exists in the directory: {os.getcwd()}")

# Load the CSV file
symptom_data = pd.read_csv(file_path)
# Route for doctor login page
@app.route('/doctor_login', methods=['GET', 'POST'])
def doctor_login():
    doctor_mapping = {
        "Dr. Smith": {"specialization": "General Medicine", "username": "drsmith", "password": "password12345"},
        "Dr. Gren": {"specialization": "Dermatology", "username": "drgren", "password": "password1234"},
        "Dr. Brow": {"specialization": "Endocrinology", "username": "drbrow0", "password": "password123"},
       
        # Add other doctors...
    }

    if request.method == 'POST':
        doctor_name = request.form['doctor_name']
        department = request.form['department']
        username = request.form['username']
        password = request.form['password']
        
        for doctor, info in doctor_mapping.items():
            if info['specialization'] == department and info['username'] == username and info['password'] == password:
                # After successful login, redirect to the doctor's dashboard
                return redirect(url_for('doctor_dashboard', doctor_name=doctor))

        return "Invalid credentials. Please try again."

    return render_template('doctor_login.html')

# Doctor mapping for departments
doctor_mapping = {
    "General Medicine": {"doctor": "Dr. Smith", "time_slots": ["10:00 AM", "11:00 AM", "2:00 PM"]},
    "Cardiology": {"doctor": "Dr. Brow", "time_slots": ["9:00 AM", "1:00 PM", "3:00 PM"]},
    "Dermatology": {"doctor": "Dr. Gren", "time_slots": ["10:30 AM", "12:30 PM", "4:00 PM"]},
    "Dermatology": {"doctor": "Dr. Grn", "time_slots": ["1:30 AM", "2:30 PM", "4:00 PM"]},
    "Endocrinology": {"doctor": "Dr. Gree", "time_slots": ["10:30 AM", "12:30 PM", "4:00 PM"]},
    "Pulmonology": {"doctor": "Dr. reen", "time_slots": ["10:30 AM", "12:30 PM", "4:00 PM"]},
    "ENT": {"doctor": "Dr. Gen", "time_slots": ["10:30 AM", "12:30 PM", "4:00 PM"]},
    "Infectious Disease": {"doctor": "Dr. Grn", "time_slots": ["10:30 AM", "12:30 PM", "4:00 PM"]},
    "Surgery": {"doctor": "Dr. Greenn", "time_slots": ["10:30 AM", "12:30 PM", "4:00 PM"]},
    "Hematology": {"doctor": "Dr. Greeen", "time_slots": ["10:30 AM", "12:30 PM", "4:00 PM"]},
    "Rheumatology": {"doctor": "Dr. Gvreen", "time_slots": ["10:30 AM", "12:30 PM", "4:00 PM"]},
    "Nephrology": {"doctor": "Dr. Greedn", "time_slots": ["10:30 AM", "12:30 PM", "4:00 PM"]},
    "Neurology": {"doctor": "Dr. Greenf", "time_slots": ["10:30 AM", "12:30 PM", "4:00 PM"]},
    "Psychiatry": {"doctor": "Dr. Greeng", "time_slots": ["10:30 AM", "12:30 PM", "4:00 PM"]},
    "Optometry": {"doctor": "Dr. Greener", "time_slots": ["10:30 AM", "12:30 PM", "4:00 PM"]},
    "Oncology": {"doctor": "Dr. Greenw", "time_slots": ["10:30 AM", "12:30 PM", "4:00 PM"]},
    "Gastroenterology": {"doctor": "Dr. Gfreen", "time_slots": ["10:30 AM", "12:30 PM", "4:00 PM"]},
    "Endocrinology": {"doctor": "Dr. Greeeen", "time_slots": ["10:30 AM", "12:30 PM", "4:00 PM"]},
}

# Database setup: Create 'appointments' table if it doesn't exist
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor TEXT,
        date TEXT,
        time_slot TEXT,
        patient_id INTEGER
    )
''')
conn.commit()
conn.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        address = request.form['address']
        phone = request.form['phone']
        gender = request.form['gender']

        # Save patient info into the database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER,
                address TEXT,
                phone TEXT,
                gender TEXT
            )
        ''')
        cursor.execute('''
            INSERT INTO patients (name, age, address, phone, gender)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, age, address, phone, gender))
        conn.commit()
        conn.close()

        return redirect('/symptoms')

    return render_template('register.html')


@app.route('/symptoms', methods=['GET', 'POST'])
def symptoms():
    if request.method == 'POST':
        selected_symptoms = request.form.getlist('symptoms')
        return redirect('/analyze', code=307)

    symptoms_list = list(symptom_data.columns[1:-3])
    return render_template('symptoms.html', symptoms=symptoms_list)

@app.route('/analyze', methods=['POST'])
def analyze():
    selected_symptoms = request.form.getlist('symptoms')

    filtered_diseases = symptom_data.copy()
    for symptom in selected_symptoms:
        filtered_diseases = filtered_diseases[filtered_diseases[symptom] == 1]

    if not filtered_diseases.empty:
        disease = filtered_diseases.iloc[0]['Disease']
        department = filtered_diseases.iloc[0]['Department']
        floor = filtered_diseases.iloc[0]['Floor']
    else:
        disease = "Unknown"
        department = "General Medicine"
        floor = "1"

    doctor_info = doctor_mapping.get(department, {"doctor": "Dr. Smith", "time_slots": ["9:00 AM"]})
    doctor = doctor_info["doctor"]
    time_slots = doctor_info["time_slots"]

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    today = datetime.now().date()

    cursor.execute('''
        SELECT time_slot FROM appointments
        WHERE doctor = ? AND date = ?
    ''', (doctor, str(today)))
    booked_slots = [row[0] for row in cursor.fetchall()]

    available_slot = None
    for slot in time_slots:
        if slot not in booked_slots:
            available_slot = slot
            break

    if not available_slot:
        today += timedelta(days=1)
        available_slot = time_slots[0]

    cursor.execute('''
        INSERT INTO appointments (doctor, date, time_slot, patient_id)
        VALUES (?, ?, ?, ?)
    ''', (doctor, str(today), available_slot, 1))  # Replace 1 with actual patient ID logic
    conn.commit()
    conn.close()

    return render_template(
        'doctor.html',
        disease=disease,
        department=department,
        doctor=doctor,
        floor=floor,
        assigned_slot=available_slot,
        date=today
    )

@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/submit_payment', methods=['POST'])
def submit_payment():
    name = request.form['name']
    card_number = request.form['card_number']
    expiry_date = request.form['expiry_date']
    cvv = request.form['cvv']

    print(f"Payment details submitted: {name}, {card_number}, {expiry_date}, {cvv}")
    return redirect('/payment_success')

@app.route('/payment_success')
def payment_success():
    return render_template('payment_success.html')

@app.route('/patients')
def patients():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients")
    patient_list = cursor.fetchall()
    conn.close()
    return render_template('patients.html', patients=patient_list)
 # Route for doctor's dashboard after successful login
@app.route('/doctor_dashboard/<doctor_name>', methods=['GET', 'POST'])
def doctor_dashboard(doctor_name):
    # Retrieve doctor information (time slots, specialization, etc.)
    doctor_info = doctor_mapping.get(doctor_name, {"doctor": "Dr. Smith", "time_slots": ["9:00 AM"], "specialization": "General Medicine"})
    
    # Retrieve appointments for the doctor
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    today = datetime.now().date()
    
    cursor.execute('''SELECT id, patient_id, time_slot, date FROM appointments WHERE doctor = ? AND date >= ? ORDER BY date, time_slot''', 
                   (doctor_name, str(today)))
    appointments = cursor.fetchall()
    
    # Fetch patient details for appointments
    appointment_details = []
    for appointment in appointments:
        cursor.execute('SELECT name, age, phone FROM patients WHERE id = ?', (appointment[1],))
        patient = cursor.fetchone()
        appointment_details.append({
            'appointment_id': appointment[0],
            'patient_name': patient[0],
            'patient_age': patient[1],
            'patient_phone': patient[2],
            'time_slot': appointment[2],
            'date': appointment[3]
        })
    
    conn.close()

    return render_template('doctor_dashboard.html', doctor_name=doctor_name, doctor_info=doctor_info, appointments=appointment_details)


if __name__ == '__main__':
    app.run(debug=True)

