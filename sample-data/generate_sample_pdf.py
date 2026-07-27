import os
import json
import random
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from fpdf import FPDF

# Load the API key from the backend .env file relative to this script's location
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, "..", "backend", ".env")
load_dotenv(dotenv_path=env_path)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_random_complaint_data():
    """Use Groq to generate a completely random, realistic pharma complaint."""
    print("🧠 Asking Groq to generate a random pharma complaint...")
    
    prompt = """
    Generate a highly realistic customer complaint for a pharmaceutical company.
    Make it completely random and different every time. It could be about broken tablets, 
    missing labels, incorrect liquid volume, contamination, strange smell, damaged packaging, etc.
    
    Return EXACTLY this JSON structure, with realistic made-up data:
    {
        "complaint_id": "CPT-2026-XXXX",
        "date_received": "Month DD, YYYY",
        "source": "Name of a Pharmacy, Hospital, or Distributor",
        "product_name": "Name of a drug (e.g. Paracetamol tablets, Cough Syrup, etc)",
        "strength": "e.g. 500mg, 10mg/ml",
        "batch_number": "Random alphanumeric",
        "mfg_date": "Month YYYY",
        "exp_date": "Month YYYY",
        "quantity": "e.g. 50 boxes, 2 pallets",
        "description_paragraph_1": "Detailed 2 sentence explanation of the physical defect or issue.",
        "description_paragraph_2": "A concluding sentence requesting investigation or replacement."
    }
    """
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.8 # Higher temp for more variety
    )
    
    raw = response.choices[0].message.content
    return json.loads(raw)


def create_complaint_pdf():
    # 1. Generate the dynamic content via AI
    data = generate_random_complaint_data()
    
    # 2. Build the PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Customer Complaint Report", ln=True, align='C')
    pdf.ln(10)
    
    # Content
    pdf.set_font("Arial", size=12)
    
    content_lines = [
        f"Complaint ID: {data['complaint_id']}",
        f"Date Received: {data['date_received']}",
        f"Complaint Source: {data['source']}",
        "",
        "PRODUCT DETAILS:",
        f"Product Name: {data['product_name']}",
        f"Product Strength/Grade: {data['strength']}",
        f"Batch/Lot Number: {data['batch_number']}",
        f"Manufacturing Date: {data['mfg_date']}",
        f"Expiry Date: {data['exp_date']}",
        f"Affected Quantity: {data['quantity']}",
        "",
        "COMPLAINT DESCRIPTION:",
        data['description_paragraph_1'],
        "",
        data['description_paragraph_2']
    ]
    
    for line in content_lines:
        # Multi_cell handles text wrapping for long paragraphs automatically
        pdf.multi_cell(0, 8, txt=line)
        
    # Save the pdf with a timestamp to avoid overwriting in the sample-data folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(script_dir, f"sample_complaint_{timestamp}.pdf")
    pdf.output(pdf_path)
    
    print(f"✅ Success! AI generated a new PDF at: {pdf_path}")
    print(f"Product: {data['product_name']} | Issue: {data['description_paragraph_1'][:50]}...")

if __name__ == "__main__":
    create_complaint_pdf()
