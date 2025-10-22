# 🏥 Personal Healthcare Assistant - Hybrid RAG + Knowledge Graph System

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🎯 Özellikler

### **🔬 Hybrid System - 3-Way Intent Classification**

| Mod | Veri Kaynağı | Teknoloji | Kullanım |
|-----|--------------|-----------|----------|
| 🔒 **Personal** | Neo4j Knowledge Graph | **Graph Query** | Sadece kişisel sağlık verileri (Cypher) |
| 🌐 **Generic** | FAISS + MedQuad Dataset | **RAG** | Sadece genel tıbbi bilgiler (Vector Search + LLM) |
| 🎯 **Hybrid** | Neo4j + FAISS | **Graph + RAG** | İKİSİNİ BİRLİKTE (Personalized Medical Advice) |

**🤖 LLM-Based Intent Classification:**
- Keyword matching yerine **GPT-4o-mini** ile akıllı classification
- 3-way classification: PERSONAL, GENERIC, HYBRID
- Fallback mechanism ile %100 uptime

**Bu bir Hybrid RAG sistemidir çünkü:**
- **Structured Data** (Graph): Neo4j ile Cypher sorguları
- **Unstructured Data** (RAG): FAISS vector search + GPT retrieval
- **Intent-Based Routing**: LLM ile otomatik yönlendirme
- **Hybrid Mode**: İkisini birlikte kullanma yeteneği

### **✨ Ana Özellikler:**

1. **🔍 Transparent Demo Interface**
   - Personal sorularda Neo4j'den çekilen tüm data görünür
   - RAG sorularda similarity scores ve kaynak dokümanlar
   - Execution trace ile tüm pipeline adımları izlenebilir
   - Jüri için mükemmel şeffaflık!

2. **Kişisel Sağlık Yönetimi**
   - 📅 Randevu takibi ve hatırlatmalar
   - 💊 İlaç yönetimi ve dozaj bilgileri
   - 🩺 Hastalık kayıtları ve seviye takibi
   - 🔬 Test sonuçları ve trend analizi
   - 👨‍⚕️ Doktor bilgileri ve notları
   - 📝 Randevu notları ve tavsiyeler

2. **Akıllı Intent Classification**
   - Otomatik personal/generic soru tespiti
   - Hybrid soruları anlayıp iki kaynaktan da bilgi getirir
   - Context-aware yanıt üretimi

3. **Görsel Zengin UI**
   - 🎨 Intent badges (Personal/Generic/Hybrid)
   - 📊 Similarity skorları (cosine similarity)
   - 🟢🟡🔴 Renk kodlu kaynak kalitesi
   - 📚 Detaylı kaynak gösterimi (soru + cevap)
   - 💬 Sidebar dashboard (personal data özeti)
   - 🔍 **Execution Trace** (hangi tool/fonksiyon çağrıldı, ne kadar sürdü)

4. **Gelişmiş RAG Pipeline**
   - Sentence Transformers embeddings
   - FAISS vector search (Cosine Similarity)
   - Dynamic threshold (personal sorular için esnek)
   - GPT-4o-mini (uygun maliyet)

---

## 📊 Dataset Information

### **MedQuad - Medical Question-Answer Dataset**

**📍 Kaynak:** [Kaggle - MedQuad Dataset](https://www.kaggle.com/datasets/pythonafroz/medquad-medical-question-answer-for-ai-research)

**📈 İstatistikler:**
- **16,461** question-answer pairs
- **47** medical topics and conditions
- Multiple authoritative sources:
  - NIH (National Institutes of Health)
  - Mayo Clinic
  - MPlusHealthTopics
  - CDC (Centers for Disease Control)
  - FDA (Food and Drug Administration)

**🎯 Kapsam:**
- Hastalıklar ve semptomlar
- Tedavi yöntemleri
- İlaç bilgileri
- Önleme stratejileri
- Teşhis prosedürleri

**💡 Kullanım:**
Bu dataset, generic health questions için bilgi kaynağı olarak kullanılıyor. FAISS vector store'da embedding'leri saklanıyor ve cosine similarity ile en alakalı dokümanlar bulunuyor.

---

## ⚡ Quick Start (Jüri için)

**5 dakikada çalıştır:**

```bash
# 0. MedQuad Dataset İndir (eğer yoksa)
# Kaggle'dan indir: https://www.kaggle.com/datasets/pythonafroz/medquad-medical-question-answer-for-ai-research
# medquad.csv dosyasını data/ klasörüne koy

# 1. Neo4j başlat (Docker)
docker run --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/12345678 neo4j:latest

# 2. Virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. Paketleri yükle
pip install --upgrade pip wheel
pip install -r requirements.txt

# 4. .env dosyası oluştur
# OPENAI_API_KEY=sk-proj-...
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=12345678

# 5. Vector index oluştur (ilk kez, 1-2 dakika)
python build_index.py

# 6. Demo data yükle (DİNAMİK TARİHLER!)
python setup_demo_data_enhanced.py

# 7. Uygulamayı başlat
streamlit run app_hybrid.py
```

**Test Soruları:**
```
🔒 Personal (Graph):  "Do I have any appointments today?"
🌐 Generic (RAG):     "What is high blood pressure?"
🎯 Hybrid (Graph+RAG): "Should I be concerned about my blood pressure given my hypertension?"
```

**⚙️ Ayarlar:**
- Sidebar'da "🔍 Show execution trace" seçeneğini aktif edin
- Hangi fonksiyonların çağrıldığını ve ne kadar sürdüğünü görün
- Performance analizi ve debug için idealdir!

---

## 🚀 Detaylı Kurulum

### 1️⃣ Neo4j Kurulumu

**Docker ile (Önerilen):**

**Windows (CMD):**
```cmd
docker run --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/12345678 neo4j:latest
```

**Windows (PowerShell):**
```powershell
docker run `
    --name neo4j `
    -p 7474:7474 -p 7687:7687 `
    -e NEO4J_AUTH=neo4j/12345678 `
    neo4j:latest
```

**Linux/Mac:**
```bash
docker run \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/12345678 \
    neo4j:latest
```

Neo4j Browser: http://localhost:7474

---

### 2️⃣ Python Environment

```bash
# Virtual environment oluştur
python -m venv venv

# Aktif et (Windows)
venv\Scripts\activate

# Aktif et (Linux/Mac)
source venv/bin/activate

# Paketleri yükle
pip install --upgrade pip wheel
pip install -r requirements.txt
```

---

### 3️⃣ Environment Variables

`.env` dosyasını oluştur:

```env
# OpenAI API Key
OPENAI_API_KEY=sk-proj-your_openai_api_key_here

# Neo4j Credentials
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=12345678
```

---

### 4️⃣ Vector Store Oluştur

```bash
# İlk kez çalıştırırken embeddings oluşturulacak (1-2 dakika)
python build_index.py
```

Bu adım:
- `medquad.csv` dataseti yükler (16,000+ QA pairs)
  - **Kaynak:** [MedQuad Dataset - Kaggle](https://www.kaggle.com/datasets/pythonafroz/medquad-medical-question-answer-for-ai-research)
- Sentence Transformers ile embeddings oluşturur
- FAISS index'i oluşturur ve kaydeder

---

### 5️⃣ Demo Verileri Yükle

```bash
# Enhanced demo data yükle (multi-layer graph)
python setup_demo_data_enhanced.py
```

Bu adım şunları oluşturur:
- 👤 Demo user (John Doe, 45 yaşında)
- 👨‍⚕️ 4 doktor (Dr. Sarah Johnson - Cardiology, Dr. Michael Chen - GP, vb.)
- 📅 5 randevu **(DİNAMİK TARİHLER!)**
  - 2 geçmiş randevu (90 gün önce, 60 gün önce)
  - 1 bugünkü randevu (script çalıştığı gün)
  - 2 gelecek randevu (7 gün sonra, 14 gün sonra)
- 📝 Randevu notları ve doktor tavsiyeleri
- 💊 4 ilaç (Lisinopril, Metformin, Aspirin, Atorvastatin)
- 🩺 3 hastalık (Hypertension, Type 2 Diabetes, Hyperlipidemia)
- 🔬 8 test sonucu (Blood Pressure, HbA1c, Cholesterol, Glucose)

**⚠️ ÖNEMLİ:** Tüm tarihler script çalıştırıldığında otomatik olarak o güne göre ayarlanır. Jüri ne zaman test ederse etsin, tarihler mantıklı olacak!

**Script Çıktısı Örneği:**
```
✓ Connected to Neo4j
✓ Neo4j schema oluşturuldu
✓ Created user: demo_user

📋 Creating Doctors...
  ✓ Dr. Sarah Johnson (Cardiology)
  ✓ Dr. Michael Chen (General Practice)
  ✓ Dr. Emily Rodriguez (Ophthalmology)
  ✓ Dr. James Wilson (Endocrinology)

📅 Creating Past Appointments...
  ✓ Past appointment: Dr. Chen (3 months ago) - Hypertension diagnosed
  ✓ Test results added: BP, Cholesterol
  ✓ Past appointment: Dr. Wilson (2 months ago) - Diabetes diagnosed
  ✓ Test results added: HbA1c, Glucose

📆 Creating Current/Future Appointments...
  ✓ Today: Dr. Sarah Johnson (Cardiology)
  ✓ Next week: Dr. Michael Chen (BP follow-up)
  ✓ In 2 weeks: Dr. Emily Rodriguez (Eye screening)

💊 Creating Medications...
  ✓ Lisinopril 10mg - Once daily (morning)
  ✓ Aspirin 81mg - Once daily (morning)
  ✓ Metformin 500mg - Twice daily (with meals)
  ✓ Atorvastatin 20mg - Once daily (evening)

🩺 Creating Health Conditions...
  ✓ Hypertension (High Blood Pressure) (Moderate)
  ✓ Type 2 Diabetes Mellitus (Mild)
  ✓ Hyperlipidemia (High Cholesterol) (Moderate)

🔗 Linking Medications to Conditions...
  ✓ Lisinopril → Hypertension (High Blood Pressure)
  ✓ Metformin → Type 2 Diabetes Mellitus
  ✓ Atorvastatin → Hyperlipidemia (High Cholesterol)

🧪 Adding Recent Test Results...
  ✓ Blood Pressure (Home Reading): 128/84 mmHg
  ✓ Fasting Blood Glucose (Home): 118 mg/dL

============================================================
✅ ENHANCED DEMO DATA SETUP COMPLETE!
============================================================

📊 Graph Statistics:
  • User: demo_user
  • Doctors: 4
  • Appointments: 5 (2 past, 1 today, 2 future)
  • Medications: 4
  • Conditions: 3

📅 Dynamic Dates (relative to today: 2024-10-22):
  • Past appointments: 2024-07-24 and 2024-08-23
  • Today's appointment: 2024-10-22
  • Future appointments: 2024-10-29 and 2024-11-05
  • Recent test results: 2024-10-21 and 2024-10-22
```

---

### 6️⃣ Uygulamayı Başlat

```bash
streamlit run app_hybrid.py
```

Uygulama: http://localhost:8501

---

## 🎮 Örnek Kullanımlar

### 🔒 **Personal Questions**

#### Randevular & Doktorlar
```
❓ "Do I have any appointments today?"
✅ "Yes! You have an appointment with Dr. Sarah Johnson at 2:00 PM 
    (Cardiology, City Medical Center, Room 305)."

❓ "What did Dr. Chen say in my last appointment?"
✅ "In your last appointment 3 months ago, Dr. Chen diagnosed hypertension 
    (BP: 145/92) and started you on Lisinopril. He recommended monitoring 
    blood pressure daily and reducing sodium intake."

❓ "Who is my cardiologist?"
✅ "Your cardiologist is Dr. Sarah Johnson from City Medical Center. 
    You have an appointment with her today at 2:00 PM."

❓ "When is my next appointment?"
✅ "Your next appointment is in 7 days with Dr. Michael Chen at 10:30 AM 
    at Community Health Clinic for blood pressure follow-up."
```

#### İlaçlar & Hastalıklar
```
❓ "What medications am I taking?"
✅ "You're currently taking:
    - Lisinopril 10mg (once daily, morning) for blood pressure
    - Metformin 500mg (twice daily with meals) for diabetes
    - Aspirin 81mg (once daily, morning) as blood thinner
    - Atorvastatin 20mg (once daily, evening) for cholesterol"

❓ "Which medication am I taking for diabetes?"
✅ "You're taking Metformin 500mg twice daily for Type 2 Diabetes. 
    You started this medication 2 months ago. Remember to take it with meals."

❓ "What health conditions do I have?"
✅ "Based on your records:
    - Hypertension (moderate severity, diagnosed 3 months ago)
    - Type 2 Diabetes Mellitus (mild, diagnosed 2 months ago)
    - Hyperlipidemia (moderate, diagnosed 3 months ago)"

❓ "Is my blood pressure controlled?"
✅ "Your blood pressure is improving. Initial reading was 145/92 (HIGH), 
    and your latest reading yesterday was 128/84 (BORDERLINE). 
    You're on the right track with Lisinopril!"
```

#### Test Sonuçları
```
❓ "What were my last blood pressure test results?"
✅ "Your most recent blood pressure reading (from yesterday) was 128/84 mmHg.
    Status: 🟡 BORDERLINE (Normal: <120/80)
    This shows improvement from your reading 3 months ago of 145/92."

❓ "Show me my recent test results"
✅ "Here are your recent test results:
    
    Blood Pressure (yesterday): 128/84 mmHg 🟡 Borderline
    Fasting Glucose (today): 118 mg/dL 🟡 Borderline
    HbA1c (2 months ago): 7.2% 🔴 High (Target: <5.7%)
    Total Cholesterol (3 months ago): 220 mg/dL 🔴 High (<200)"

❓ "How has my blood pressure changed over time?"
✅ "Your blood pressure has improved significantly:
    - 3 months ago (initial): 145/92 mmHg 🔴 HIGH
    - Yesterday (latest): 128/84 mmHg 🟡 BORDERLINE
    
    This shows a positive trend! Your Lisinopril medication is working.
    Keep up with your medication and lifestyle changes."
```

---

### 🌐 **Generic Questions**

```
❓ "What is high blood pressure?"
✅ [MedQuad knowledge base'den detaylı cevap + kaynaklar]

📚 Sources & Context Used:
  Document 1: 🟢 Similarity: 0.9234 (higher = better)
  - Source: NIHSeniorHealth
  - Focus Area: High Blood Pressure
  Q: What is high blood pressure?
  ───────────────────

❓ "What causes diabetes?"
✅ [MedQuad'dan cevap + similarity skorları]

❓ "What is Lisinopril used for?"
✅ [İlaç bilgileri + yan etkiler]
```

---

### 🎯 **Hybrid Questions** (En Güçlü Özellik!)

```
❓ "Should I be concerned about my blood pressure given my condition?"
✅ 🎯 Hybrid Question - Using your health records + medical knowledge

"Based on your health records and medical knowledge:

YOUR CURRENT STATUS:
• Diagnosis: Hypertension (moderate, diagnosed 3 months ago)
• Latest BP: 128/84 mmHg (yesterday) - 🟡 BORDERLINE
• Initial BP: 145/92 mmHg (3 months ago) - 🔴 HIGH
• Current medication: Lisinopril 10mg daily

GOOD NEWS:
Your blood pressure has improved significantly! The drop from 145/92 to 128/84 
shows that your medication is working well.

THINGS TO WATCH:
With your additional conditions (Type 2 Diabetes and Hyperlipidemia), managing 
blood pressure is crucial. Here's what you should do:

1. Continue Lisinopril as prescribed
2. Monitor BP regularly (target: <120/80 mmHg)
3. Follow low-sodium diet
4. Exercise 30 minutes daily
5. Keep today's appointment with Dr. Sarah Johnson at 2:00 PM

NEXT STEPS:
Discuss your progress with Dr. Johnson today. She may adjust your medication 
based on the positive trend."

ℹ️ Using relaxed similarity threshold for personal questions (min: 0.5)

📚 Sources & Context Used:
  Document 1: 🟡 Similarity: 0.6892 (higher = better)
  - Source: Mayo Clinic
  - Focus Area: Hypertension Management
  Q: How to manage high blood pressure with diabetes?
  
  Document 2: 🔴 Similarity: 0.5734 (higher = better)
  - Source: NIHSeniorHealth
  - Focus Area: Blood Pressure Control
  Q: What are healthy blood pressure levels?
```

**Other Hybrid Examples:**

```
❓ "What foods should I avoid with my current medications?"
✅ Combines: Your medications (Lisinopril, Metformin, Aspirin, Atorvastatin) 
    + General drug-food interaction knowledge

❓ "Is my diabetes under control based on my test results?"
✅ Combines: Your test results (HbA1c: 7.2%, Glucose: 118) 
    + Diabetes management guidelines

❓ "What should I ask my doctor at my appointment today?"
✅ Combines: Today's appointment with Dr. Johnson + Your recent test results 
    + Your conditions → Personalized questions to ask
```

---

## 📊 Sistem Mimarisi

```
┌─────────────────┐
│  User Question  │
└────────┬────────┘
         ↓
┌─────────────────────────┐
│ LLM Intent Classifier   │ ← GPT-4o-mini (10 tokens)
│  (3-way classification) │
└────────┬────────────────┘
         ↓
    ┌────┴─────┬────────┐
    ↓          ↓        ↓
PERSONAL   GENERIC   HYBRID
    ↓          ↓        ↓
┌───────┐ ┌──────┐ ┌──────────┐
│ Neo4j │ │FAISS │ │Neo4j+FAISS│
│ Graph │ │ RAG  │ │Graph+RAG │
└───┬───┘ └──┬───┘ └────┬─────┘
    │        │          │
    └────────┴──────────┘
             ↓
      ┌─────────────┐
      │ GPT-4o-mini │ ← Intent-based system prompt
      └──────┬──────┘
             ↓
      ┌─────────────┐
      │  Response   │
      └─────────────┘

🔒 Personal: Sadece Neo4j Graph (Cypher)
🌐 Generic:  Sadece FAISS RAG (Vector + LLM)
🎯 Hybrid:   Neo4j + FAISS (Graph + RAG birlikte)
```

---

## 🗂️ Enhanced Neo4j Schema

### **Nodes:**
```cypher
// User
(u:User {
    id: "user_123",
    name: "John Doe",
    age: 45,
    blood_type: "A+"
})

// Doctor
(d:Doctor {
    id: "doc_001",
    name: "Dr. Sarah Johnson",
    specialty: "Cardiology",
    phone: "+1-555-0100"
})

// Appointment
(a:Appointment {
    id: "apt_001",
    date: "2024-10-22",
    time: "14:00",
    location: "Room 305",
    status: "scheduled"
})

// AppointmentNote
(n:AppointmentNote {
    id: "note_001",
    note: "Patient BP improved...",
    recommendations: "Continue medication...",
    created_at: "2024-10-15T10:30:00"
})

// Medication
(m:Medication {
    id: "med_001",
    name: "Lisinopril",
    dosage: "10mg",
    frequency: "Once daily",
    start_date: "2022-03-20"
})

// Condition
(c:Condition {
    id: "cond_001",
    name: "Hypertension",
    diagnosed_date: "2022-03-15",
    severity: "moderate",
    status: "active"
})

// TestResult
(t:TestResult {
    id: "test_001",
    test_name: "Blood Pressure",
    test_date: "2024-10-21",
    result: "128/84",
    unit: "mmHg",
    normal_range: "<120/80",
    status: "borderline"
})
```

### **Relationships:**
```cypher
// User relationships
(u:User)-[:HAS_APPOINTMENT]->(a:Appointment)
(u:User)-[:TAKES_MEDICATION]->(m:Medication)
(u:User)-[:HAS_CONDITION]->(c:Condition)
(u:User)-[:HAS_TEST_RESULT]->(t:TestResult)

// Appointment relationships
(a:Appointment)-[:WITH_DOCTOR]->(d:Doctor)
(a:Appointment)-[:HAS_NOTE]->(n:AppointmentNote)
(a:Appointment)-[:RESULTED_IN]->(t:TestResult)

// Medication-Condition relationship
(m:Medication)-[:TREATS]->(c:Condition)
```

### **Örnek Graph Query:**
```cypher
// Kullanıcının tüm profilini getir
MATCH (u:User {id: 'user_123'})
OPTIONAL MATCH (u)-[:HAS_APPOINTMENT]->(a:Appointment)-[:WITH_DOCTOR]->(d:Doctor)
OPTIONAL MATCH (a)-[:HAS_NOTE]->(n:AppointmentNote)
OPTIONAL MATCH (u)-[:TAKES_MEDICATION]->(m:Medication)-[:TREATS]->(c:Condition)
OPTIONAL MATCH (u)-[:HAS_TEST_RESULT]->(t:TestResult)
RETURN u, a, d, n, m, c, t
```

---

## 📁 Proje Yapısı

```
AKBANKV4/
├── 📂 src/
│   ├── data_processor.py        # MedQuad dataset loader
│   ├── embeddings.py            # Sentence Transformers wrapper
│   ├── vector_store.py          # FAISS vector store (Cosine Similarity)
│   ├── chatbot.py               # GPT-4o-mini integration
│   ├── neo4j_client.py          # Neo4j CRUD operations
│   ├── intent_classifier.py     # Personal/Generic classifier
│   ├── date_tools.py             # Date/time utilities
│   └── hybrid_context.py        # Neo4j + FAISS orchestrator
│
├── 📂 data/
│   └── medquad.csv              # 16,000+ medical Q&A pairs
│                                 # Source: https://www.kaggle.com/datasets/pythonafroz/medquad-medical-question-answer-for-ai-research
│
├── app_hybrid.py                # ⭐ Main Streamlit app
├── build_index.py               # Embedding & FAISS index builder
├── setup_demo_data_enhanced.py # ⭐ Enhanced demo data loader
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (create this)
├── README_HYBRID.md             # ⭐ This file
│
└── 📂 Generated Files/
    ├── faiss_index.bin          # FAISS vector index
    └── documents.pkl            # Document metadata + similarity metric
```

---

## ⚙️ Yapılandırma

### **Similarity Threshold Logic**

| Intent | Sidebar Threshold | Effective Threshold | Davranış |
|--------|-------------------|---------------------|----------|
| **GENERIC** | 0.7 | 0.7 | Sadece yüksek kaliteli kaynaklar |
| **GENERIC** | 0.7 (hiç geçmeyen yok) | 0.7 | **Fallback**: Top k_docs döküman (warning ile) |
| **PERSONAL** | 0.7 | 0.5 (esnek) | Her zaman knowledge göster |
| **PERSONAL** | 0.3 | 0.3 | Çok düşük threshold bile çalışır |

**Fallback Davranışı (YENİ!):**
- Eğer hiç döküman threshold'u geçemezse, kullanıcının seçtiği sayı kadar döküman gösterilir (k_docs)
- Örnek: User "Knowledge documents: 5" seçmişse → 5 döküman gösterilir (threshold geçilmese bile)
- Kullanıcıya warning gösterilir: "No documents met threshold, showing top N results"
- GPT'ye kullanıcının istediği kadar context verilmiş olur
- Execution trace'de `fallback_used: true` ve `k_docs` değeri işaretlenir

**Avantajlar:**
- Generic sorularda kaliteli filtreleme
- Threshold geçilmese bile GPT'ye context verilir
- Personal sorularda her zaman context
- Hybrid sorular tam destekleniyor
- Şeffaflık: Kullanıcı hangi dökümanın kullanıldığını görür

---

## 🎨 UI Features

### **1. Intent Badges**
```
🔒 Personal Question - Using your health records
🌐 General Question - Using medical knowledge base
🎯 Hybrid Question - Using your health records + medical knowledge
```

### **2. Neo4j Data Transparency (PERSONAL/HYBRID)**
```
🔒 Personal Data from Neo4j Graph
Retrieved from Knowledge Graph:

👤 User: John Doe (Age: 45)

📅 Appointments (2 results)
- Today at 14:00
  - Doctor: Dr. Sarah Johnson
  - Specialty: Cardiology
- Next week at 10:30
  - Doctor: Dr. Michael Chen
  - Specialty: General Practice

💊 Medications (4 results)
- Lisinopril
  - Dosage: 10mg
  - Frequency: Once daily (morning)
- Metformin
  - Dosage: 500mg
  - Frequency: Twice daily (with meals)

🩺 Health Conditions (3 results)
- Hypertension (High Blood Pressure)
  - Severity: Moderate
- Type 2 Diabetes Mellitus
  - Severity: Mild

🧪 Test Results (4 results)
- Blood Pressure: 128/84 mmHg
  - Date: 2025-10-21
  - Status: ✅ Normal
- Fasting Blood Glucose: 118 mg/dL
  - Date: 2025-10-22
  - Status: ⚠️ Borderline

📊 Data retrieved from Neo4j Knowledge Graph using Cypher queries
```

### **3. RAG Similarity Scores (GENERIC/HYBRID)**
```
📚 Sources & Context Used

Document 1: 🟢 Similarity: 0.9234 (higher = better)
- Source: NIH
- Focus Area: Hypertension
Q: What is high blood pressure?
📄 View Full Answer

Document 2: 🟡 Similarity: 0.7845 (higher = better)
- Source: Mayo Clinic
- Focus Area: Cardiovascular
Q: How is hypertension diagnosed?

🟢 0.85+ → Excellent match
🟡 0.70-0.85 → Good match
🔴 <0.70 → Weak match
```

### **4. Sidebar Dashboard**
```
👤 Current User: John Doe (45)

📊 Quick Stats:
• 3 Active Conditions
• 3 Medications
• 1 Appointment Today
• 6 Test Results

📅 Upcoming Appointments:
→ Today 2:00 PM - Dr. Johnson (Cardiology)
→ Nov 15 3:00 PM - Dr. Chen (Endocrinology)
```

### **4. Source Display**
```
📚 Sources & Context Used ▼

  Document 1: 🟢 Similarity: 0.9234 (higher = better)
  - Source: NIHSeniorHealth
  - Focus Area: High Blood Pressure
  
  Q: What is high blood pressure?
  
  📄 View Full Answer ▼
    High blood pressure (hypertension) is a condition in which...
  ───────────────────
```

### **5. Execution Trace (NEW! 🔍)**
```
🔍 Execution Trace - Tools & Functions Called ▼

System Pipeline Execution:

┌─────────────────────────────────────────────────────────────┐
│ 1. Intent Classification                    | Duration: 2.45ms    🟢 │
│ IntentClassifier.classify()                                   │
│ Parameters: question: "Do I have..."                          │
│ Result: intent: PERSONAL                                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Neo4j Query (Personal Data)             | Duration: 8.32ms    🟢 │
│ Neo4jClient.get_user_*                                        │
│ Parameters: user_id: demo_user                                │
│ Result:                                                       │
│   • get_user_appointments() → 3 results                       │
│   • get_user_medications() → 4 results                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. FAISS Vector Search                      | Duration: 1.87ms    🟢 │
│ VectorStore.search()                                          │
│ Parameters: k: 3, similarity_metric: cosine                   │
│ Result: documents_found: 3, top_score: 0.8945                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Similarity Filtering                     | Duration: 0.12ms    🟢 │
│ filter_by_threshold()                                         │
│ Parameters:                                                   │
│   • threshold: 0.7                                            │
│   • original_count: 3                                         │
│   • k_docs: 3                                                 │
│   • fallback_used: false                                      │
│ Result:                                                       │
│   • filtered_count: 2                                         │
│   • note: Threshold met                                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Context Formatting                       | Duration: 0.34ms    🟢 │
│ HybridContextBuilder.format_for_gpt()                         │
│ Parameters: intent: PERSONAL                                  │
│ Result: context_length: 1245 chars                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. GPT-4o-mini API Call                     | Duration: 1823.56ms 🟡 │
│ HealthcareChatbot.generate_personalized_response()           │
│ Parameters:                                                   │
│   • model: gpt-4o-mini                                        │
│   • temperature: 0.7                                          │
│   • max_tokens: 800                                           │
│ Result: success: True, answer_length: 456 chars              │
└─────────────────────────────────────────────────────────────┘

────────────────────────────────────────────────────────────────
✅ TOTAL                                       | Total Time: 1836.66ms
Total Steps: 6
```

**Duration Color Codes:**
- 🟢 Green: < 100ms (Fast)
- 🟡 Yellow: 100-1000ms (Moderate)
- 🔴 Red: > 1000ms (Slow - usually GPT API)

**Fallback Scenario Example:**
```
User: "How is hypertension diagnosed?"
Threshold: 0.7
k_docs: 3 (sidebar setting)
Best Match Score: 0.65 (below threshold!)

┌─────────────────────────────────────────────────────────────┐
│ 4. Similarity Filtering                     | Duration: 0.15ms    🟢 │
│ filter_by_threshold()                                         │
│ Parameters:                                                   │
│   • threshold: 0.7                                            │
│   • original_count: 3                                         │
│   • k_docs: 3                                                 │
│   • fallback_used: true     ← FALLBACK ACTIVATED!            │
│ Result:                                                       │
│   • filtered_count: 3       ← User requested 3, showing all 3│
│   • note: Using top 3 docs (below threshold)                 │
└─────────────────────────────────────────────────────────────┘

⚠️ No documents met the similarity threshold (0.70). 
   Showing top 3 results anyway (best score: 0.6500)

📚 Sources & Context Used ▼
  Document 1: 🔴 Similarity: 0.6500 (higher = better)
  - Source: NIHSeniorHealth
  - Focus Area: Hypertension
  Q: What are the risk factors for high blood pressure?
  
  Document 2: 🔴 Similarity: 0.6200
  - Source: Mayo Clinic
  - Focus Area: Blood Pressure
  Q: How is blood pressure measured?
  
  Document 3: 🔴 Similarity: 0.5800
  - Source: CDC
  - Focus Area: Hypertension
  Q: What causes high blood pressure?
```
```

---

## 🐛 Troubleshooting

### **0. Tarihler Yanlış Görünüyor?**

**SORUN YOK!** Demo data script'i çalıştırdığınız güne göre otomatik tarihler üretiyor.

```bash
# Script'i bugün (22 Ekim 2024) çalıştırırsanız:
# - Bugünkü randevu: 2024-10-22
# - Gelecek randevu: 2024-10-29 (7 gün sonra)
# - Geçmiş randevu: 2024-07-24 (90 gün önce)

# Script'i 1 Kasım 2024'te çalıştırırsanız:
# - Bugünkü randevu: 2024-11-01
# - Gelecek randevu: 2024-11-08 (7 gün sonra)
# - Geçmiş randevu: 2024-08-03 (90 gün önce)
```

**Test etmek için:**
```
"Do I have any appointments today?"
→ Script çalıştığı günkü randevuyu gösterecek
```

---

### **1. Neo4j Bağlantı Hatası**
```bash
# Neo4j çalışıyor mu?
docker ps | grep neo4j

# Çalışmıyorsa başlat
docker start neo4j

# Logs kontrol et
docker logs neo4j

# Port conflict varsa
netstat -ano | findstr :7687
```

### **2. Embeddings Oluşturulmuyor**
```bash
# FAISS dosyalarını sil ve yeniden oluştur
del faiss_index.bin documents.pkl
python build_index.py
```

### **3. Similarity Skorları Yanlış**
```bash
# Metric mismatch varsa index'i yeniden oluştur
# vector_store.py şimdi otomatik algılıyor ama manuel de yapabilirsin
del faiss_index.bin documents.pkl
python build_index.py
```

### **4. Demo Data Yüklenmiyor**
```python
# Neo4j'yi temizle
from src.neo4j_client import Neo4jClient
import os
from dotenv import load_dotenv

load_dotenv()
client = Neo4jClient(
    os.getenv("NEO4J_URI"),
    os.getenv("NEO4J_USER"),
    os.getenv("NEO4J_PASSWORD")
)
client.clear_all_data()

# Tekrar yükle
python setup_demo_data_enhanced.py
```

### **5. Intent Yanlış Tespit Ediliyor**
```python
# src/intent_classifier.py içinde keyword'leri güncelle
self.personal_keywords.append("your_new_keyword")
```

---

## 🚀 İleri Seviye Özellikler

### **1. Custom User Ekleme**
```python
from src.neo4j_client import Neo4jClient

client = Neo4jClient(uri, user, password)

# Yeni user
user_id = client.create_user("Jane Smith", 38, "B+")

# Randevu ekle
apt_id = client.create_appointment(user_id, {
    'date': '2024-11-01',
    'time': '10:00',
    'doctor': 'Dr. Williams',
    'specialty': 'Dermatology',
    'location': 'Room 201'
})
```

### **2. Test Result Analizi**
```python
# app_hybrid.py içinde kullanıcının test trend'ini göster
test_results = neo4j_client.get_user_test_results(user_id)
# Pandas ile analiz yap, Streamlit'te grafik göster
```

### **3. Multi-User Support**
```python
# Sidebar'a user selector ekle
selected_user = st.selectbox("Select User", ["user_123", "user_456"])
context = hybrid_builder.build_context(selected_user, prompt)
```

---

## 📊 Performans & Maliyet

### **Vector Search:**
- FAISS: ~1-2ms per query (16,000 docs)
- Cosine Similarity: L2 normalization + Inner Product

### **GPT API:**
- Model: `gpt-4o-mini` (ucuz ve hızlı)
- Cost: ~$0.0001 per response
- Average tokens: 500-800

### **Neo4j:**
- Query time: <10ms (indexed)
- Memory: ~100MB (demo data)

---

## 🎯 Gelecek Geliştirmeler

### **Phase 2: Authentication**
- [ ] JWT-based user authentication
- [ ] Multi-user support
- [ ] Role-based access (Patient/Doctor/Admin)

### **Phase 3: Advanced Analytics**
- [ ] Health metrics visualization (charts)
- [ ] Predictive health alerts
- [ ] Drug interaction checking
- [ ] Multi-hop graph reasoning

### **Phase 4: Production Features**
- [ ] HTTPS + SSL encryption
- [ ] Data backup & recovery
- [ ] Audit logs
- [ ] HIPAA compliance

---

## 🏆 Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python 3.8+ |
| **Frontend** | Streamlit |
| **LLM** | OpenAI GPT-4o-mini |
| **Embeddings** | Sentence Transformers (all-MiniLM-L6-v2) |
| **Vector DB** | FAISS (Cosine Similarity) |
| **Graph DB** | Neo4j |
| **Dataset** | MedQuad (16,000+ QA pairs) - [Kaggle](https://www.kaggle.com/datasets/pythonafroz/medquad-medical-question-answer-for-ai-research) |

---

## 📜 License

MIT License - Feel free to use for educational/commercial purposes

---

## 🙏 Credits

- **MedQuad Dataset**: 
  - Original Sources: NIH, Mayo Clinic, MPlusHealthTopics
  - Kaggle Dataset: [pythonafroz/medquad-medical-qa](https://www.kaggle.com/datasets/pythonafroz/medquad-medical-question-answer-for-ai-research)
  - 16,461 medical question-answer pairs
- **Sentence Transformers**: Hugging Face
- **FAISS**: Facebook AI Research
- **Neo4j**: Neo4j Inc.
- **OpenAI**: GPT-4o-mini API

---

## 📞 Support

Sorun yaşarsanız:
1. ✅ `.env` dosyasını kontrol edin
2. ✅ Neo4j çalışıyor mu kontrol edin
3. ✅ Python paketleri güncel mi kontrol edin
4. ✅ Troubleshooting bölümüne bakın

---

**Enjoy your Personal Healthcare Assistant! 🚀**

_Last Updated: October 22, 2024_
