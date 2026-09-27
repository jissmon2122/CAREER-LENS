import re

class ResumeValidator:
    """
    Strict Multi-Signal Resume Document Validator.
    Determines whether an extracted PDF text is a genuine Resume/CV or an unrelated document 
    (Research Paper, Invoice, Assignment, Textbook, Article, etc.).
    """

    @classmethod
    def validate_document(cls, raw_text):
        """
        Validate document text and return classification metadata.
        
        Statuses:
            - VALID_RESUME
            - INVALID_RESUME
            - INSUFFICIENT_TEXT
        
        Document Types:
            - RESUME
            - RESEARCH_PAPER
            - INVOICE
            - ASSIGNMENT
            - NON_RESUME
            - SCANNED_DOCUMENT
        """
        if not raw_text or len(raw_text.strip()) < 40:
            return {
                "status": "INSUFFICIENT_TEXT",
                "document_type": "SCANNED_DOCUMENT",
                "confidence": 0.0,
                "positive_signals": [],
                "negative_signals": ["insufficient_text_length"],
                "reason": "Document text is empty or too short (< 40 characters). Scanned PDF or OCR required."
            }

        text_lower = raw_text.lower()
        words = re.findall(r'\b[a-z0-9\-\+\.#]+\b', text_lower)
        word_count = len(words)

        positive_signals = []
        negative_signals = []
        pos_score = 0
        neg_score = 0

        # --- 1. POSITIVE RESUME SIGNALS ---
        # Contact signals
        if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_text):
            positive_signals.append("email_present")
            pos_score += 15

        if re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', raw_text):
            positive_signals.append("phone_present")
            pos_score += 15

        if "linkedin.com" in text_lower or "github.com" in text_lower:
            positive_signals.append("online_profile_url")
            pos_score += 10

        # Resume Section Headings (Regex tolerant of colons/numbers)
        if re.search(r'\b(education|academic background|educational qualification|qualification|academic history|scholastic achievement)\b', text_lower):
            positive_signals.append("education_heading")
            pos_score += 20

        if re.search(r'\b(degree|b\.tech|b\.e\.|b\.sc|m\.sc|bca|m\.tech|mca|ph\.d|phd|postdoc|bachelor|master|doctorate|diploma|university|college|institute|school|cgpa|gpa)\b', text_lower):
            positive_signals.append("degree_education_keywords")
            pos_score += 15

        if re.search(r'\b(skills|technical skills|core competencies|key skills|tech stack|skill set|expertise|competencies|areas of expertise|tools|methods)\b', text_lower):
            positive_signals.append("skills_heading")
            pos_score += 20

        if re.search(r'\b(projects|academic projects|key projects|personal projects|research projects|observational projects|capstone)\b', text_lower):
            positive_signals.append("projects_heading")
            pos_score += 15

        if re.search(r'\b(experience|work experience|employment|professional experience|internship|work history|clinical experience|teaching experience|research experience|professional history)\b', text_lower):
            positive_signals.append("experience_heading")
            pos_score += 15

        if re.search(r'\b(certifications|certificates|licenses|achievements|awards|honors|publications|presentations|grants)\b', text_lower):
            positive_signals.append("certifications_heading")
            pos_score += 10

        if re.search(r'\b(summary|profile|professional summary|career objective|objective|biography|about me)\b', text_lower):
            positive_signals.append("summary_heading")
            pos_score += 10

        # --- 2. NEGATIVE NON-RESUME SIGNALS ---
        # Research Paper Signals
        paper_signals = 0
        if re.search(r'\b(abstract)\b', text_lower):
            negative_signals.append("abstract_section")
            paper_signals += 25
        if re.search(r'\b(methodology|literature review|experimental setup|experimental results)\b', text_lower):
            negative_signals.append("research_methodology")
            paper_signals += 25
        if re.search(r'\b(references|bibliography|works cited)\b', text_lower) and ("author" in text_lower or "vol." in text_lower or "pp." in text_lower or "doi" in text_lower):
            negative_signals.append("academic_references")
            paper_signals += 30
        if re.search(r'\b(doi:|arxiv:|ieee|acm|proceedings|journal of)\b', text_lower):
            negative_signals.append("publication_doi_journal")
            paper_signals += 30
        if re.search(r'\b(fig\.|figure \d|table \d|equation \d)\b', text_lower):
            negative_signals.append("paper_figure_table_reference")
            paper_signals += 15

        # Invoice / Financial Signals
        invoice_signals = 0
        if re.search(r'\b(invoice number|invoice #|inv-\d+)\b', text_lower):
            negative_signals.append("invoice_number")
            invoice_signals += 35
        if re.search(r'\b(subtotal|tax amount|vat|gstin|amount due|total due|payment terms)\b', text_lower):
            negative_signals.append("financial_invoice_totals")
            invoice_signals += 35
        if re.search(r'\b(bill to|ship to|billing address)\b', text_lower):
            negative_signals.append("billing_address")
            invoice_signals += 25

        # Assignment / Homework Signals
        assignment_signals = 0
        if re.search(r'\b(assignment \d|homework \d|problem \d|question \d)\b', text_lower) and ("due date" in text_lower or "course code" in text_lower or "submitted by" in text_lower or "instructor" in text_lower):
            negative_signals.append("academic_assignment")
            assignment_signals += 35

        neg_score = paper_signals + invoice_signals + assignment_signals

        # --- 3. CLASSIFICATION & DECISION ENGINE ---
        net_score = pos_score - neg_score

        # Check document type
        document_type = "RESUME"
        if paper_signals >= 35 and paper_signals > pos_score:
            document_type = "RESEARCH_PAPER"
        elif invoice_signals >= 35 and invoice_signals > pos_score:
            document_type = "INVOICE"
        elif assignment_signals >= 35 and assignment_signals > pos_score:
            document_type = "ASSIGNMENT"
        elif neg_score >= 35 and neg_score > pos_score:
            document_type = "NON_RESUME"

        # Student Resume Grace Handling:
        # A valid student resume MUST have:
        # 1. Contact (email or phone)
        # 2. Education or Degree
        # 3. Skills or Projects
        # 4. Low negative score (< 25)
        has_contact = ("email_present" in positive_signals) or ("phone_present" in positive_signals)
        has_education = ("education_heading" in positive_signals) or ("degree_education_keywords" in positive_signals)
        has_content = ("skills_heading" in positive_signals) or ("projects_heading" in positive_signals)

        is_valid_student_resume = has_contact and has_education and has_content and neg_score < 25
        is_high_scoring_resume = pos_score >= 45 and neg_score < 30 and document_type == "RESUME"

        if is_valid_student_resume or is_high_scoring_resume:
            status = "VALID_RESUME"
            confidence = min(0.99, max(0.70, round((pos_score - neg_score * 0.5) / 100, 2)))
            reason = f"Document recognized as a valid resume with {len(positive_signals)} resume sections detected."
        else:
            status = "INVALID_RESUME"
            confidence = min(0.99, max(0.60, round((neg_score + 30) / 100, 2))) if document_type != "RESUME" else 0.85
            if document_type == "RESEARCH_PAPER":
                reason = "Document recognized as a Research Paper (contains abstract, methodology, and academic citations)."
            elif document_type == "INVOICE":
                reason = "Document recognized as an Invoice or Billing Statement."
            elif document_type == "ASSIGNMENT":
                reason = "Document recognized as an Academic Assignment or Homework Submission."
            else:
                reason = f"Document lacks essential resume sections (Education, Skills, Projects, or Contact Info) and is classified as {document_type}."

        return {
            "status": status,
            "validation_status": status,
            "document_type": document_type,
            "confidence": confidence,
            "positive_signals": positive_signals,
            "negative_signals": negative_signals,
            "reason": reason
        }
