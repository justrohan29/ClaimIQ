# ClaimIQ

**AI that audits healthcare insurance claims before they cost someone money.**

---

## The Problem

Healthcare insurance claims get delayed, underpaid, or outright rejected — not because the treatment wasn't covered, but because the paperwork is messy.

A single claim involves many independently created documents: hospital bills, discharge summaries, prescriptions, lab reports, imaging reports, pharmacy invoices, payment receipts, insurance forms, patient IDs, and doctor certificates. Each one comes from a different system, in a different format, with different terminology.

Today, insurance companies pay human reviewers to manually cross-check all of this:

- Is every required document present?
- Do all documents refer to the same patient?
- Are dates consistent across documents?
- Does the billed procedure match the diagnosis?
- Do the financials add up?

This process is **slow, expensive, error-prone**, and creates a terrible experience for everyone — patients wait weeks, hospitals chase reimbursements, and insurers burn money on manual review.

---

## What ClaimIQ Does

ClaimIQ sits between the claim submitter (hospital/patient) and the insurance company. It reviews the entire claim package **before** it's submitted and tells you what's wrong, why it matters, and how to fix it.

Think of it as **Grammarly for insurance claims**.

It does **not** approve or reject claims. It does **not** replace insurers. It performs the quality-control work that humans currently do — except it does it in seconds instead of days.

---

## How It Works (Conceptually)

1. **Upload** — User uploads a bundle of claim documents (PDFs, scanned images, photos).

2. **Read & Understand** — AI reads every document, understands medical language, and extracts structured information: patient name, dates, diagnosis, procedures, medications, amounts, invoice numbers.

3. **Classify** — AI automatically identifies what each document is (hospital bill vs. discharge summary vs. prescription vs. lab report) without manual tagging.

4. **Cross-Check** — This is the core value. AI compares information **across** all documents to find inconsistencies:
   - Patient name says "Rahul Sharma" on the bill but "Rahul Kumar" on the insurance form
   - Diagnosis says appendicitis but the bill charges for gallbladder removal
   - Admission date is June 12 on one document but June 11 on another
   - Discharge summary mentions diabetes but there are no insulin charges on the pharmacy invoice

5. **Detect Missing Documents** — AI identifies which required documents are absent (e.g., payment receipt missing, pathology report not uploaded).

6. **Score & Explain** — AI produces a **Claim Readiness Score** (e.g., 84/100) with an estimated rejection risk level, a list of every issue found, and plain-English recommendations on how to fix each one.

After fixes are applied, the score updates — demonstrating a clear before-and-after impact.

---

## Why AI Is Necessary (Not Just Software)

Traditional software can check whether a document exists or whether a date field is filled in.

Only AI can:

- **Understand** whether a diagnosis actually supports the billed procedure
- **Reason** across documents that describe the same clinical event in completely different wording
- **Detect** that free-text medical notes are inconsistent with line items on an invoice
- **Explain** issues in natural language that a human can act on immediately

The value comes from combining document understanding, multi-source reasoning, and actionable natural-language recommendations — not from simple rule matching.

---

## Why This Matters (The Money Angle)

Every issue ClaimIQ catches has a direct financial consequence:

| Issue Detected | Financial Impact |
|---|---|
| Missing discharge summary | Claim delayed ~14 days |
| Wrong admission date | Triggers manual review |
| Procedure–diagnosis mismatch | Possible rejection |
| Duplicate medicine charge | Fraud investigation |

ClaimIQ doesn't generate text for the sake of it. Every suggestion it produces prevents real money from being lost to delays, rework, or preventable rejections.

---

## Who It's For

- **Insurance companies** — cleaner incoming claims, less manual review, lower ops costs
- **Third Party Administrators (TPAs)** — process thousands of claims daily, automation saves labor
- **Hospitals** — faster reimbursement through cleaner submissions
- **Patients** — know what's wrong before you submit, avoid weeks of back-and-forth
