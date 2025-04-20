# PDF Chatbot with LLM

A Streamlit-based web application that extracts text, images, and tables from PDF files, stores them in a SQLite database, and allows users to query the content using the Ollama Mistral language model. The application features an intuitive UI with a navigation bar, data visualization, and conversation history management.

## Features

### PDF Content Extraction

- Extracts text, images, and tables from PDFs using `pdfminer.six` and `pdfplumber`.
- Stores extracted data in a SQLite database (`extracted_data.db`).

### LLM-Powered Queries

- Uses the Ollama Mistral model to answer user questions based on extracted PDF content.
- Provides feedback on whether relevant data was fetched from the database.

### Interactive Streamlit UI

- Navigation bar with three sections: **Chatbot**, **Data**, and **History**.
- Styled with custom CSS for a modern, user-friendly experience.
- Supports PDF upload or file path input.
- Displays extracted images in a grid and tables in a structured format.
- Allows clearing conversation history.

### Robust Error Handling

- Handles `None` values in table data and database errors gracefully.
- Shows success, warning, and error messages in styled boxes.

### Caching

- Uses `cachetools` to cache LLM responses for improved performance.

## Project Structure

```
pdf-chatbot/
├── app.py                  # Streamlit UI with navigation and core application logic
├── llm_handler.py          # Handles LLM interactions and database queries
├── pdf_extractor.py        # Extracts and stores PDF content in SQLite
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── extracted_data.db       # SQLite database (generated after running)
```

## Prerequisites

- **Python:** Version 3.8 or higher.
- **Ollama:** Installed and running with the Mistral model.
- **Operating System:** Windows, macOS, or Linux.
- **PDF Files:** Sample PDFs for testing (e.g., `n2xy-iec-60502-1-xlpe-pvc-0-6-1kv-cable.pdf`).

## Setup Instructions

1. **Clone the Repository**

   ```
    git clone https://github.com/your-username/pdf-chatbot.git
    cd pdf-chatbot
   ```

2. **Install Python Dependencies**

   Create a virtual environment (optional but recommended) and install the required packages:

   ```
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
   ```

3. **Install and Configure Ollama**

   Install Ollama (follow instructions at https://ollama.ai) and pull the Mistral model:

   ```
    ollama pull mistral
    ollama run mistral
   ```

   Ensure Ollama is running in the background while using the application.

4. **Prepare PDF Files**

   Place your PDF files in a known directory (e.g., `./pdfs/n2xy-iec-60502-1-xlpe-pvc-0-6-1kv-cable.pdf`) or use the upload feature in the UI.

5. **Run the Application**

   Start the Streamlit server:

   ```
    streamlit run app.py
   ```

   Open the provided URL (usually `http://localhost:8501`) in a web browser.

## Usage

### Chatbot Page

1. Select **Chatbot** from the sidebar.
2. Upload a PDF or enter a file path (e.g., `./pdfs/n2xy-iec-60502-1-xlpe-pvc-0-6-1kv-cable.pdf`).
3. Click **Extract PDF Content** to process the PDF and store data in `extracted_data.db`.
4. Enter a question (e.g., "What is the voltage rating of the cable?") and click **Submit Query**.
5. View the LLM response and a status message indicating whether data was fetched.

### Data Page

1. Select **Data** from the sidebar.
2. Expand sections to view extracted text (preview of 10 entries), images (in a 3-column grid), or tables (structured format).
3. Use this to verify extracted content.

### History Page

1. Select **History** from the sidebar.
2. View past queries and responses in expandable sections.
3. Click **Clear History** to reset the conversation history.

## Example Queries

- "What is the voltage rating of the cable?"
- "Show the cable specifications in the table."
- "What materials are used in the cable?"


## Demo

https://github.com/user-attachments/assets/fee4b463-067a-4477-b92b-f2f2bb7e5596


