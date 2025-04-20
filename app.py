import streamlit as st
import os
import sqlite3
import json
from pdf_extractor import extract_pdf_content
from llm_handler import get_rag_response

# Custom CSS for styling
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; padding: 20px; }
    .stButton>button { background-color: #4CAF50; color: white; border-radius: 5px; }
    .stTextInput>div>input { border-radius: 5px; }
    .sidebar .sidebar-content { background-color: #ffffff; }
    .st-expander { background-color: #ffffff; border-radius: 5px; }
    h1, h2, h3 { color: #2c3e50; }
    .success-box { background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; }
    .warning-box { background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; }
    .error-box { background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if "history" not in st.session_state:
    st.session_state.history = []
if "db_path" not in st.session_state:
    st.session_state.db_path = "extracted_data.db"

# Navigation bar
st.sidebar.title("📚 PDF Chatbot Navigation")
page = st.sidebar.radio("Go to", ["Chatbot", "Data", "History"], index=0)

# Chatbot Page
if page == "Chatbot":
    st.header("🤖 PDF Chatbot")
    st.write("Upload a PDF or enter a file path, then ask questions about its content.")

    # PDF input
    with st.container():
        st.subheader("📄 Upload or Specify PDF")
        pdf_option = st.radio("Choose PDF input method:", ("Upload PDF", "Enter PDF Path"), key="pdf_option")
        pdf_path = None

        if pdf_option == "Upload PDF":
            uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"], key="pdf_upload")
            if uploaded_file:
                pdf_path = "temp.pdf"
                with open(pdf_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
        else:
            pdf_path = st.text_input("Enter PDF file path", value=r"E:/murahari/Task/pdf_chatbot/n2xy-iec-60502-1-xlpe-pvc-0-6-1kv-cable.pdf", key="pdf_path")

        if pdf_path and st.button("Extract PDF Content", key="extract_button"):
            if os.path.exists(pdf_path):
                with st.spinner("Extracting PDF content..."):
                    success = extract_pdf_content(pdf_path, st.session_state.db_path)
                    if success:
                        st.markdown('<div class="success-box">PDF content extracted and stored in database!</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-box">Failed to extract PDF content.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-box">PDF file not found.</div>', unsafe_allow_html=True)

    # Query input
    with st.container():
        st.subheader("❓ Ask a Question")
        user_query = st.text_input("Ask a question about the PDF:", placeholder="e.g., What is the voltage rating?", key="query_input")
        if user_query and st.button("Submit Query", key="submit_button"):
            with st.spinner("Processing query..."):
                response, status_message = get_rag_response(user_query, st.session_state.db_path, st.session_state.history)
                st.session_state.history.append({"query": user_query, "response": response})
                
                # Display status message
                if "successfully fetched" in status_message:
                    st.markdown(f'<div class="success-box">{status_message}</div>', unsafe_allow_html=True)
                elif "No relevant data" in status_message:
                    st.markdown(f'<div class="warning-box">{status_message}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-box">{status_message}</div>', unsafe_allow_html=True)
                
                # Display response
                st.write("**Response:**")
                if "Error" in response or "Sorry" in response:
                    st.markdown(f'<div class="error-box">{response}</div>', unsafe_allow_html=True)
                else:
                    st.write(response)

    # Clean up temporary file
    if pdf_option == "Upload PDF" and os.path.exists("temp.pdf"):
        os.remove("temp.pdf")

# Data Page
elif page == "Data":
    st.header("📊 Extracted Data")
    st.write("View the text, images, and tables extracted from the PDF.")

    # Text Data
    with st.expander("📝 Extracted Text", expanded=False):
        conn = sqlite3.connect(st.session_state.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT page_number, content FROM texts")
        texts = cursor.fetchall()
        conn.close()
        
        if texts:
            for page, content in texts[:10]:  # Limit to 10 for preview
                st.write(f"**Page {page}:**")
                st.write(content[:200] + "..." if len(content) > 200 else content)
                st.write("---")
            if len(texts) > 10:
                st.write(f"Showing 10 of {len(texts)} text entries. Extract more data to view all.")
        else:
            st.write("No text data found.")

    # Images
    with st.expander("🖼️ Extracted Images", expanded=False):
        conn = sqlite3.connect(st.session_state.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT image_name, image_format, image_data FROM images")
        images = cursor.fetchall()
        conn.close()
        
        if images:
            cols = st.columns(3)
            for idx, (name, fmt, data) in enumerate(images):
                with cols[idx % 3]:
                    st.image(data, caption=name, use_column_width=True)
        else:
            st.write("No images found.")

    # Tables
    with st.expander("📋 Extracted Tables", expanded=False):
        conn = sqlite3.connect(st.session_state.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT page_number, table_index, content FROM tables")
        tables = cursor.fetchall()
        conn.close()
        
        if tables:
            for page, idx, content in tables:
                table_data = json.loads(content)
                st.write(f"**Table (Page {page}, Index {idx}):**")
                st.table(table_data)
        else:
            st.write("No tables found.")

# History Page
elif page == "History":
    st.header("🕒 Conversation History")
    st.write("View and manage your conversation history with the chatbot.")

    if st.button("Clear History", key="clear_history"):
        st.session_state.history = []
        st.markdown('<div class="success-box">Conversation history cleared!</div>', unsafe_allow_html=True)

    if st.session_state.history:
        for item in st.session_state.history:
            with st.expander(f"Q: {item['query'][:50]}...", expanded=False):
                st.write(f"**Question:** {item['query']}")
                st.write(f"**Answer:** {item['response']}")
    else:
        st.write("No conversation history yet.")