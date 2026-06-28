import os
from fpdf import FPDF

# Ensure output directory exists
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class HospitalPDF(FPDF):
    def __init__(self, title=""):
        super().__init__()
        self.doc_title = title

    def header(self):
        # Header box
        self.set_fill_color(15, 23, 36) # Dark navy
        self.rect(0, 0, 210, 32, "F")
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "CITY GENERAL HOSPITAL & RESEARCH CENTRE", ln=1, align="C")
        self.set_font("Arial", "", 9)
        self.cell(0, 5, "Plot No. 42, Sector 15, Dwarka, New Delhi - 110075 | Tel: 011-2589-4400", ln=1, align="C")
        self.cell(0, 5, "NABH Accredited (Entry Level) | NABL Certified Lab | GSTIN: 07AABCC1234A1Z5", ln=1, align="C")
        self.ln(8)
        self.set_text_color(0, 0, 0)
        if self.doc_title:
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, self.doc_title, ln=1, align="C")
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()} | Computer Generated Official Medical Record | City General Hospital", align="C")

def generate_hospital_bill():
    pdf = HospitalPDF("FINAL HOSPITAL BILL - ITEMISED")
    pdf.add_page()
    pdf.set_font("Arial", "", 10)
    
    # Patient metadata table
    pdf.cell(95, 6, "Bill No: CGH/2024/FBL/08734", 0, 0)
    pdf.cell(95, 6, "Bill Date: 15-Jun-2024", 0, 1)
    pdf.cell(95, 6, "Patient Name: Mr. Rahul Sharma", 0, 0)  # Correct name
    pdf.cell(95, 6, "UHID: CGH-2024-78432", 0, 1)
    pdf.cell(95, 6, "Age / Gender: 32 Years / Male", 0, 0)
    pdf.cell(95, 6, "IP Number: IP/2024/06/1247", 0, 1)
    pdf.cell(95, 6, "Admission Date: 12-Jun-2024, 09:30 AM", 0, 0) # Correct admission date
    pdf.cell(95, 6, "Discharge Date: 15-Jun-2024, 11:00 AM", 0, 1)
    pdf.cell(95, 6, "Treating Doctor: Dr. Priya Mehta (MS, FACS)", 0, 0)
    pdf.cell(95, 6, "Ward: General Ward - 3A", 0, 1)
    pdf.cell(190, 6, "Primary Diagnosis: Acute Appendicitis (ICD-10: K35.80)", 0, 1)
    pdf.cell(190, 6, "Procedure: Laparoscopic Appendectomy (ICD-10-PCS: 0DTJ4ZZ)", 0, 1)
    pdf.ln(5)
    
    # Table headers
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(230, 235, 245)
    pdf.cell(15, 8, "S.No", 1, 0, "C", True)
    pdf.cell(95, 8, "Description of Service / Item", 1, 0, "L", True)
    pdf.cell(20, 8, "Qty", 1, 0, "C", True)
    pdf.cell(30, 8, "Rate (INR)", 1, 0, "R", True)
    pdf.cell(30, 8, "Amount (INR)", 1, 1, "R", True)
    
    # Items
    items = [
        ("1", "Room Charges (General Ward, 3 days)", "3", "2,500.00", "7,500.00"),
        ("2", "Operation Theatre Charges", "1", "18,000.00", "18,000.00"),
        ("3", "Surgeon Professional Fee", "1", "15,000.00", "15,000.00"),
        ("4", "Anaesthesia Charges", "1", "8,000.00", "8,000.00"),
        ("5", "Nursing Charges (3 days)", "3", "1,500.00", "4,500.00"),
        ("6", "Pathology / Diagnostics Package", "1", "4,200.00", "4,200.00"),
        ("7", "Radiology (Ultrasound Abdomen)", "1", "2,800.00", "2,800.00"),
        ("8", "Pharmacy / Medicines (Inpatient)", "1", "12,600.00", "12,600.00"),
        ("9", "Surgical Consumables & Trocar Kit", "1", "6,400.00", "6,400.00"),
        ("10", "IV Fluids & Injections Admin", "1", "3,500.00", "3,500.00"),
        ("11", "Patient Monitoring Charges (3 days)", "3", "800.00", "2,400.00"),
        ("12", "Insulin Glargine Administration", "2", "350.00", "700.00") # PLANTED: Insulin for appendicitis
    ]
    
    pdf.set_font("Arial", "", 9)
    for sno, desc, qty, rate, amt in items:
        pdf.cell(15, 7, sno, 1, 0, "C")
        pdf.cell(95, 7, desc, 1, 0, "L")
        pdf.cell(20, 7, qty, 1, 0, "C")
        pdf.cell(30, 7, rate, 1, 0, "R")
        pdf.cell(30, 7, amt, 1, 1, "R")
        
    pdf.set_font("Arial", "B", 10)
    pdf.cell(160, 8, "GROSS TOTAL CLAIMED AMOUNT", 1, 0, "R")
    pdf.cell(30, 8, "85,600.00", 1, 1, "R")
    pdf.cell(160, 8, "Less: Institutional Discount Allowed", 1, 0, "R")
    pdf.cell(30, 8, "- 600.00", 1, 1, "R") # PLANTED: Discount ignored by insurance claim form
    pdf.set_fill_color(220, 255, 220)
    pdf.cell(160, 8, "NET PAYABLE BILL TOTAL", 1, 0, "R", True)
    pdf.cell(30, 8, "85,000.00", 1, 1, "R", True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, "Payment Status: Unpaid / Cashless Approval Pending", 0, 1)
    pdf.cell(0, 6, "TPA Name: MediAssist Healthcare Services | Policy: MA/HLT/2023/981245", 0, 1)
    pdf.ln(10)
    pdf.cell(95, 6, "Prepared By: Smt. Anita Verma (Billing)", 0, 0)
    pdf.cell(95, 6, "Verified By: Mr. Rakesh Gupta (Accounts Mgr)", 0, 1)
    
    path = os.path.join(OUTPUT_DIR, "1_Hospital_Bill.pdf")
    pdf.output(path)
    print(f"Generated: {path}")

def generate_discharge_summary():
    pdf = HospitalPDF("CLINICAL DISCHARGE SUMMARY")
    pdf.add_page()
    pdf.set_font("Arial", "", 10)
    
    pdf.cell(95, 6, "Patient Name: Mr. Rahul Sharma", 0, 0)
    pdf.cell(95, 6, "UHID: CGH-2024-78432", 0, 1)
    pdf.cell(95, 6, "Age / Gender: 32 Years / Male", 0, 0)
    pdf.cell(95, 6, "IP Number: IP/2024/06/1247", 0, 1)
    pdf.cell(95, 6, "Date of Admission: 12-Jun-2024", 0, 0)
    pdf.cell(95, 6, "Date of Discharge: 15-Jun-2024", 0, 1)
    pdf.cell(190, 6, "Consultant Surgeon: Dr. Priya Mehta, MS (Gen. Surgery), FACS (MCI: DMC-45672)", 0, 1)
    pdf.ln(5)
    
    def section(title, content):
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 7, f"  {title}", 0, 1, "L", True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 6, content)
        pdf.ln(3)
        
    section("DIAGNOSIS", "Primary Diagnosis: Acute Appendicitis (ICD-10: K35.80)\nSecondary Diagnosis: None reported.") # PLANTED: None reported vs Pre-existing diabetes on form
    section("CLINICAL HISTORY & PRESENTATION", "Patient presented to Emergency on 12-Jun-2024 with acute right lower quadrant abdominal pain for 2 days, accompanied by 2 episodes of vomiting and mild fever (100.4 F). No history of previous abdominal surgeries or chronic illnesses.")
    section("EXAMINATION & DIAGNOSTIC FINDINGS", "Vitals stable. BP: 128/82 mmHg, Pulse: 96/min. Abdominal examination revealed marked tenderness at McBurney's point with positive Rovsing's sign. Ultrasound abdomen confirmed inflamed appendix measuring 11mm with periappendiceal fluid accumulation. Fasting blood sugar on admission was 96 mg/dL (Normal).")
    section("SURGICAL INTERVENTION", "Procedure Performed: Laparoscopic Appendectomy under General Anaesthesia on 13-Jun-2024. Intraoperative findings showed an edematous, non-perforated appendix. Specimen excised and sent for histopathology.")
    section("HOSPITAL COURSE & TREATMENT GIVEN", "Patient received IV Antibiotics (Ceftriaxone 1g BD, Metronidazole 500mg TDS), IV fluids, and adequate analgesia. Patient made an uneventful recovery, tolerated oral diet on POD 1, and ambulated well. Drain removed on POD 2.")
    section("DISCHARGE ADVICE & MEDICATIONS", "1. Tab Cefixime 200mg - 1 BD x 5 days\n2. Tab Metronidazole 400mg - 1 TDS x 5 days\n3. Tab Paracetamol 500mg - 1 TDS SOS x 3 days\n4. Tab Pantoprazole 40mg - 1 OD before breakfast x 7 days\nFollow up in Surgery OPD after 7 days for suture removal.")
    
    pdf.ln(10)
    pdf.cell(0, 6, "Dr. Priya Mehta (Consultant Surgeon)                   Dr. S.K. Aggarwal (HOD Surgery)", 0, 1)
    
    path = os.path.join(OUTPUT_DIR, "2_Discharge_Summary.pdf")
    pdf.output(path)
    print(f"Generated: {path}")

def generate_prescription():
    pdf = HospitalPDF("OUTPATIENT / DISCHARGE PRESCRIPTION")
    pdf.add_page()
    pdf.set_font("Arial", "", 10)
    
    pdf.cell(95, 6, "Date: 14-Jun-2024", 0, 0)
    pdf.cell(95, 6, "UHID: CGH-2024-78432", 0, 1)
    pdf.cell(95, 6, "Patient Name: Mr. Rahul Sharma", 0, 0)
    pdf.cell(95, 6, "Age / Gender: 32 / Male", 0, 1)
    pdf.cell(190, 6, "Consultant: Dr. Priya Mehta (MS Gen. Surgery)", 0, 1)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Rx / Medications Prescribed:", 0, 1)
    
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(230, 235, 245)
    pdf.cell(15, 8, "S.No", 1, 0, "C", True)
    pdf.cell(75, 8, "Medicine Name", 1, 0, "L", True)
    pdf.cell(30, 8, "Dosage", 1, 0, "C", True)
    pdf.cell(35, 8, "Frequency", 1, 0, "C", True)
    pdf.cell(35, 8, "Duration", 1, 1, "C", True)
    
    meds = [
        ("1", "Tab. Cefixime 200mg", "200 mg", "1 - 0 - 1 (After food)", "5 Days"),
        ("2", "Tab. Metronidazole 400mg", "400 mg", "1 - 1 - 1 (After food)", "5 Days"),
        ("3", "Tab. Paracetamol 500mg", "500 mg", "1 - 1 - 1 (SOS Pain)", "3 Days"),
        ("4", "Tab. Pantoprazole 40mg", "40 mg", "1 - 0 - 0 (Empty stomach)", "7 Days"),
        ("5", "Inj. Insulin Glargine", "10 IU", "0 - 0 - 1 (Subcutaneous)", "5 Days"), # PLANTED
        ("6", "Tab. Metformin 500mg", "500 mg", "1 - 0 - 1 (After food)", "Ongoing")  # PLANTED
    ]
    
    pdf.set_font("Arial", "", 9)
    for sno, name, dose, freq, dur in meds:
        pdf.cell(15, 7, sno, 1, 0, "C")
        pdf.cell(75, 7, name, 1, 0, "L")
        pdf.cell(30, 7, dose, 1, 0, "C")
        pdf.cell(35, 7, freq, 1, 0, "C")
        pdf.cell(35, 7, dur, 1, 1, "C")
        
    pdf.ln(10)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, "Special Instructions: Take antibiotics regularly. Monitor blood glucose daily while on insulin.", 0, 1)
    pdf.ln(15)
    pdf.cell(0, 6, "Signature: Dr. Priya Mehta (MCI: DMC-45672)", 0, 1)
    
    path = os.path.join(OUTPUT_DIR, "3_Prescription.pdf")
    pdf.output(path)
    print(f"Generated: {path}")

def generate_lab_report():
    pdf = HospitalPDF("DEPARTMENT OF PATHOLOGY & BIOCHEMISTRY")
    pdf.add_page()
    pdf.set_font("Arial", "", 10)
    
    pdf.cell(95, 6, "Lab Report No: LAB/2024/06/29847", 0, 0)
    pdf.cell(95, 6, "Collection Date: 11-Jun-2024, 08:45 AM", 0, 1) # PLANTED: Collected before admission (12-Jun)
    pdf.cell(95, 6, "Patient Name: Mr. Rahul Sharma", 0, 0)
    pdf.cell(95, 6, "Report Date: 11-Jun-2024, 02:30 PM", 0, 1) # PLANTED
    pdf.cell(95, 6, "UHID: CGH-2024-78432 | Age: 32Y / M", 0, 0)
    pdf.cell(95, 6, "Referred By: Dr. Priya Mehta", 0, 1)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(230, 235, 245)
    pdf.cell(60, 8, "Test Parameter", 1, 0, "L", True)
    pdf.cell(35, 8, "Observed Value", 1, 0, "C", True)
    pdf.cell(25, 8, "Unit", 1, 0, "C", True)
    pdf.cell(45, 8, "Biological Ref. Interval", 1, 0, "C", True)
    pdf.cell(25, 8, "Flag", 1, 1, "C", True)
    
    tests = [
        ("Total WBC Count", "14,200", "/uL", "4,000 - 11,000", "HIGH"),
        ("Neutrophils", "82", "%", "40 - 70", "HIGH"),
        ("Lymphocytes", "12", "%", "20 - 40", "LOW"),
        ("Haemoglobin", "14.2", "g/dL", "13.0 - 17.0", "Normal"),
        ("Platelet Count", "2,45,000", "/uL", "1,50,000 - 4,10,000", "Normal"),
        ("C-Reactive Protein (CRP)", "48.0", "mg/L", "0.0 - 5.0", "HIGH"),
        ("Fasting Blood Sugar (FBS)", "96", "mg/dL", "70 - 100", "Normal"), # PLANTED: Normal blood sugar
        ("Post-Prandial Sugar (PPBS)", "124", "mg/dL", "70 - 140", "Normal"),
        ("HbA1c (Glycated Hb)", "5.4", "%", "4.0 - 5.6", "Normal") # PLANTED: Normal HbA1c
    ]
    
    pdf.set_font("Arial", "", 9)
    for name, val, unit, ref, flag in tests:
        pdf.cell(60, 7, name, 1, 0, "L")
        pdf.cell(35, 7, val, 1, 0, "C")
        pdf.cell(25, 7, unit, 1, 0, "C")
        pdf.cell(45, 7, ref, 1, 0, "C")
        if flag != "Normal":
            pdf.set_font("Arial", "B", 9)
            pdf.set_text_color(200, 0, 0)
        pdf.cell(25, 7, flag, 1, 1, "C")
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(0, 0, 0)
        
    pdf.ln(10)
    pdf.set_font("Arial", "I", 9)
    pdf.multi_cell(0, 5, "Pathologist Note: Leukocytosis with neutrophilia and elevated CRP strongly correlate with acute inflammatory pathology (compatible with clinical diagnosis of acute appendicitis). Glycemic profile is completely within normal limits.")
    pdf.ln(15)
    pdf.set_font("Arial", "", 10)
    pdf.cell(95, 6, "Dr. Kavita Reddy, MD (Pathology)", 0, 0)
    pdf.cell(95, 6, "Dr. Arun Saxena, MD (Biochemistry)", 0, 1)
    
    path = os.path.join(OUTPUT_DIR, "4_Lab_Report.pdf")
    pdf.output(path)
    print(f"Generated: {path}")

def generate_insurance_form():
    pdf = HospitalPDF("MEDIASSIST TPA - CASHLESS / REIMBURSEMENT CLAIM FORM")
    pdf.add_page()
    pdf.set_font("Arial", "", 10)
    
    def box(title, rows):
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(220, 225, 235)
        pdf.cell(0, 7, f"  {title}", 1, 1, "L", True)
        pdf.set_font("Arial", "", 9)
        for k, v in rows:
            pdf.cell(80, 6, f"  {k}:", 1, 0, "L")
            pdf.cell(110, 6, f"  {v}", 1, 1, "L")
        pdf.ln(3)
        
    box("SECTION A: INSURED PATIENT DETAILS", [
        ("Claim Reference Number", "CLM/2024/06/78234"),
        ("Policy Number", "MA/HLT/2023/981245"),
        ("Policyholder / Patient Name", "Mr. Rahul Kumar"), # PLANTED: Rahul Kumar instead of Rahul Sharma
        ("Age / Gender", "32 Years / Male"),
        ("Contact Number", "+91-98765-43210"),
        ("Address", "14/B, Vasant Kunj, New Delhi - 110070")
    ])
    
    box("SECTION B: HOSPITALIZATION DETAILS", [
        ("Hospital Name", "City General Hospital & Research Centre"),
        ("Hospital ROHINI ID", "H-2024-DEL-1542"),
        ("Date of Admission", "11-Jun-2024"), # PLANTED: 11-Jun instead of 12-Jun
        ("Date of Discharge", "15-Jun-2024"),
        ("Total Days of Stay Claimed", "4 Days"), # PLANTED: 4 days instead of 3 days
        ("Type of Admission", "Emergency")
    ])
    
    box("SECTION C: CLINICAL & CLAIM EXPENSE DETAILS", [
        ("Primary Diagnosis", "Acute Appendicitis (ICD-10: K35.80)"),
        ("Procedure Performed", "Laparoscopic Appendectomy"),
        ("Pre-existing Medical Conditions", "Diabetes Mellitus Type 2"), # PLANTED: False pre-existing condition
        ("Total Room & Nursing Charges", "INR 12,000.00"),
        ("Surgeon & OT Charges", "INR 41,000.00"),
        ("Medicines & Consumables", "INR 19,000.00"),
        ("Diagnostics & Investigation", "INR 7,000.00"),
        ("Miscellaneous Charges", "INR 6,600.00"),
        ("TOTAL AMOUNT CLAIMED", "INR 85,600.00") # PLANTED: 85,600 instead of net 85,000
    ])
    
    pdf.ln(5)
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 4, "Declaration: I hereby declare that the details provided above are true and correct to the best of my knowledge. I consent to MediAssist seeking medical records from the hospital.")
    pdf.ln(10)
    pdf.set_font("Arial", "", 10)
    pdf.cell(100, 6, "Date: 15-Jun-2024 | Place: New Delhi", 0, 0)
    pdf.cell(90, 6, "Signature of Policyholder: [Rahul Kumar]", 0, 1, "R")
    
    path = os.path.join(OUTPUT_DIR, "5_Insurance_Claim_Form.pdf")
    pdf.output(path)
    print(f"Generated: {path}")

def generate_pharmacy_invoice():
    pdf = HospitalPDF("INPATIENT PHARMACY TAX INVOICE")
    pdf.add_page()
    pdf.set_font("Arial", "", 10)
    
    pdf.cell(95, 6, "Invoice No: PHR/2024/06/14523", 0, 0)
    pdf.cell(95, 6, "Date: 15-Jun-2024", 0, 1)
    pdf.cell(95, 6, "Patient Name: Mr. Rahul Sharma", 0, 0)
    pdf.cell(95, 6, "UHID: CGH-2024-78432", 0, 1)
    pdf.cell(95, 6, "IP Number: IP/2024/06/1247", 0, 0)
    pdf.cell(95, 6, "Ward: General Ward - 3A", 0, 1)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(230, 235, 245)
    pdf.cell(12, 7, "S.No", 1, 0, "C", True)
    pdf.cell(75, 7, "Item / Drug Name", 1, 0, "L", True)
    pdf.cell(28, 7, "Batch No", 1, 0, "C", True)
    pdf.cell(15, 7, "Qty", 1, 0, "C", True)
    pdf.cell(25, 7, "MRP (INR)", 1, 0, "R", True)
    pdf.cell(35, 7, "Total (INR)", 1, 1, "R", True)
    
    drugs = [
        ("1", "Inj. Ceftriaxone 1g", "CT24A089", "6", "285.00", "1,710.00"),
        ("2", "Inj. Metronidazole 500mg", "MZ24B034", "9", "95.00", "855.00"),
        ("3", "Inj. Paracetamol 1g", "PC24C112", "9", "62.00", "558.00"),
        ("4", "IV Ringer Lactate 1000ml", "RL24D045", "4", "85.00", "340.00"),
        ("5", "IV Normal Saline 500ml", "NS24D023", "3", "65.00", "195.00"),
        ("6", "Tab. Cefixime 200mg (Strip of 10)", "CF24E078", "1", "320.00", "320.00"),
        ("7", "Tab. Metronidazole 400mg (Strip)", "MZ24F019", "1", "180.00", "180.00"),
        ("8", "Tab. Pantoprazole 40mg (Strip)", "PP24H034", "1", "126.00", "126.00"),
        ("9", "Inj. Insulin Glargine 10ml Vial", "IG24I012", "1", "700.00", "700.00"), # PLANTED
        ("10", "Tab. Metformin 500mg (Strip)", "MF24J045", "1", "80.00", "80.00"),  # PLANTED
        ("11", "Laparoscopic Trocar Kit 10mm", "LT24K001", "1", "4,200.00", "4,200.00"),
        ("12", "Surgical Consumables & Sutures", "SC24L003", "1", "3,336.00", "3,336.00")
    ]
    
    pdf.set_font("Arial", "", 8.5)
    for sno, name, batch, qty, mrp, tot in drugs:
        pdf.cell(12, 6, sno, 1, 0, "C")
        pdf.cell(75, 6, name, 1, 0, "L")
        pdf.cell(28, 6, batch, 1, 0, "C")
        pdf.cell(15, 6, qty, 1, 0, "C")
        pdf.cell(25, 6, mrp, 1, 0, "R")
        pdf.cell(35, 6, tot, 1, 1, "R")
        
    pdf.set_font("Arial", "B", 9)
    pdf.cell(155, 7, "TOTAL PHARMACY INVOICE AMOUNT", 1, 0, "R")
    pdf.cell(35, 7, "12,600.00", 1, 1, "R")
    
    pdf.ln(10)
    pdf.set_font("Arial", "", 9)
    pdf.cell(95, 6, "Pharmacist: Mr. Deepak Kumar (Reg: DPC-3421)", 0, 0)
    pdf.cell(95, 6, "Checked By: Dr. R.K. Singh (Chief Pharmacist)", 0, 1)
    
    path = os.path.join(OUTPUT_DIR, "6_Pharmacy_Invoice.pdf")
    pdf.output(path)
    print(f"Generated: {path}")

if __name__ == "__main__":
    print("Generating sample claim documents for ClaimIQ demo...")
    generate_hospital_bill()
    generate_discharge_summary()
    generate_prescription()
    generate_lab_report()
    generate_insurance_form()
    generate_pharmacy_invoice()
    print("\nAll 6 realistic demo PDFs generated successfully in 'sample_data/output/'.")
