from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LTImage, LTFigure
import pdfplumber
import sqlite3
import json
import os

def init_database(db_path):
    """Initialize SQLite database with tables for text, images, and tables."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS texts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_number INTEGER,
            content TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_name TEXT,
            image_format TEXT,
            image_data BLOB
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_number INTEGER,
            table_index INTEGER,
            content TEXT
        )
    ''')
    
    conn.commit()
    return conn

def extract_pdf_content(pdf_path, db_path="extracted_data.db"):
    """
    Extract text, images, and tables from a PDF and store in SQLite database.
    Returns True if successful, False otherwise.
    """
    try:
        # Initialize database
        conn = init_database(db_path)
        cursor = conn.cursor()
        
        # Clear existing data for this PDF (optional, comment out to keep data)
        cursor.execute("DELETE FROM texts")
        cursor.execute("DELETE FROM images")
        cursor.execute("DELETE FROM tables")
        
        # Extract text and images using pdfminer.six
        image_counter = 0
        page_number = 0
        
        for page_layout in extract_pages(pdf_path):
            page_number += 1
            for element in page_layout:
                if isinstance(element, LTTextBoxHorizontal):
                    text = element.get_text().strip()
                    if text:
                        cursor.execute(
                            "INSERT INTO texts (page_number, content) VALUES (?, ?)",
                            (page_number, text)
                        )
                
                elif isinstance(element, LTImage) or isinstance(element, LTFigure):
                    try:
                        if hasattr(element, 'stream') and element.stream:
                            image_data = element.stream.rawdata
                            image_ext = element.stream.get('Filter', 'unknown')
                            if isinstance(image_ext, bytes):
                                image_ext = image_ext.decode('utf-8').lower()
                            elif isinstance(image_ext, list):
                                image_ext = image_ext[0].decode('utf-8').lower() if isinstance(image_ext[0], bytes) else image_ext[0].lower()
                            else:
                                image_ext = image_ext.lower()

                            if 'jpeg' in image_ext or 'jpg' in image_ext:
                                ext = '.jpg'
                            elif 'png' in image_ext:
                                ext = '.png'
                            else:
                                ext = '.bin'
                            
                            image_name = f"image_{image_counter}{ext}"
                            cursor.execute(
                                "INSERT INTO images (image_name, image_format, image_data) VALUES (?, ?, ?)",
                                (image_name, ext, image_data)
                            )
                            image_counter += 1
                    except Exception as e:
                        print(f"Error extracting image: {e}")
        
        # Extract tables using pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()
                for table_idx, table in enumerate(tables):
                    if table:
                        table_json = json.dumps(table)
                        cursor.execute(
                            "INSERT INTO tables (page_number, table_index, content) VALUES (?, ?, ?)",
                            (page_num, table_idx, table_json)
                        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return False

if __name__ == "__main__":
    pdf_file = r"E:/murahari/Task/pdf_chatbot/n2xy-iec-60502-1-xlpe-pvc-0-6-1kv-cable.pdf"
    extract_pdf_content(pdf_file, "extracted_data.db")