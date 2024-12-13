import pandas as pd
import os
import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Check current working directory
print("Current Working Directory:", os.getcwd())

# Check if the CSV file exists
file_path = 'symptoms_diseases.csv'
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Required file '{file_path}' not found. Please ensure it exists in the directory: {os.getcwd()}")

# Load the CSV file
symptom_data = pd.read_csv(file_path)

# Route for home page
@app.route('/')
def home():
    return render_template('home.html')

# Route for patient registration
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

        # Redirect to symptoms page
        return redirect('/symptoms')

    # If GET request, render the registration page
    return render_template('register.html')

# Route to process symptom selection
@app.route('/diagnosis', methods=['POST'])
def diagnosis():
    selected_symptoms = request.form.getlist('symptom')  # Get a list of selected symptoms
    
    # Filter the symptom data based on selected symptoms
    filtered_data = symptom_data[symptom_data['Symptom'].isin(selected_symptoms)]

    # Check if any disease is found based on the symptoms
    if filtered_data.empty:
        message = "No disease found based on the selected symptoms."
    else:
        # Get department and floor number from the first matched disease (assuming unique diagnosis)
        department = filtered_data.iloc[0]['Department']
        floor_number = filtered_data.iloc[0]['Floor']
        message = f"Based on your symptoms, a possible diagnosis is {filtered_data.iloc[0]['Disease']}. Please visit the {department} department on floor {floor_number} for further evaluation."

    return render_template('diagnosis.html', message=message)

# Route for symptoms page
@app.route('/symptoms', methods=['GET', 'POST'])
def symptoms():
    if request.method == 'POST':
        selected_symptoms = request.form.getlist('symptoms')
        return redirect('/analyze', code=307)  # Perform the analysis

    symptoms_list = list(symptom_data.columns[1:-3])  # All symptoms except Disease, Department, Floor, and Doctor
    return render_template('symptoms.html', symptoms=symptoms_list)

# Analyze symptoms and suggest department
# Route for symptom selection and analysis
@app.route('/analyze', methods=['POST'])
def analyze():
    selected_symptoms = request.form.getlist('symptom')

    # Filter diseases with selected symptoms
    filtered_diseases = symptom_data.copy()
    for symptom in selected_symptoms:
        filtered_diseases = filtered_diseases[filtered_diseases[symptom] == 1]

    # Get the most probable disease, department, and floor
    if not filtered_diseases.empty:
        disease = filtered_diseases.iloc[0]['Disease']
        department = filtered_diseases.iloc[0]['Department']
        floor = filtered_diseases.iloc[0]['Floor']
        message = f"Based on your symptoms, a possible diagnosis is {disease}. " \
                  f"Please visit the {department} department on floor {floor} for further evaluation."
    else:
        disease = None
        department = "General Medicine" 
        floor = "1" 
        message = "No specific disease found based on your symptoms. " \
                  "Please consult a doctor in the General Medicine department."

    
    # Map to doctor (based on department)
    doctor_mapping = {
        "General Medicine": "Dr. Smith",
        "Pulmonology": "Dr. Johnson",
        "Neurology": "Dr. Lee",
        "Cardiology": "Dr. Patel",
        "Endocrinology": "Dr. Gupta",
        "Dermatology": "Dr. Roy",
        "Infectious Disease": "Dr. Fernandes",
        "Gastroenterology": "Dr. Thomas",
        "Rheumatology": "Dr. Bose",
        "Hematology": "Dr. Sharma",
        "Nephrology": "Dr. Rao",
        "Oncology": "Dr. Smith",
        "ENT": "Dr. Singh",
        "Surgery": "Dr. Sarkaar",
        "Psichiatry": "Dr. Shyam",
        "Optometry": "Dr. Siddharth"# Add more departments and doctors as needed
    }
    
    doctor = doctor_mapping.get(department, "Dr. Smith")

    # Render the doctor information page with department, doctor, and floor
    return render_template('doctor.html', message=message, disease=disease, department=department, doctor=doctor, floor=floor)

# Route for payment page
@app.route('/payment')
def payment():
    return render_template('payment.html')

# Route for handling the payment form submission
@app.route('/submit_payment', methods=['POST'])
def submit_payment():
    name = request.form['name']
    card_number = request.form['card_number']
    expiry_date = request.form['expiry_date']
    cvv = request.form['cvv']

    # Here, you would handle the payment processing logic (e.g., using a payment gateway API)
    # For now, just print the data for testing
    print(f"Payment details submitted: {name}, {card_number}, {expiry_date}, {cvv}")
    
    # Redirect to a confirmation or success page
    return redirect('/payment_success')

# Route for payment success page
@app.route('/payment_success')
def payment_success():
    return render_template('payment_success.html')

# Route for displaying all patients
@app.route('/patients')
def patients():
    # Connect to the database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Retrieve all patients from the database
    cursor.execute("SELECT * FROM patients")
    patient_list = cursor.fetchall()
    conn.close()
    
    # Render the patients data to a template
    return render_template('patients.html', patients=patient_list)

if __name__ == '__main__': 
    app.run(debug=True)
