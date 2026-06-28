import os
import sys
from fpdf import FPDF

# Output folder for edge case test files
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_pdfs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class MedicalDocPDF(FPDF):
    def __init__(self, hospital_name, subtitle, address=""):
        super().__init__()
        self.hospital_name = hospital_name
        self.subtitle = subtitle
        self.address = address

    def header(self):
        self.set_font("Arial", "B", 14)
        self.set_text_color(20, 50, 90)
        self.cell(0, 8, self.hospital_name, ln=True, align="C")
        self.set_font("Arial", "I", 9)
        self.set_text_color(100, 100, 100)
        if self.address:
            self.cell(0, 5, self.address, ln=True, align="C")
        self.set_font("Arial", "B", 11)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, f"--- {self.subtitle.upper()} ---", ln=True, align="C")
        self.ln(4)
        self.set_draw_color(20, 50, 90)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()} | Confidential Medical Record", align="C")

def create_inpatient_bill():
    pdf = MedicalDocPDF("MAX SUPER SPECIALITY HOSPITAL", "Inpatient Final Tax Invoice", "1, Press Enclave Road, Saket, New Delhi - 110017 | Reg: DL-MAX-9981")
    pdf.add_page()
    pdf.set_font("Arial", "", 10)
    
    # Patient Info Block
    pdf.set_fill_color(240, 245, 250)
    pdf.rect(10, pdf.get_y(), 190, 25, "F")
    pdf.set_xy(12, pdf.get_y() + 2)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(90, 6, "Patient Name: Mrs. Ananya V. Deshmukh", ln=0)
    pdf.cell(90, 6, "IPD No: MAX/IPD/2024/8812", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.set_xy(12, pdf.get_y())
    pdf.cell(90, 5, "Age/Gender: 34 Yrs / Female", ln=0)
    pdf.cell(90, 5, "Admission Date: 18-Oct-2024 (11:15 AM)", ln=True)
    pdf.set_xy(12, pdf.get_y())
    pdf.cell(90, 5, "Treating Doctor: Dr. Vivek Awasthi (MD Med)", ln=0)
    pdf.cell(90, 5, "Discharge Date: 22-Oct-2024 (04:00 PM)", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "ITEMIZED BILLING BREAKDOWN:", ln=True)
    pdf.ln(2)
    
    # Table Header
    pdf.set_fill_color(20, 50, 90)
    pdf.set_text_color(255, 255, 250)
    pdf.cell(15, 7, "S.No", border=1, align="C", fill=True)
    pdf.cell(105, 7, "Description of Service / Therapy", border=1, fill=True)
    pdf.cell(30, 7, "Date Billed", border=1, align="C", fill=True)
    pdf.cell(40, 7, "Amount (INR)", border=1, align="R", fill=True, ln=True)
    
    # Table Rows
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 9)
    items = [
        ("1", "Private Room Rent (4 Days @ Rs 8,000/day)", "18-22 Oct", "32,000.00"),
        ("2", "ICU Step-down Monitoring (1 Day)", "19-Oct-2024", "12,000.00"),
        ("3", "Diagnostic Hematology & Dengue Serology Panel", "18-Oct-2024", "6,500.00"),
        ("4", "Intravenous Fluids & Electrolyte Management", "18-21 Oct", "8,400.00"),
        ("5", "Inj Meropenem 1g IV (High-end Antibiotic - 6 Doses)", "19-21 Oct", "18,600.00"),
        ("6", "Inj Vancomycin 500mg IV (Reserve Antibiotic)", "20-21 Oct", "14,000.00"),
        ("7", "Single Donor Platelet (SDP) Transfusion (2 Units)", "20-Oct-2024", "26,000.00"),
        ("8", "Doctor Consultation & Daily Visit Fees (4 Days)", "18-22 Oct", "10,000.00"),
        ("9", "Post-Discharge Outpatient CT Chest Scan (Anomalous Date)", "24-Oct-2024", "15,000.00")
    ]
    
    for sno, desc, dt, amt in items:
        pdf.cell(15, 6, sno, border=1, align="C")
        pdf.cell(105, 6, desc, border=1)
        pdf.cell(30, 6, dt, border=1, align="C")
        pdf.cell(40, 6, amt, border=1, align="R", ln=True)
        
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(150, 6, "Gross Total Charges:", align="R")
    pdf.cell(40, 6, "1,42,500.00", align="R", ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(150, 6, "Less: Advance Deposit Paid by Patient (Receipt #MAX/DEP/991):", align="R")
    pdf.cell(40, 6, "- 40,000.00", align="R", ln=True)
    pdf.cell(150, 6, "Less: Unused Pharmacy Return Credit:", align="R")
    pdf.cell(40, 6, "- 2,500.00", align="R", ln=True)
    
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(180, 20, 20)
    pdf.cell(150, 8, "NET PAYABLE HOSPITAL AMOUNT:", align="R")
    pdf.cell(40, 8, "INR 1,00,000.00", align="R", ln=True)
    
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "I", 9)
    pdf.multi_cell(0, 5, "Declaration: This is an automated computerized invoice. All charges are billed as per the approved institutional tariff schedule of Max Super Speciality Hospital.")
    pdf.output(os.path.join(OUTPUT_DIR, "1_Max_Inpatient_Bill.pdf"))

def create_discharge_summary():
    pdf = MedicalDocPDF("MAX SUPER SPECIALITY HOSPITAL", "Clinical Summary & Discharge Note", "Department of Internal Medicine")
    pdf.add_page()
    pdf.set_font("Arial", "", 10)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 6, "Patient Name:", 0)
    pdf.set_font("Arial", "", 10)
    pdf.cell(60, 6, "Mrs. Ananya V. Deshmukh", 0)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(30, 6, "Age / Sex:", 0)
    pdf.set_font("Arial", "", 10)
    pdf.cell(60, 6, "34 Yrs / Female", ln=True)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 6, "Date of Admission:", 0)
    pdf.set_font("Arial", "", 10)
    pdf.cell(60, 6, "18-Oct-2024", 0)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(30, 6, "Date of Discharge:", 0)
    pdf.set_font("Arial", "", 10)
    pdf.cell(60, 6, "22-Oct-2024", ln=True)
    
    pdf.ln(6)
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(20, 50, 90)
    pdf.cell(0, 7, "FINAL DIAGNOSIS:", ln=True)
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(180, 20, 20)
    pdf.cell(0, 6, "1. Dengue Hemorrhagic Fever with Severe Thrombocytopenia (ICD-10: A91)", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, "2. Mild Hepatic Transaminitis (Secondary to viral infection)", ln=True)
    
    pdf.ln(6)
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(20, 50, 90)
    pdf.cell(0, 7, "CLINICAL HISTORY & HOSPITAL COURSE:", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 10)
    history = (
        "34-year-old female presented to the emergency department on 18-Oct-2024 with high-grade fever (103.4 F), retro-orbital headache, severe myalgia, and petechial rashes on lower extremities for 4 days. Initial laboratory evaluation confirmed NS1 Antigen positive and Dengue IgM positive.\n\n"
        "During hospital stay, platelet count dropped significantly to 32,000 /mcL on 20-Oct-2024, requiring prophylactic Single Donor Platelet (SDP) transfusion (2 units). Patient was managed conservatively with aggressive IV hydration (Ringer Lactate) and antipyretics.\n\n"
        "Notably, treating physician empirically initiated broad-spectrum intravenous Meropenem and Vancomycin on day 2 due to transient febrile spikes. However, subsequent blood and urine cultures returned completely sterile with no evidence of secondary bacterial sepsis. Platelets recovered to 1,15,000 /mcL by discharge date (22-Oct-2024)."
    )
    pdf.multi_cell(0, 5.5, history)
    
    pdf.ln(6)
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(20, 50, 90)
    pdf.cell(0, 7, "DISCHARGE ADVICE & MEDICATIONS:", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, "1. Tab Paracetamol 650 mg - 1 tab SOS for fever > 100 F", ln=True)
    pdf.cell(0, 6, "2. Tab Caripill (Papaya Leaf Extract) 1100 mg - Twice daily for 5 days", ln=True)
    pdf.cell(0, 6, "3. Plenty of oral fluids (ORS, Coconut water)", ln=True)
    pdf.cell(0, 6, "4. Follow-up OPD review with Dr. Vivek Awasthi after 3 days with fresh CBC report.", ln=True)
    
    pdf.ln(15)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(100, 6, "", 0)
    pdf.cell(90, 6, "Dr. Vivek Awasthi, MD (Internal Medicine)", align="R", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(100, 6, "", 0)
    pdf.cell(90, 6, "Senior Consultant | Reg No: DMC-44912", align="R", ln=True)
    pdf.output(os.path.join(OUTPUT_DIR, "2_Max_Discharge_Summary.pdf"))

def create_lab_report():
    pdf = MedicalDocPDF("SRL DIAGNOSTICS & REFERENCE LABS", "Diagnostic Hematology & Microbiology Report", "Accredited by NABL & CAP | Lab Ref: SRL/DEL/88412")
    pdf.add_page()
    pdf.set_font("Arial", "", 10)
    
    pdf.cell(90, 6, "Patient Name: Mrs. Ananya V. Deshmukh", ln=0)
    pdf.cell(90, 6, "Sample Collected: 18-Oct-2024 (12:30 PM)", ln=True)
    pdf.cell(90, 6, "Referred By: Dr. Vivek Awasthi (Max Hospital)", ln=0)
    pdf.cell(90, 6, "Report Reported: 19-Oct-2024 (08:00 AM)", ln=True)
    
    pdf.ln(6)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, "HEMATOLOGY & SEROLOGY PANEL", ln=True)
    
    # Table Header
    pdf.set_fill_color(220, 230, 240)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(70, 6, "Investigation / Test Name", border=1, fill=True)
    pdf.cell(40, 6, "Observed Result", border=1, align="C", fill=True)
    pdf.cell(40, 6, "Biological Reference", border=1, align="C", fill=True)
    pdf.cell(40, 6, "Clinical Flag", border=1, align="C", fill=True, ln=True)
    
    pdf.set_font("Arial", "", 9)
    labs = [
        ("Hemoglobin (Hb)", "13.2 g/dL", "12.0 - 15.5 g/dL", "Normal"),
        ("Total Leukocyte Count (WBC)", "6,400 /mcL", "4,000 - 11,000 /mcL", "Normal"),
        ("Platelet Count (Automated)", "35,000 /mcL", "1,50000 - 4,50000", "CRITICAL LOW"),
        ("Dengue NS1 Antigen (ELISA)", "POSITIVE (Index 4.8)", "Negative (< 0.9)", "ABNORMAL"),
        ("Dengue IgM Antibody", "POSITIVE", "Negative", "ABNORMAL"),
        ("Blood Culture (Aerobic & Anaerobic)", "STERILE (No Growth)", "No bacterial growth", "NORMAL")
    ]
    
    for test, res, ref, flag in labs:
        pdf.cell(70, 6, test, border=1)
        pdf.set_font("Arial", "B" if "LOW" in flag or "ABNORMAL" in flag else "", 9)
        pdf.cell(40, 6, res, border=1, align="C")
        pdf.set_font("Arial", "", 9)
        pdf.cell(40, 6, ref, border=1, align="C")
        pdf.set_font("Arial", "B" if flag != "Normal" and flag != "NORMAL" else "", 9)
        pdf.set_text_color(180, 20, 20 if flag != "Normal" and flag != "NORMAL" else 0)
        pdf.cell(40, 6, flag, border=1, align="C", ln=True)
        pdf.set_text_color(0, 0, 0)
        
    pdf.ln(10)
    pdf.set_font("Arial", "I", 9)
    pdf.multi_cell(0, 5, "Microbiologist Note: Blood culture incubated for 48 hours shows zero bacterial colonies. High-end antibacterial antibiotics are clinically unwarranted unless secondary bacterial infection is proven.")
    pdf.output(os.path.join(OUTPUT_DIR, "3_SRL_Lab_Report.pdf"))

def create_claim_form():
    pdf = MedicalDocPDF("STAR HEALTH & ALLIED INSURANCE CO.", "Cashless Reimbursement Claim Form", "Claim Dept: Toll Free 1800-425-2255 | Policy No: STAR/HLTH/2024/9901")
    pdf.add_page()
    pdf.set_font("Arial", "", 10)
    
    pdf.set_fill_color(255, 240, 240)
    pdf.rect(10, pdf.get_y(), 190, 15, "F")
    pdf.set_xy(12, pdf.get_y() + 2)
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(180, 20, 20)
    pdf.cell(0, 5, "NOTICE: EDGE CASE TYPO PLANTED BELOW (Patient Name: 'Ananya Desmukh' missing 'h')", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(8)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 7, "Primary Insured Patient Name:", border=1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(130, 7, " Mrs. Ananya Desmukh", border=1, ln=True) # Typo: Desmukh instead of Deshmukh
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 7, "Policy Card Number:", border=1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(130, 7, " SH-882190-A", border=1, ln=True)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 7, "Treating Hospital:", border=1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(130, 7, " Max Super Speciality Hospital, Saket", border=1, ln=True)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 7, "Date of Admission:", border=1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(130, 7, " 18-Oct-2024", border=1, ln=True)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 7, "Date of Discharge:", border=1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(130, 7, " 22-Oct-2024", border=1, ln=True)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 7, "Primary Diagnosis:", border=1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(130, 7, " Dengue Fever with Severe Thrombocytopenia", border=1, ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 8, "Total Claimed Reimbursement:", border=1, fill=True)
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(180, 20, 20)
    # Asking for gross 1,42,500 instead of net 1,00,000!
    pdf.cell(130, 8, " INR 1,42,500.00 (Gross Billed Amount)", border=1, ln=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(10)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 5, "Note by Insured: I hereby declare that the particulars furnished above are true to the best of my knowledge. I am requesting full reimbursement of INR 1,42,500.00 incurred during my inpatient hospitalization.")
    pdf.output(os.path.join(OUTPUT_DIR, "4_StarHealth_Claim_Form.pdf"))

def create_payment_receipt():
    pdf = MedicalDocPDF("MAX SUPER SPECIALITY HOSPITAL", "Official Deposit & Payment Receipt", "Accounts & Billing Department | Receipt #MAX/DEP/991")
    pdf.add_page()
    pdf.set_font("Arial", "", 10)
    
    pdf.cell(100, 6, "Received With Thanks From: Mrs. Ananya V. Deshmukh", ln=0)
    pdf.cell(90, 6, "Date: 18-Oct-2024", ln=True)
    pdf.cell(100, 6, "IPD Registration: MAX/IPD/2024/8812", ln=0)
    pdf.cell(90, 6, "Payment Mode: Credit Card (HDFC)", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(60, 8, "Amount Received:", border=1)
    pdf.cell(130, 8, " INR 40,000.00 (Forty Thousand Rupees Only)", border=1, ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(60, 8, "Towards:", border=1)
    pdf.cell(130, 8, " Inpatient Admission Security Deposit", border=1, ln=True)
    
    pdf.ln(15)
    pdf.cell(0, 6, "Authorized Signatory - Accounts Cashier", align="R", ln=True)
    pdf.output(os.path.join(OUTPUT_DIR, "5_Max_Payment_Receipt.pdf"))

if __name__ == "__main__":
    print("Generating completely independent Edge Case Healthcare Claim PDFs...")
    create_inpatient_bill()
    create_discharge_summary()
    create_lab_report()
    create_claim_form()
    create_payment_receipt()
    print(f"Success! 5 unique files generated in: {OUTPUT_DIR}")
