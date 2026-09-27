import os
import re
import logging
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

class PDFService:
    """
    Robust Multi-Stage PDF Text & OCR Extraction Service.
    Primary: PyMuPDF (fitz) page text extraction
    Secondary Fallback: pdfplumber text extraction
    Tertiary Fallback: RapidOCR local ONNX engine for scanned / image-based PDFs
    Diagnostics: Password protection, Scanned/OCR detection, Corruption, Zero-page empty state.
    """

    @staticmethod
    def extract_text(file_path):
        """
        Extract text from a PDF file using PyMuPDF primary, pdfplumber secondary fallback,
        and local RapidOCR fallback for scanned/image PDFs across ALL pages.
        
        Args:
            file_path (str): Path to the PDF file.
            
        Returns:
            dict: {
                "text": str,
                "page_count": int,
                "is_valid": bool,
                "status": str,
                "message": str,
                "extraction_method": str or None,
                "extracted_char_count": int,
                "extracted_word_count": int,
                "error_details": str or None
            }
        """
        file_name = os.path.basename(file_path) if file_path else "unknown.pdf"
        file_size = os.path.getsize(file_path) if (file_path and os.path.exists(file_path)) else 0

        logger.info(f"PDF_UPLOAD_STARTED: filename={file_name}, size_bytes={file_size}")

        if not file_path or not os.path.exists(file_path):
            logger.error(f"PDF_EXTRACTION_FAILED: File not found at path {file_path}")
            return {
                "text": "",
                "page_count": 0,
                "is_valid": False,
                "status": "PDF_FILE_NOT_FOUND",
                "message": "The uploaded PDF file could not be found on the server.",
                "extraction_method": None,
                "extracted_char_count": 0,
                "extracted_word_count": 0,
                "error_details": f"File not found: {file_path}"
            }

        # Step 1: Open Document & Detect Encrypted / Password Protected PDFs
        try:
            doc = fitz.open(file_path)
        except fitz.FileDataError as e:
            logger.error(f"PDF_CORRUPTED: Failed to open PDF file {file_name} - {str(e)}")
            return {
                "text": "",
                "page_count": 0,
                "is_valid": False,
                "status": "PDF_CORRUPTED",
                "message": "This PDF could not be read. Please try exporting or saving the resume as a new PDF.",
                "extraction_method": None,
                "extracted_char_count": 0,
                "extracted_word_count": 0,
                "error_details": str(e)
            }
        except Exception as e:
            err_str = str(e).lower()
            if "password" in err_str or "encrypted" in err_str:
                logger.warning(f"PDF_PASSWORD_PROTECTED: File {file_name} is password protected.")
                return {
                    "text": "",
                    "page_count": 0,
                    "is_valid": False,
                    "status": "PDF_PASSWORD_PROTECTED",
                    "message": "This PDF is password protected. Please upload an unlocked PDF.",
                    "extraction_method": None,
                    "extracted_char_count": 0,
                    "extracted_word_count": 0,
                    "error_details": "Document encrypted/password protected"
                }
            logger.error(f"PDF_EXTRACTION_FAILED: Unexpected error opening {file_name} - {str(e)}")
            return {
                "text": "",
                "page_count": 0,
                "is_valid": False,
                "status": "PDF_EXTRACTION_FAILED",
                "message": "We couldn't read this PDF. Please try another PDF file.",
                "extraction_method": None,
                "extracted_char_count": 0,
                "extracted_word_count": 0,
                "error_details": str(e)
            }

        if doc.is_encrypted:
            try:
                auth_success = doc.authenticate("")
            except Exception:
                auth_success = False

            if not auth_success or doc.is_encrypted:
                doc.close()
                logger.warning(f"PDF_PASSWORD_PROTECTED: File {file_name} is locked with a password.")
                return {
                    "text": "",
                    "page_count": 0,
                    "is_valid": False,
                    "status": "PDF_PASSWORD_PROTECTED",
                    "message": "This PDF is password protected. Please upload an unlocked PDF.",
                    "extraction_method": None,
                    "extracted_char_count": 0,
                    "extracted_word_count": 0,
                    "error_details": "Encrypted document requiring password authentication"
                }

        page_count = len(doc)
        logger.info(f"PDF_OPEN_SUCCESS: filename={file_name}, page_count={page_count}")
        logger.info(f"PDF_PAGE_COUNT: {page_count}")

        if page_count == 0 or getattr(doc, 'is_repair', False):
            doc.close()
            if file_size > 20:
                logger.warning(f"PDF_CORRUPTED: File {file_name} size={file_size} contains corrupted structure or 0 pages.")
                return {
                    "text": "",
                    "page_count": 0,
                    "is_valid": False,
                    "status": "PDF_CORRUPTED",
                    "message": "This PDF could not be read. Please try exporting or saving the resume as a new PDF.",
                    "extraction_method": None,
                    "extracted_char_count": 0,
                    "extracted_word_count": 0,
                    "error_details": "Corrupted PDF file structure (0 readable pages)"
                }
            else:
                logger.warning(f"PDF_EMPTY: File {file_name} is empty (0 pages).")
                return {
                    "text": "",
                    "page_count": 0,
                    "is_valid": False,
                    "status": "PDF_EMPTY",
                    "message": "The uploaded PDF does not contain readable resume content.",
                    "extraction_method": None,
                    "extracted_char_count": 0,
                    "extracted_word_count": 0,
                    "error_details": "PDF has 0 pages"
                }

        # Step 2: Primary Extraction via PyMuPDF (fitz)
        logger.info(f"PDF_TEXT_EXTRACTION_STARTED: primary_method=PyMuPDF, pages={page_count}")
        page_texts = []
        for page_idx in range(page_count):
            try:
                page = doc[page_idx]
                p_text = page.get_text("text") or ""
                p_text = p_text.replace('\x00', '')
                if p_text.strip():
                    page_texts.append(p_text.strip())
            except Exception as page_err:
                logger.warning(f"Failed to extract text from page {page_idx} of {file_name}: {page_err}")

        doc.close()

        pymupdf_combined = "\n\n".join(page_texts)
        pymupdf_clean = PDFService._normalize_text(pymupdf_combined)
        
        char_count = len(pymupdf_clean)
        words = re.findall(r'\b[a-zA-Z0-9\-\+\.#]+\b', pymupdf_clean)
        word_count = len(words)
        extraction_method = "PyMuPDF"

        logger.info(f"PyMuPDF Extraction completed: char_count={char_count}, word_count={word_count}")

        # Step 3: Secondary Fallback Extraction via pdfplumber
        if char_count < 40 or word_count < 10:
            logger.info(f"PyMuPDF text small/empty (chars={char_count}, words={word_count}). Attempting pdfplumber fallback...")
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    plumber_pages = []
                    for page in pdf.pages:
                        pt = page.extract_text() or ""
                        pt = pt.replace('\x00', '')
                        if pt.strip():
                            plumber_pages.append(pt.strip())
                    
                    plumber_combined = "\n\n".join(plumber_pages)
                    plumber_clean = PDFService._normalize_text(plumber_combined)
                    plumber_chars = len(plumber_clean)
                    plumber_words = len(re.findall(r'\b[a-zA-Z0-9\-\+\.#]+\b', plumber_clean))

                    if plumber_chars > char_count:
                        logger.info(f"pdfplumber fallback produced superior text (chars={plumber_chars}, words={plumber_words})")
                        pymupdf_clean = plumber_clean
                        char_count = plumber_chars
                        word_count = plumber_words
                        extraction_method = "pdfplumber"
            except Exception as plumber_err:
                logger.warning(f"pdfplumber fallback attempt encountered error: {plumber_err}")

        # Step 4: Scanned / Image-Based PDF Fallback via Local RapidOCR
        if char_count < 30 or word_count < 6:
            logger.info(f"PDF_OCR_REQUIRED: PyMuPDF/pdfplumber produced insufficient text (chars={char_count}, words={word_count}). Starting OCR engine...")
            
            ocr_text, ocr_status, ocr_err = PDFService._perform_ocr_fallback(file_path, page_count)
            ocr_char_count = len(ocr_text)
            ocr_words = len(re.findall(r'\b[a-zA-Z0-9\-\+\.#]+\b', ocr_text))

            if ocr_status == "OCR_SUCCESS" and (ocr_char_count >= 30 and ocr_words >= 6):
                logger.info(f"OCR_SUCCESS: filename={file_name}, extracted_chars={ocr_char_count}, extracted_words={ocr_words}, pages={page_count}")
                return {
                    "text": ocr_text,
                    "page_count": page_count,
                    "is_valid": True,
                    "status": "SUCCESS",
                    "message": "Scanned resume detected. Text extracted successfully via OCR.",
                    "extraction_method": "PyMuPDF+RapidOCR",
                    "extracted_char_count": ocr_char_count,
                    "extracted_word_count": ocr_words,
                    "error_details": None
                }
            else:
                logger.warning(f"OCR_FAILED: filename={file_name}, ocr_chars={ocr_char_count}, ocr_words={ocr_words}, err={ocr_err}")
                return {
                    "text": "",
                    "page_count": page_count,
                    "is_valid": False,
                    "status": "OCR_FAILED",
                    "message": "We couldn't read enough text from this scanned PDF. Please upload a clearer PDF.",
                    "extraction_method": "PyMuPDF+RapidOCR",
                    "extracted_char_count": ocr_char_count,
                    "extracted_word_count": ocr_words,
                    "error_details": f"OCR extraction returned insufficient text ({ocr_char_count} chars). {ocr_err or ''}"
                }

        # Step 5: Successful Standard Text Extraction
        logger.info(f"PDF_TEXT_EXTRACTION_SUCCESS: filename={file_name}, method={extraction_method}, char_count={char_count}, word_count={word_count}, page_count={page_count}")
        return {
            "text": pymupdf_clean,
            "page_count": page_count,
            "is_valid": True,
            "status": "SUCCESS",
            "message": "Text extracted successfully.",
            "extraction_method": extraction_method,
            "extracted_char_count": char_count,
            "extracted_word_count": word_count,
            "error_details": None
        }

    @staticmethod
    def _perform_ocr_fallback(file_path, page_count):
        """
        Render all PDF pages at 300 DPI and run RapidOCR engine.
        Clean up rendered images in memory immediately.
        """
        file_name = os.path.basename(file_path) if file_path else "unknown.pdf"
        logger.info(f"OCR_STARTED: filename={file_name}, total_pages={page_count}")
        try:
            from rapidocr_onnxruntime import RapidOCR
            ocr_engine = RapidOCR()
        except Exception as ocr_init_err:
            logger.error(f"OCR_FAILED: Failed to initialize RapidOCR engine: {ocr_init_err}")
            return "", "OCR_FAILED", f"OCR engine initialization error: {ocr_init_err}"

        try:
            doc = fitz.open(file_path)
            all_page_texts = []

            for page_idx in range(len(doc)):
                page = doc[page_idx]
                # Render page to high-res 300 DPI image for optimal text recognition
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes("png")
                pix = None  # Free memory immediately

                ocr_result, _ = ocr_engine(img_bytes)
                img_bytes = None  # Free memory immediately

                if ocr_result:
                    # Extract text lines
                    lines = [item[1] for item in ocr_result if item and len(item) > 1 and item[1]]
                    page_text = "\n".join(lines).strip()
                    if page_text:
                        all_page_texts.append(page_text)

            doc.close()

            ocr_combined = "\n\n".join(all_page_texts)
            ocr_clean = PDFService._normalize_text(ocr_combined)
            return ocr_clean, "OCR_SUCCESS", None

        except Exception as ocr_err:
            logger.error(f"OCR_FAILED: Error during page rendering or OCR processing: {ocr_err}")
            return "", "OCR_FAILED", str(ocr_err)

    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        Normalize broken whitespace, remove null characters, preserve paragraph structure and meaningful newlines.
        Does NOT aggressively remove punctuation or resume formatting symbols.
        """
        if not text:
            return ""

        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = text.replace('\xa0', ' ').replace('\t', ' ')
        text = re.sub(r'\n{3,}', '\n\n', text)
        lines = [line.strip() for line in text.split('\n')]
        normalized = "\n".join(lines).strip()
        return normalized
