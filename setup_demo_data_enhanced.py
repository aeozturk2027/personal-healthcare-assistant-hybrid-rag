"""
Enhanced Demo Data Setup - Çok katmanlı graph yapısı

🎯 DİNAMİK TARİHLER:
   Bu script çalıştırıldığında TÜM TARİHLER otomatik olarak 
   o günün tarihine göre ayarlanır.
   
   Örnek:
   - Bugünkü randevu: Script'in çalıştığı gün
   - Geçmiş randevular: 90 gün önce, 60 gün önce
   - Gelecek randevular: 7 gün sonra, 14 gün sonra
   - Test sonuçları: Bugüne yakın tarihler
   
   ✅ Jüri ne zaman test ederse etsin, tarihler mantıklı olacak!
"""
import os
from dotenv import load_dotenv
from src.neo4j_client import Neo4jClient
from datetime import date, timedelta

load_dotenv()

# Neo4j connection
neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
neo4j_user = os.getenv("NEO4J_USER", "neo4j")
neo4j_password = os.getenv("NEO4J_PASSWORD")

if not neo4j_password:
    print("❌ NEO4J_PASSWORD not set!")
    exit(1)

client = Neo4jClient(neo4j_uri, neo4j_user, neo4j_password)

# Verify connection
if not client.verify_connection():
    print("❌ Cannot connect to Neo4j!")
    exit(1)

print("✓ Connected to Neo4j")

# Clear old data (her zaman temiz başla)
print("🗑️ Eski verileri temizleniyor...")
client.clear_all_data()
print("✓ Eski veriler temizlendi")

# Create schema
client.create_schema()

# ==================== CREATE USER ====================
USER_ID = "demo_user"
client.create_user(USER_ID, "Demo User", age=35)
print(f"✓ Created user: {USER_ID}")

# ==================== CREATE DOCTORS ====================
print("\n📋 Creating Doctors...")

doctors = [
    {
        'name': 'Dr. Sarah Johnson',
        'specialty': 'Cardiology',
        'hospital': 'City Medical Center',
        'phone': '+1-555-0101'
    },
    {
        'name': 'Dr. Michael Chen',
        'specialty': 'General Practice',
        'hospital': 'Community Health Clinic',
        'phone': '+1-555-0102'
    },
    {
        'name': 'Dr. Emily Rodriguez',
        'specialty': 'Ophthalmology',
        'hospital': 'Vision Care Center',
        'phone': '+1-555-0103'
    },
    {
        'name': 'Dr. James Wilson',
        'specialty': 'Endocrinology',
        'hospital': 'Diabetes & Metabolic Institute',
        'phone': '+1-555-0104'
    }
]

for doc in doctors:
    client.create_doctor(doc)
    print(f"  ✓ {doc['name']} ({doc['specialty']})")

# ==================== PAST APPOINTMENTS ====================
print("\n📅 Creating Past Appointments...")

today = date.today()

# Past appointment 1 (3 months ago)
past_apt1 = client.create_appointment_with_doctor(USER_ID, "Dr. Michael Chen", {
    'date': str(today - timedelta(days=90)),
    'time': '10:00',
    'status': 'completed',
    'location': 'Community Health Clinic, Room 201',
    'notes': 'Annual checkup'
})
apt1_id = dict(past_apt1["a"])['id']

# Add notes from doctor
client.add_appointment_notes(apt1_id, {
    'summary': 'Patient came in for annual physical examination.',
    'diagnosis': 'Hypertension detected (BP: 145/92). Patient started on Lisinopril.',
    'recommendations': 'Monitor blood pressure daily. Reduce sodium intake. Exercise 30min/day.',
    'follow_up': 'Return in 3 months for BP check'
})
print(f"  ✓ Past appointment: Dr. Chen (3 months ago) - Hypertension diagnosed")

# Test results from that appointment
client.create_test_result(USER_ID, {
    'test_name': 'Blood Pressure',
    'test_date': str(today - timedelta(days=90)),
    'result': '145/92',
    'unit': 'mmHg',
    'normal_range': '<120/80',
    'status': 'high'
}, appointment_id=apt1_id)

client.create_test_result(USER_ID, {
    'test_name': 'Cholesterol (Total)',
    'test_date': str(today - timedelta(days=90)),
    'result': '220',
    'unit': 'mg/dL',
    'normal_range': '<200',
    'status': 'high'
}, appointment_id=apt1_id)

print(f"  ✓ Test results added: BP, Cholesterol")

# Past appointment 2 (2 months ago - Endocrinologist)
past_apt2 = client.create_appointment_with_doctor(USER_ID, "Dr. James Wilson", {
    'date': str(today - timedelta(days=60)),
    'time': '14:30',
    'status': 'completed',
    'location': 'Diabetes & Metabolic Institute',
    'notes': 'Diabetes screening'
})
apt2_id = dict(past_apt2["a"])['id']

client.add_appointment_notes(apt2_id, {
    'summary': 'Patient referred for diabetes screening due to family history.',
    'diagnosis': 'Type 2 Diabetes confirmed (HbA1c: 7.2%). Started on Metformin.',
    'recommendations': 'Low-carb diet. Monitor blood glucose. Weight management program.',
    'follow_up': 'Return in 1 month for medication adjustment'
})
print(f"  ✓ Past appointment: Dr. Wilson (2 months ago) - Diabetes diagnosed")

# Test results
client.create_test_result(USER_ID, {
    'test_name': 'HbA1c (Glycated Hemoglobin)',
    'test_date': str(today - timedelta(days=60)),
    'result': '7.2',
    'unit': '%',
    'normal_range': '<5.7',
    'status': 'high'
}, appointment_id=apt2_id)

client.create_test_result(USER_ID, {
    'test_name': 'Fasting Blood Glucose',
    'test_date': str(today - timedelta(days=60)),
    'result': '142',
    'unit': 'mg/dL',
    'normal_range': '70-100',
    'status': 'high'
}, appointment_id=apt2_id)

print(f"  ✓ Test results added: HbA1c, Glucose")

# ==================== CURRENT/FUTURE APPOINTMENTS ====================
print("\n📆 Creating Current/Future Appointments...")

# Today's appointment
client.create_appointment_with_doctor(USER_ID, "Dr. Sarah Johnson", {
    'date': str(today),
    'time': '14:00',
    'status': 'scheduled',
    'location': 'City Medical Center, Cardiology Dept, Room 305',
    'notes': 'Follow-up cardiology checkup'
})
print(f"  ✓ Today: Dr. Sarah Johnson (Cardiology)")

# Next week
client.create_appointment_with_doctor(USER_ID, "Dr. Michael Chen", {
    'date': str(today + timedelta(days=7)),
    'time': '10:30',
    'status': 'scheduled',
    'location': 'Community Health Clinic',
    'notes': 'Blood pressure follow-up'
})
print(f"  ✓ Next week: Dr. Michael Chen (BP follow-up)")

# 2 weeks from now
client.create_appointment_with_doctor(USER_ID, "Dr. Emily Rodriguez", {
    'date': str(today + timedelta(days=14)),
    'time': '15:00',
    'status': 'scheduled',
    'location': 'Vision Care Center',
    'notes': 'Diabetic eye screening'
})
print(f"  ✓ In 2 weeks: Dr. Emily Rodriguez (Eye screening)")

# ==================== MEDICATIONS ====================
print("\n💊 Creating Medications...")

medications = [
    {
        'name': 'Lisinopril',
        'dosage': '10mg',
        'frequency': 'Once daily (morning)',
        'start_date': str(today - timedelta(days=90)),
        'notes': 'For blood pressure control'
    },
    {
        'name': 'Aspirin',
        'dosage': '81mg',
        'frequency': 'Once daily (morning)',
        'start_date': str(today - timedelta(days=90)),
        'notes': 'Blood thinner, cardiovascular protection'
    },
    {
        'name': 'Metformin',
        'dosage': '500mg',
        'frequency': 'Twice daily (with meals)',
        'start_date': str(today - timedelta(days=60)),
        'notes': 'For diabetes management'
    },
    {
        'name': 'Atorvastatin',
        'dosage': '20mg',
        'frequency': 'Once daily (evening)',
        'start_date': str(today - timedelta(days=90)),
        'notes': 'For cholesterol management'
    }
]

for med in medications:
    client.create_medication(USER_ID, med)
    print(f"  ✓ {med['name']} {med['dosage']} - {med['frequency']}")

# ==================== CONDITIONS ====================
print("\n🩺 Creating Health Conditions...")

conditions = [
    {
        'name': 'Hypertension (High Blood Pressure)',
        'diagnosed_date': str(today - timedelta(days=90)),
        'severity': 'Moderate',
        'notes': 'Stage 1 hypertension, controlled with medication'
    },
    {
        'name': 'Type 2 Diabetes Mellitus',
        'diagnosed_date': str(today - timedelta(days=60)),
        'severity': 'Mild',
        'notes': 'Early stage, diet and medication managed'
    },
    {
        'name': 'Hyperlipidemia (High Cholesterol)',
        'diagnosed_date': str(today - timedelta(days=90)),
        'severity': 'Moderate',
        'notes': 'Total cholesterol 220 mg/dL, on statin therapy'
    }
]

for cond in conditions:
    client.create_condition(USER_ID, cond)
    print(f"  ✓ {cond['name']} ({cond['severity']})")

# ==================== LINK MEDICATIONS TO CONDITIONS ====================
print("\n🔗 Linking Medications to Conditions...")

links = [
    ('Lisinopril', 'Hypertension (High Blood Pressure)'),
    ('Metformin', 'Type 2 Diabetes Mellitus'),
    ('Atorvastatin', 'Hyperlipidemia (High Cholesterol)'),
]

for med, cond in links:
    client.link_medication_to_condition(USER_ID, med, cond)
    print(f"  ✓ {med} → {cond}")

# ==================== RECENT TEST RESULTS ====================
print("\n🧪 Adding Recent Test Results...")

recent_tests = [
    {
        'test_name': 'Blood Pressure (Home Reading)',
        'test_date': str(today - timedelta(days=1)),
        'result': '128/84',
        'unit': 'mmHg',
        'normal_range': '<120/80',
        'status': 'borderline'
    },
    {
        'test_name': 'Fasting Blood Glucose (Home)',
        'test_date': str(today),
        'result': '118',
        'unit': 'mg/dL',
        'normal_range': '70-100',
        'status': 'borderline'
    }
]

for test in recent_tests:
    client.create_test_result(USER_ID, test)
    print(f"  ✓ {test['test_name']}: {test['result']} {test['unit']}")

# ==================== SUMMARY ====================
print("\n" + "="*60)
print("✅ ENHANCED DEMO DATA SETUP COMPLETE!")
print("="*60)

profile = client.get_user_complete_profile(USER_ID)

print(f"\n📊 Graph Statistics:")
print(f"  • User: {USER_ID}")
print(f"  • Doctors: 4")
print(f"  • Appointments: 5 (2 past, 1 today, 2 future)")
print(f"  • Medications: 4")
print(f"  • Conditions: 3")

print(f"\n📅 Dynamic Dates (relative to today: {today}):")
print(f"  • Past appointments: {today - timedelta(days=90)} and {today - timedelta(days=60)}")
print(f"  • Today's appointment: {today}")
print(f"  • Future appointments: {today + timedelta(days=7)} and {today + timedelta(days=14)}")
print(f"  • Recent test results: {today - timedelta(days=1)} and {today}")
print(f"  • Test Results: 6")
print(f"  • Appointment Notes: 2")
print(f"  • Condition-Medication Links: 3")

print(f"\n🕸️ Graph Relationships:")
print(f"  User → Appointments → Doctors")
print(f"  User → Medications ← Conditions")
print(f"  User → Test Results ← Appointments")
print(f"  Appointments → Notes (from doctors)")

print(f"\n🚀 Ready to test! Run:")
print(f"  streamlit run app_hybrid.py")

print(f"\n💡 Try these queries:")
print(f"  • 'What were the results of my last blood pressure test?'")
print(f"  • 'What did Dr. Chen say in my last appointment?'")
print(f"  • 'Which medication am I taking for diabetes?'")
print(f"  • 'Show me all my test results'")

client.close()

