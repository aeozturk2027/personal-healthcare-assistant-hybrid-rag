"""
Neo4j client ve bağlantı yönetimi
"""
from neo4j import GraphDatabase
from typing import List, Dict, Optional
from datetime import datetime, date
import os

class Neo4jClient:
    """Neo4j veritabanı client'ı"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        print(f"✓ Neo4j bağlantısı kuruldu: {uri}")
    
    def close(self):
        """Bağlantıyı kapat"""
        self.driver.close()
    
    def verify_connection(self):
        """Bağlantıyı test et"""
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                return result.single()["test"] == 1
        except Exception as e:
            print(f"❌ Neo4j bağlantı hatası: {e}")
            return False
    
    def create_schema(self):
        """Gelişmiş schema'yı oluştur"""
        with self.driver.session() as session:
            # Constraints (unique IDs)
            queries = [
                "CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE",
                "CREATE CONSTRAINT appointment_id IF NOT EXISTS FOR (a:Appointment) REQUIRE a.id IS UNIQUE",
                "CREATE CONSTRAINT medication_id IF NOT EXISTS FOR (m:Medication) REQUIRE m.id IS UNIQUE",
                "CREATE CONSTRAINT condition_id IF NOT EXISTS FOR (c:Condition) REQUIRE c.id IS UNIQUE",
                "CREATE CONSTRAINT doctor_id IF NOT EXISTS FOR (d:Doctor) REQUIRE d.id IS UNIQUE",
                "CREATE CONSTRAINT test_result_id IF NOT EXISTS FOR (t:TestResult) REQUIRE t.id IS UNIQUE",
                "CREATE CONSTRAINT note_id IF NOT EXISTS FOR (n:AppointmentNote) REQUIRE n.id IS UNIQUE"
            ]
            
            for query in queries:
                try:
                    session.run(query)
                except Exception as e:
                    # Constraint zaten varsa devam et
                    pass
            
            print("✓ Neo4j schema oluşturuldu")
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, user_id: str, name: str, age: Optional[int] = None):
        """Yeni kullanıcı oluştur"""
        with self.driver.session() as session:
            query = """
            CREATE (u:User {
                id: $user_id,
                name: $name,
                age: $age,
                created_at: datetime()
            })
            RETURN u
            """
            result = session.run(query, user_id=user_id, name=name, age=age)
            return result.single()
    
    def get_user(self, user_id: str):
        """Kullanıcı bilgilerini getir"""
        with self.driver.session() as session:
            query = """
            MATCH (u:User {id: $user_id})
            RETURN u
            """
            result = session.run(query, user_id=user_id)
            record = result.single()
            return dict(record["u"]) if record else None
    
    # ==================== APPOINTMENT OPERATIONS ====================
    
    def create_appointment(self, user_id: str, appointment_data: Dict):
        """Randevu oluştur"""
        with self.driver.session() as session:
            query = """
            MATCH (u:User {id: $user_id})
            CREATE (a:Appointment {
                id: randomUUID(),
                date: date($date),
                time: $time,
                doctor: $doctor,
                specialty: $specialty,
                location: $location,
                notes: $notes,
                created_at: datetime()
            })
            CREATE (u)-[:HAS_APPOINTMENT]->(a)
            RETURN a
            """
            result = session.run(query, 
                user_id=user_id,
                date=appointment_data.get('date'),
                time=appointment_data.get('time'),
                doctor=appointment_data.get('doctor'),
                specialty=appointment_data.get('specialty', ''),
                location=appointment_data.get('location', ''),
                notes=appointment_data.get('notes', '')
            )
            return result.single()
    
    def get_user_appointments(self, user_id: str, date_filter: Optional[str] = None):
        """Kullanıcının randevularını getir (doctor bilgisiyle birlikte)"""
        with self.driver.session() as session:
            if date_filter:
                query = """
                MATCH (u:User {id: $user_id})-[:HAS_APPOINTMENT]->(a:Appointment)
                WHERE a.date = date($date_filter)
                OPTIONAL MATCH (a)-[:WITH_DOCTOR]->(d:Doctor)
                RETURN a, d.name as doctor_name, d.specialty as doctor_specialty
                ORDER BY a.date, a.time
                """
                result = session.run(query, user_id=user_id, date_filter=date_filter)
            else:
                query = """
                MATCH (u:User {id: $user_id})-[:HAS_APPOINTMENT]->(a:Appointment)
                WHERE a.date >= date()
                OPTIONAL MATCH (a)-[:WITH_DOCTOR]->(d:Doctor)
                RETURN a, d.name as doctor_name, d.specialty as doctor_specialty
                ORDER BY a.date, a.time
                LIMIT 10
                """
                result = session.run(query, user_id=user_id)
            
            # Appointment ve doctor bilgisini birleştir
            appointments = []
            for record in result:
                apt = dict(record["a"])
                apt['doctor'] = record["doctor_name"]
                apt['specialty'] = record["doctor_specialty"]
                appointments.append(apt)
            
            return appointments
    
    # ==================== MEDICATION OPERATIONS ====================
    
    def create_medication(self, user_id: str, medication_data: Dict):
        """İlaç ekle"""
        with self.driver.session() as session:
            query = """
            MATCH (u:User {id: $user_id})
            CREATE (m:Medication {
                id: randomUUID(),
                name: $name,
                dosage: $dosage,
                frequency: $frequency,
                start_date: date($start_date),
                notes: $notes,
                created_at: datetime()
            })
            CREATE (u)-[:TAKES_MEDICATION]->(m)
            RETURN m
            """
            result = session.run(query,
                user_id=user_id,
                name=medication_data.get('name'),
                dosage=medication_data.get('dosage', ''),
                frequency=medication_data.get('frequency', 'daily'),
                start_date=medication_data.get('start_date', str(date.today())),
                notes=medication_data.get('notes', '')
            )
            return result.single()
    
    def get_user_medications(self, user_id: str):
        """Kullanıcının ilaçlarını getir"""
        with self.driver.session() as session:
            query = """
            MATCH (u:User {id: $user_id})-[:TAKES_MEDICATION]->(m:Medication)
            RETURN m
            ORDER BY m.name
            """
            result = session.run(query, user_id=user_id)
            return [dict(record["m"]) for record in result]
    
    # ==================== CONDITION OPERATIONS ====================
    
    def create_condition(self, user_id: str, condition_data: Dict):
        """Hastalık/durum ekle"""
        with self.driver.session() as session:
            query = """
            MATCH (u:User {id: $user_id})
            CREATE (c:Condition {
                id: randomUUID(),
                name: $name,
                diagnosed_date: date($diagnosed_date),
                severity: $severity,
                notes: $notes,
                created_at: datetime()
            })
            CREATE (u)-[:HAS_CONDITION]->(c)
            RETURN c
            """
            result = session.run(query,
                user_id=user_id,
                name=condition_data.get('name'),
                diagnosed_date=condition_data.get('diagnosed_date', str(date.today())),
                severity=condition_data.get('severity', 'moderate'),
                notes=condition_data.get('notes', '')
            )
            return result.single()
    
    def get_user_conditions(self, user_id: str):
        """Kullanıcının hastalıklarını getir"""
        with self.driver.session() as session:
            query = """
            MATCH (u:User {id: $user_id})-[:HAS_CONDITION]->(c:Condition)
            RETURN c
            ORDER BY c.name
            """
            result = session.run(query, user_id=user_id)
            return [dict(record["c"]) for record in result]
    
    # ==================== DOCTOR OPERATIONS ====================
    
    def create_doctor(self, doctor_data: Dict):
        """Doktor oluştur"""
        with self.driver.session() as session:
            query = """
            CREATE (d:Doctor {
                id: randomUUID(),
                name: $name,
                specialty: $specialty,
                hospital: $hospital,
                phone: $phone,
                created_at: datetime()
            })
            RETURN d
            """
            result = session.run(query,
                name=doctor_data.get('name'),
                specialty=doctor_data.get('specialty', ''),
                hospital=doctor_data.get('hospital', ''),
                phone=doctor_data.get('phone', '')
            )
            return result.single()
    
    def get_doctor_by_name(self, name: str):
        """İsme göre doktor bul"""
        with self.driver.session() as session:
            query = """
            MATCH (d:Doctor)
            WHERE d.name = $name
            RETURN d
            """
            result = session.run(query, name=name)
            record = result.single()
            return dict(record["d"]) if record else None
    
    # ==================== ENHANCED APPOINTMENT OPERATIONS ====================
    
    def create_appointment_with_doctor(self, user_id: str, doctor_name: str, appointment_data: Dict):
        """Doktor ile bağlantılı randevu oluştur"""
        with self.driver.session() as session:
            query = """
            MATCH (u:User {id: $user_id})
            MATCH (d:Doctor {name: $doctor_name})
            CREATE (a:Appointment {
                id: randomUUID(),
                date: date($date),
                time: $time,
                status: $status,
                location: $location,
                notes: $notes,
                created_at: datetime()
            })
            CREATE (u)-[:HAS_APPOINTMENT]->(a)
            CREATE (a)-[:WITH_DOCTOR]->(d)
            RETURN a, d
            """
            result = session.run(query,
                user_id=user_id,
                doctor_name=doctor_name,
                date=appointment_data.get('date'),
                time=appointment_data.get('time'),
                status=appointment_data.get('status', 'scheduled'),
                location=appointment_data.get('location', ''),
                notes=appointment_data.get('notes', '')
            )
            return result.single()
    
    # ==================== APPOINTMENT NOTES ====================
    
    def add_appointment_notes(self, appointment_id: str, notes_data: Dict):
        """Randevu notları ekle (doktor'dan gelen sonuç)"""
        with self.driver.session() as session:
            query = """
            MATCH (a:Appointment {id: $appointment_id})
            CREATE (n:AppointmentNote {
                id: randomUUID(),
                summary: $summary,
                diagnosis: $diagnosis,
                recommendations: $recommendations,
                follow_up: $follow_up,
                created_at: datetime()
            })
            CREATE (a)-[:HAS_NOTES]->(n)
            RETURN n
            """
            result = session.run(query,
                appointment_id=appointment_id,
                summary=notes_data.get('summary', ''),
                diagnosis=notes_data.get('diagnosis', ''),
                recommendations=notes_data.get('recommendations', ''),
                follow_up=notes_data.get('follow_up', '')
            )
            return result.single()
    
    # ==================== TEST RESULTS ====================
    
    def create_test_result(self, user_id: str, test_data: Dict, appointment_id: Optional[str] = None):
        """Test sonucu oluştur"""
        with self.driver.session() as session:
            if appointment_id:
                query = """
                MATCH (u:User {id: $user_id})
                MATCH (a:Appointment {id: $appointment_id})
                CREATE (t:TestResult {
                    id: randomUUID(),
                    test_name: $test_name,
                    test_date: date($test_date),
                    result: $result,
                    unit: $unit,
                    normal_range: $normal_range,
                    status: $status,
                    created_at: datetime()
                })
                CREATE (u)-[:HAS_TEST_RESULT]->(t)
                CREATE (a)-[:ORDERED_TEST]->(t)
                RETURN t
                """
            else:
                query = """
                MATCH (u:User {id: $user_id})
                CREATE (t:TestResult {
                    id: randomUUID(),
                    test_name: $test_name,
                    test_date: date($test_date),
                    result: $result,
                    unit: $unit,
                    normal_range: $normal_range,
                    status: $status,
                    created_at: datetime()
                })
                CREATE (u)-[:HAS_TEST_RESULT]->(t)
                RETURN t
                """
            
            result = session.run(query,
                user_id=user_id,
                appointment_id=appointment_id,
                test_name=test_data.get('test_name'),
                test_date=test_data.get('test_date'),
                result=test_data.get('result'),
                unit=test_data.get('unit', ''),
                normal_range=test_data.get('normal_range', ''),
                status=test_data.get('status', 'normal')
            )
            return result.single()
    
    def get_user_test_results(self, user_id: str):
        """Kullanıcının test sonuçlarını getir"""
        with self.driver.session() as session:
            query = """
            MATCH (u:User {id: $user_id})-[:HAS_TEST_RESULT]->(t:TestResult)
            RETURN t
            ORDER BY t.test_date DESC
            """
            result = session.run(query, user_id=user_id)
            return [dict(record["t"]) for record in result]
    
    # ==================== MEDICATION-CONDITION RELATIONSHIP ====================
    
    def link_medication_to_condition(self, user_id: str, medication_name: str, condition_name: str):
        """İlaç ile hastalığı ilişkilendir"""
        with self.driver.session() as session:
            query = """
            MATCH (u:User {id: $user_id})-[:TAKES_MEDICATION]->(m:Medication)
            MATCH (u)-[:HAS_CONDITION]->(c:Condition)
            WHERE m.name = $medication_name AND c.name = $condition_name
            CREATE (c)-[:TREATED_WITH]->(m)
            RETURN c, m
            """
            result = session.run(query,
                user_id=user_id,
                medication_name=medication_name,
                condition_name=condition_name
            )
            return result.single()
    
    # ==================== COMPLEX QUERIES ====================
    
    def get_user_complete_profile(self, user_id: str):
        """Kullanıcının tüm bilgilerini ilişkilerle getir"""
        with self.driver.session() as session:
            query = """
            MATCH (u:User {id: $user_id})
            OPTIONAL MATCH (u)-[:HAS_APPOINTMENT]->(a:Appointment)-[:WITH_DOCTOR]->(d:Doctor)
            OPTIONAL MATCH (a)-[:HAS_NOTES]->(n:AppointmentNote)
            OPTIONAL MATCH (u)-[:TAKES_MEDICATION]->(m:Medication)
            OPTIONAL MATCH (u)-[:HAS_CONDITION]->(c:Condition)
            OPTIONAL MATCH (c)-[:TREATED_WITH]->(m2:Medication)
            OPTIONAL MATCH (u)-[:HAS_TEST_RESULT]->(t:TestResult)
            RETURN u, 
                   collect(DISTINCT a) as appointments,
                   collect(DISTINCT d) as doctors,
                   collect(DISTINCT n) as notes,
                   collect(DISTINCT m) as medications,
                   collect(DISTINCT c) as conditions,
                   collect(DISTINCT t) as test_results
            """
            result = session.run(query, user_id=user_id)
            return result.single()
    
    # ==================== UTILITY ====================
    
    def clear_all_data(self):
        """Tüm veriyi sil (SADECE TEST İÇİN!)"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("⚠️ Tüm Neo4j verisi silindi")

