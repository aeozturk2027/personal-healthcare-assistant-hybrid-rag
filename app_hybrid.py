"""
Healthcare Chatbot - Hybrid System (Neo4j + FAISS)
Personalized healthcare assistant with user health records

Dataset: MedQuad (16,461 medical Q&A pairs)
Source: https://www.kaggle.com/datasets/pythonafroz/medquad-medical-question-answer-for-ai-research
"""
import streamlit as st
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from src.data_processor import DataProcessor
from src.embeddings import EmbeddingModel
from src.vector_store import VectorStore
from src.chatbot import HealthcareChatbot
from src.neo4j_client import Neo4jClient
from src.hybrid_context import HybridContextBuilder
from src.date_tools import DateTools

# Sayfa yapılandırması
st.set_page_config(
    page_title="Personal Healthcare Assistant",
    page_icon="🏥",
    layout="wide"
)

# .env dosyasını yükle
load_dotenv()

@st.cache_resource
def initialize_system():
    """Sistemi başlatır (tek sefer çalışır)"""
    
    # API key kontrolü
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        st.error("⚠️ .env dosyasında OPENAI_API_KEY tanımlı değil!")
        st.stop()
    
    # Neo4j connection
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    
    if not neo4j_password:
        st.error("⚠️ .env dosyasında NEO4J_PASSWORD tanımlı değil!")
        st.stop()
    
    try:
        neo4j_client = Neo4jClient(neo4j_uri, neo4j_user, neo4j_password)
        if not neo4j_client.verify_connection():
            st.error("❌ Neo4j bağlantısı kurulamadı!")
            st.stop()
        # Schema oluştur
        neo4j_client.create_schema()
    except Exception as e:
        st.error(f"❌ Neo4j hatası: {e}")
        st.stop()
    
    # Data processor
    data_processor = DataProcessor()
    documents = data_processor.prepare_documents()
    
    # Embedding model
    embedding_model = EmbeddingModel()
    
    # Vector store
    vector_store = VectorStore(dimension=embedding_model.get_dimension())
    
    # Kaydedilmiş index var mı kontrol et
    if not vector_store.load():
        st.info("First time setup: Creating embeddings... (This may take a few minutes)")
        
        # Tüm dokümanlar için embedding oluştur
        texts = [doc['text'] for doc in documents]
        embeddings = embedding_model.encode(texts)
        
        # Vector store'a ekle ve kaydet
        vector_store.add_documents(embeddings, documents)
        vector_store.save()
        
        st.success("✓ Embeddings created and saved!")
    
    # Chatbot (gpt-4o-mini: ucuz ve hızlı)
    chatbot = HealthcareChatbot(api_key, model="gpt-4o-mini")
    
    # Hybrid context builder
    hybrid_builder = HybridContextBuilder(neo4j_client, vector_store, embedding_model)
    
    return neo4j_client, hybrid_builder, chatbot, DateTools()

# Sistem başlatma
neo4j_client, hybrid_builder, chatbot, date_tools = initialize_system()

# Hardcoded user ID (auth olmadan)
USER_ID = "demo_user"

# Demo user'ı oluştur (eğer yoksa)
if not neo4j_client.get_user(USER_ID):
    neo4j_client.create_user(USER_ID, "Demo User", age=35)
    st.success("✓ Demo user created!")

# Ana sayfa
st.title("🏥 Personal Healthcare Assistant")
st.markdown("Your intelligent health companion with personalized insights")

# Sidebar - User Dashboard
with st.sidebar:
    st.markdown(f"### 👤 {USER_ID.replace('_', ' ').title()}")
    
    current_date = date_tools.get_current_date()
    st.caption(f"📅 {date_tools.format_date_friendly(current_date)}")
    
    st.divider()
    
    # Today's appointments ONLY (kompakt)
    today_appointments = neo4j_client.get_user_appointments(USER_ID, current_date)
    
    if today_appointments:
        st.markdown(f"**📅 Today ({len(today_appointments)} appt)**")
        for apt in today_appointments:
            doctor_name = apt.get('doctor') or 'TBD'
            apt_time = apt.get('time', 'TBD')
            specialty = apt.get('specialty', '')
            
            # Kompakt görünüm
            if specialty:
                st.text(f"🏥 {apt_time} - {doctor_name}")
                st.caption(f"   {specialty}")
            else:
                st.text(f"🏥 {apt_time} - {doctor_name}")
    else:
        st.markdown("**📅 Today**")
        st.caption("✓ No appointments")
    
    st.divider()
    
    # Quick Stats (compact)
    st.markdown("**📊 Quick Stats**")
    
    # Get data
    medications = neo4j_client.get_user_medications(USER_ID)
    conditions = neo4j_client.get_user_conditions(USER_ID)
    upcoming = neo4j_client.get_user_appointments(USER_ID)
    
    # Count upcoming (gelecekteki randevular)
    upcoming_count = 0
    if upcoming:
        for apt in upcoming:
            apt_date = str(apt.get('date', ''))
            if apt_date > current_date:
                upcoming_count += 1
    
    # Display metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💊 Medications", len(medications) if medications else 0)
    with col2:
        st.metric("🩺 Conditions", len(conditions) if conditions else 0)
    
    st.metric("📅 Upcoming Appts", upcoming_count)
    
    # Expandable details
    with st.expander("💊 View Medications"):
        if medications:
            for med in medications:
                st.markdown(f"**{med['name']}**")
                if med.get('dosage') and med.get('frequency'):
                    st.caption(f"{med['dosage']} - {med['frequency']}")
        else:
            st.caption("No medications")
    
    with st.expander("🩺 View Conditions"):
        if conditions:
            for cond in conditions:
                st.text(f"• {cond['name']}")
        else:
            st.caption("No conditions")
    
    with st.expander("📆 View Upcoming Appointments"):
        if upcoming_count > 0:
            shown = 0
            for apt in upcoming:
                if str(apt.get('date', '')) > current_date and shown < 3:
                    date_friendly = date_tools.format_date_friendly(str(apt['date']))
                    doctor = apt.get('doctor', 'Unknown')
                    apt_time = apt.get('time', 'TBD')
                    st.text(f"• {date_friendly} at {apt_time}")
                    st.caption(f"  {doctor}")
                    shown += 1
        else:
            st.caption("No upcoming appointments")
    
    st.divider()
    
    # Settings
    st.markdown("**⚙️ Settings**")
    k_docs = st.slider("Knowledge documents", min_value=1, max_value=10, value=3, help="Number of documents to retrieve")
    
    similarity_threshold = st.slider(
        "Similarity Threshold", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.7, 
        step=0.05,
        help="Minimum similarity score (0.0-1.0)"
    )
    
    show_context = st.checkbox("Show context details", value=False)
    show_trace = st.checkbox("🔍 Show execution trace", value=False, help="See which tools/functions are called")

# Main content - Chat
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### 💬 Ask me anything!")
    st.caption("I can answer both general health questions and questions about your personal health records.")

with col2:
    if st.button("🔄 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Example questions
with st.expander("💡 Example Questions - Try These!"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔒 Personal Questions:**")
        st.markdown("""
        **Appointments & Doctors:**
        - "Do I have any appointments today?"
        - "When is my next appointment?"
        - "Who is my cardiologist?"
        - "What did Dr. Chen say in my last appointment?"
        
        **Medications & Conditions:**
        - "What medications am I taking?"
        - "Which medication am I taking for diabetes?"
        - "What health conditions do I have?"
        - "Is my blood pressure controlled?"
        
        **Test Results:**
        - "What were my last blood pressure test results?"
        - "Show me my recent test results"
        - "What was my HbA1c level?"
        - "How has my blood pressure changed over time?"
        """)
    
    with col2:
        st.markdown("**🌐 General Questions:**")
        st.markdown("""
        **Diseases & Conditions:**
        - "What is high blood pressure?"
        - "What causes diabetes?"
        - "What are the symptoms of glaucoma?"
        - "How is hypertension diagnosed?"
        
        **Treatment & Prevention:**
        - "How can I prevent diabetes?"
        - "What are the treatments for high blood pressure?"
        - "What lifestyle changes help with hypertension?"
        - "What foods should I avoid for diabetes?"
        
        **Medications:**
        - "What is Lisinopril used for?"
        - "What are the side effects of Metformin?"
        - "How does Aspirin help with heart health?"
        """)
    
    st.divider()
    st.markdown("**🎯 Hybrid Questions (Personal + General):**")
    st.markdown("""
    - "Should I be concerned about my blood pressure given my condition?"
    - "What foods should I avoid with my current medications?"
    - "Is my diabetes under control based on my test results?"
    - "What should I ask my doctor at my appointment today?"
    """)

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show intent badge for assistant messages
        if message["role"] == "assistant" and message.get("intent"):
            if message["intent"] == "PERSONAL":
                st.caption("🔒 Personal Question")
            else:
                st.caption("🌐 General Question")
        
        # Show sources if available
        if message["role"] == "assistant" and message.get("sources"):
            with st.expander("📚 Sources & Context Used"):
                for i, doc in enumerate(message["sources"], 1):
                    # Header with similarity score
                    if doc.get('similarity_score'):
                        score = doc['similarity_score']
                        color = "🟢" if score > 0.85 else "🟡" if score > 0.7 else "🔴"
                        st.markdown(f"**Document {i}:** {color} Similarity: **{score:.4f}**")
                    else:
                        st.markdown(f"**Document {i}:**")
                    
                    st.markdown(f"- **Source:** {doc.get('source', 'N/A')}")
                    st.markdown(f"- **Focus Area:** {doc.get('focus_area', 'N/A')}")
                    st.markdown(f"**Q:** _{doc.get('question', 'N/A')}_")
                    
                    if show_context:
                        with st.expander("📄 View Full Answer"):
                            st.text(doc.get('answer', 'N/A'))
                    
                    st.divider()
        
        # Show execution trace if available
        if message["role"] == "assistant" and message.get("execution_trace") and show_trace:
            with st.expander("🔍 Execution Trace - Tools & Functions Called"):
                st.markdown("**System Pipeline Execution:**")
                
                for i, trace_step in enumerate(message["execution_trace"][:-1], 1):
                    with st.container():
                        cols = st.columns([3, 2, 1])
                        
                        with cols[0]:
                            st.markdown(f"**{trace_step['step']}**")
                            st.code(trace_step['function'], language="python")
                        
                        with cols[1]:
                            st.caption("**Parameters:**")
                            for key, val in trace_step['parameters'].items():
                                if isinstance(val, str) and len(val) > 50:
                                    st.caption(f"• {key}: {val[:50]}...")
                                else:
                                    st.caption(f"• {key}: {val}")
                            
                            st.caption("**Result:**")
                            for key, val in trace_step['result'].items():
                                if isinstance(val, list):
                                    for item in val:
                                        st.caption(f"• {item}")
                                else:
                                    st.caption(f"• {key}: {val}")
                        
                        with cols[2]:
                            duration_ms = float(trace_step['duration'].replace('ms', ''))
                            if duration_ms > 1000:
                                color = "🔴"
                            elif duration_ms > 100:
                                color = "🟡"
                            else:
                                color = "🟢"
                            st.metric("Duration", trace_step['duration'], delta=None)
                            st.caption(f"{color}")
                        
                        if i < len(message["execution_trace"]) - 1:
                            st.markdown("↓")
                
                # Show total
                st.divider()
                total_trace = message["execution_trace"][-1]
                cols = st.columns([2, 1, 1])
                with cols[0]:
                    st.markdown(f"**{total_trace['step']}**")
                with cols[1]:
                    st.markdown(f"**Total Steps:** {total_trace['result']['steps'] - 1}")
                with cols[2]:
                    st.metric("Total Time", total_trace['duration'], delta=None)

# User input
if prompt := st.chat_input("Ask your health question..."):
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            
            # Initialize execution trace
            execution_trace = []
            total_start = time.perf_counter()
            
            # Step 1: Build hybrid context
            step_start = time.perf_counter()
            context = hybrid_builder.build_context(USER_ID, prompt, k_docs=k_docs)
            step_time = time.perf_counter() - step_start
            
            # Show required data if personal/hybrid
            result_data = {'intent': context['intent']}
            if context['intent'] in ["PERSONAL", "HYBRID"]:
                required = context.get('required_data', {})
                needed = [k for k, v in required.items() if v]
                if needed:
                    result_data['required_data'] = needed
            
            execution_trace.append({
                'step': '1. LLM Intent Classification',
                'function': 'IntentClassifier.classify_with_data()',
                'parameters': {'question': prompt},
                'result': result_data,
                'duration': f"{step_time*1000:.2f}ms"
            })
            
            # Step 2: Personal Data Retrieval (if personal or hybrid)
            if context['intent'] in ["PERSONAL", "HYBRID"]:
                step_start = time.perf_counter()
                personal_data = context.get('personal_data', {})
                step_time = time.perf_counter() - step_start
                
                queries_made = []
                if personal_data.get('appointments'):
                    queries_made.append(f"get_user_appointments() → {len(personal_data['appointments'])} results")
                if personal_data.get('medications'):
                    queries_made.append(f"get_user_medications() → {len(personal_data['medications'])} results")
                if personal_data.get('conditions'):
                    queries_made.append(f"get_user_conditions() → {len(personal_data['conditions'])} results")
                if personal_data.get('test_results'):
                    queries_made.append(f"get_user_test_results() → {len(personal_data['test_results'])} results")
                
                execution_trace.append({
                    'step': '2. Neo4j Query (Personal Data)',
                    'function': 'Neo4jClient.get_user_*',
                    'parameters': {'user_id': USER_ID},
                    'result': {'queries': queries_made if queries_made else ['No personal data fetched']},
                    'duration': f"{step_time*1000:.2f}ms"
                })
            
            # Step 3: Vector Search (generic ve hybrid sorular için)
            if context['intent'] in ["GENERIC", "HYBRID"]:
                step_start = time.perf_counter()
                knowledge_count = len(context.get('knowledge', []))
                step_time = time.perf_counter() - step_start
                
                # Hybrid için enriched query göster
                params = {'k': k_docs, 'similarity_metric': 'cosine'}
                if context['intent'] == "HYBRID" and context.get('enriched_query'):
                    enriched = context['enriched_query']
                    if enriched != prompt:
                        params['enriched_query'] = enriched[:100] + "..." if len(enriched) > 100 else enriched
                
                execution_trace.append({
                    'step': '3. FAISS Vector Search (RAG)',
                    'function': 'VectorStore.search()',
                    'parameters': params,
                    'result': {
                        'documents_found': knowledge_count,
                        'top_score': f"{context['knowledge'][0].get('similarity_score', 0):.4f}" if context['knowledge'] else 'N/A'
                    },
                    'duration': f"{step_time*1000:.2f}ms"
                })
            else:
                knowledge_count = 0
            
            # Filter by similarity threshold (generic ve hybrid sorular için)
            if context['intent'] in ["GENERIC", "HYBRID"]:
                step_start = time.perf_counter()
                effective_threshold = similarity_threshold
                filtered_knowledge = [
                    doc for doc in context['knowledge'] 
                    if doc.get('similarity_score', 0) >= similarity_threshold
                ]
                
                # Fallback: Eğer hiç geçmeyen yoksa kullanıcının istediği kadar göster
                if not filtered_knowledge and context['knowledge']:
                    filtered_knowledge = context['knowledge'][:k_docs]
                
                context['knowledge'] = filtered_knowledge
                step_time = time.perf_counter() - step_start
                
                # Determine if fallback was used
                fallback_used = False
                if filtered_knowledge and knowledge_count > 0:
                    if filtered_knowledge[0].get('similarity_score', 0) < similarity_threshold:
                        fallback_used = True
                
                execution_trace.append({
                    'step': '4. Similarity Filtering (RAG)',
                    'function': 'filter_by_threshold()',
                    'parameters': {
                        'threshold': effective_threshold, 
                        'original_count': knowledge_count,
                        'k_docs': k_docs,
                        'fallback_used': fallback_used
                    },
                    'result': {
                        'filtered_count': len(filtered_knowledge),
                        'note': f'Using top {len(filtered_knowledge)} docs (below threshold)' if fallback_used else 'Threshold met'
                    },
                    'duration': f"{step_time*1000:.2f}ms"
                })
            else:
                # Personal: RAG yok
                filtered_knowledge = []
            
            # Format context for GPT
            step_start = time.perf_counter()
            formatted_context = hybrid_builder.format_for_gpt(context)
            step_time = time.perf_counter() - step_start
            
            context_type = "Graph Data" if context['intent'] == "PERSONAL" else "RAG Context"
            execution_trace.append({
                'step': f'5. Context Formatting ({context_type})',
                'function': 'HybridContextBuilder.format_for_gpt()',
                'parameters': {'intent': context['intent']},
                'result': {'context_length': f"{len(formatted_context)} chars"},
                'duration': f"{step_time*1000:.2f}ms"
            })
            
            # Generate response
            step_start = time.perf_counter()
            response = chatbot.generate_personalized_response(
                prompt, 
                formatted_context,
                intent=context['intent']
            )
            step_time = time.perf_counter() - step_start
            
            execution_trace.append({
                'step': '6. GPT-4o-mini API Call',
                'function': 'HealthcareChatbot.generate_personalized_response()',
                'parameters': {
                    'model': 'gpt-4o-mini',
                    'temperature': 0.7,
                    'max_tokens': 800
                },
                'result': {
                    'success': response.get('success', False),
                    'answer_length': f"{len(response.get('answer', ''))} chars"
                },
                'duration': f"{step_time*1000:.2f}ms"
            })
            
            total_time = time.perf_counter() - total_start
            execution_trace.append({
                'step': '✅ TOTAL',
                'function': 'Complete Pipeline',
                'parameters': {},
                'result': {'steps': len(execution_trace)},
                'duration': f"{total_time*1000:.2f}ms"
            })
            
            # Show intent badge
            if context['intent'] == "PERSONAL":
                st.info("🔒 **Personal Question** - Using your health records (Neo4j Graph)", icon="🔒")
            elif context['intent'] == "GENERIC":
                st.info("🌐 **General Question** - Using medical knowledge (FAISS RAG)", icon="📚")
            elif context['intent'] == "HYBRID":
                st.info("🎯 **Hybrid Question** - Combining your health records + medical knowledge", icon="🔬")
            
            # Show answer
            st.markdown(response["answer"])
            
            # Show Personal Data from Neo4j (for PERSONAL and HYBRID)
            if context['intent'] in ["PERSONAL", "HYBRID"]:
                personal_data = context.get('personal_data', {})
                has_personal = any([
                    personal_data.get('appointments'),
                    personal_data.get('medications'),
                    personal_data.get('conditions'),
                    personal_data.get('test_results')
                ])
                
                if has_personal:
                    with st.expander("🔒 Personal Data from Neo4j Graph"):
                        st.markdown("**Retrieved from Knowledge Graph:**")
                        
                        # User info
                        if personal_data.get('user'):
                            user = personal_data['user']
                            st.markdown(f"**👤 User:** {user.get('name', 'N/A')} (Age: {user.get('age', 'N/A')})")
                            st.divider()
                        
                        # Appointments
                        if personal_data.get('appointments'):
                            st.markdown(f"**📅 Appointments ({len(personal_data['appointments'])} results)**")
                            for apt in personal_data['appointments']:
                                date_friendly = date_tools.format_date_friendly(str(apt['date']))
                                st.markdown(f"- **{date_friendly}** at {apt.get('time', 'N/A')}")
                                if apt.get('doctor'):
                                    st.markdown(f"  - Doctor: {apt['doctor']}")
                                if apt.get('specialty'):
                                    st.markdown(f"  - Specialty: {apt['specialty']}")
                                if apt.get('location'):
                                    st.markdown(f"  - Location: {apt['location']}")
                            st.divider()
                        
                        # Medications
                        if personal_data.get('medications'):
                            st.markdown(f"**💊 Medications ({len(personal_data['medications'])} results)**")
                            for med in personal_data['medications']:
                                st.markdown(f"- **{med['name']}**")
                                if med.get('dosage'):
                                    st.markdown(f"  - Dosage: {med['dosage']}")
                                if med.get('frequency'):
                                    st.markdown(f"  - Frequency: {med['frequency']}")
                            st.divider()
                        
                        # Conditions
                        if personal_data.get('conditions'):
                            st.markdown(f"**🩺 Health Conditions ({len(personal_data['conditions'])} results)**")
                            for cond in personal_data['conditions']:
                                st.markdown(f"- **{cond['name']}**")
                                if cond.get('severity'):
                                    st.markdown(f"  - Severity: {cond['severity']}")
                                if cond.get('diagnosed_date'):
                                    st.markdown(f"  - Diagnosed: {cond['diagnosed_date']}")
                            st.divider()
                        
                        # Test Results
                        if personal_data.get('test_results'):
                            st.markdown(f"**🧪 Test Results ({len(personal_data['test_results'])} results)**")
                            for test in personal_data['test_results']:
                                st.markdown(f"- **{test.get('test_name', 'N/A')}**: {test.get('value', 'N/A')} {test.get('unit', '')}")
                                if test.get('date'):
                                    st.markdown(f"  - Date: {test['date']}")
                                if test.get('status'):
                                    status_emoji = "✅" if test['status'] == 'Normal' else "⚠️"
                                    st.markdown(f"  - Status: {status_emoji} {test['status']}")
                        
                        st.caption("📊 Data retrieved from Neo4j Knowledge Graph using Cypher queries")
            
            # Show info if using fallback document (for generic/hybrid)
            if context['intent'] in ["GENERIC", "HYBRID"] and filtered_knowledge:
                # Check if we're using the fallback (score below threshold)
                if filtered_knowledge[0].get('similarity_score', 0) < similarity_threshold:
                    best_score = filtered_knowledge[0].get('similarity_score', 0)
                    st.warning(f"⚠️ No documents met the similarity threshold ({similarity_threshold:.2f}). Showing top {len(filtered_knowledge)} results anyway (best score: {best_score:.4f})")
            
            # Show sources (Generic ve Hybrid sorular için)
            if context['intent'] in ["GENERIC", "HYBRID"] and filtered_knowledge:
                with st.expander("📚 Sources & Context Used"):
                    for i, doc in enumerate(filtered_knowledge, 1):
                        # Header with similarity score
                        if doc.get('similarity_score'):
                            score = doc['similarity_score']
                            color = "🟢" if score > 0.85 else "🟡" if score > 0.7 else "🔴"
                            st.markdown(f"**Document {i}:** {color} Similarity: **{score:.4f}** (higher = better)")
                        else:
                            st.markdown(f"**Document {i}:**")
                        
                        st.markdown(f"- **Source:** {doc.get('source', 'N/A')}")
                        st.markdown(f"- **Focus Area:** {doc.get('focus_area', 'N/A')}")
                        
                        # Question and Answer
                        with st.container():
                            st.markdown(f"**Q:** _{doc.get('question', 'N/A')}_")
                            with st.expander("📄 View Full Answer"):
                                st.text(doc.get('answer', 'N/A'))
                        
                        st.divider()
            
            # Show execution trace (if enabled)
            if show_trace:
                with st.expander("🔍 Execution Trace - Tools & Functions Called"):
                    st.markdown("**System Pipeline Execution:**")
                    
                    for i, trace_step in enumerate(execution_trace[:-1], 1):  # Skip TOTAL for now
                        with st.container():
                            cols = st.columns([3, 2, 1])
                            
                            with cols[0]:
                                st.markdown(f"**{trace_step['step']}**")
                                st.code(trace_step['function'], language="python")
                            
                            with cols[1]:
                                st.caption("**Parameters:**")
                                for key, val in trace_step['parameters'].items():
                                    if isinstance(val, str) and len(val) > 50:
                                        st.caption(f"• {key}: {val[:50]}...")
                                    else:
                                        st.caption(f"• {key}: {val}")
                                
                                st.caption("**Result:**")
                                for key, val in trace_step['result'].items():
                                    if isinstance(val, list):
                                        for item in val:
                                            st.caption(f"• {item}")
                                    else:
                                        st.caption(f"• {key}: {val}")
                            
                            with cols[2]:
                                # Color code by duration
                                duration_ms = float(trace_step['duration'].replace('ms', ''))
                                if duration_ms > 1000:
                                    color = "🔴"
                                elif duration_ms > 100:
                                    color = "🟡"
                                else:
                                    color = "🟢"
                                st.metric("Duration", trace_step['duration'], delta=None)
                                st.caption(f"{color}")
                            
                            if i < len(execution_trace) - 1:
                                st.markdown("↓")
                    
                    # Show total at the end
                    st.divider()
                    total_trace = execution_trace[-1]
                    cols = st.columns([2, 1, 1])
                    with cols[0]:
                        st.markdown(f"**{total_trace['step']}**")
                    with cols[1]:
                        st.markdown(f"**Total Steps:** {total_trace['result']['steps'] - 1}")
                    with cols[2]:
                        st.metric("Total Time", total_trace['duration'], delta=None)
            
            # Save to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["answer"],
                "intent": context['intent'],
                "sources": filtered_knowledge,
                "context_data": {
                    "intent": context['intent'],
                    "personal_data_count": len(str(context.get('personal_data', {}))),
                    "knowledge_docs": len(filtered_knowledge)
                },
                "execution_trace": execution_trace if show_trace else None
            })

# Footer
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.caption("⚠️ This chatbot is for informational purposes only. Always consult your healthcare provider.")
with col2:
    st.caption("🔒 Your data is stored securely in Neo4j")

