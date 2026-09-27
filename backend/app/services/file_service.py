import os
import time
import re
from werkzeug.utils import secure_filename
from app.config import Config

class FileService:
    """Handles PDF resume validation, storage, and naming."""

    @staticmethod
    def is_allowed_file(filename):
        """Check if file has allowed .pdf extension."""
        if not filename or '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in Config.ALLOWED_EXTENSIONS

    @staticmethod
    def validate_resume_file(file_obj):
        """
        Validates uploaded file presence, extension, MIME type, and size limit.
        Returns (is_valid: bool, error_message: str)
        """
        if not file_obj or file_obj.filename == '':
            return False, "No file selected for upload"

        if not FileService.is_allowed_file(file_obj.filename):
            return False, "Invalid file format. Only PDF files (.pdf) are allowed"

        # Check content length / file size
        file_obj.seek(0, os.SEEK_END)
        file_size = file_obj.tell()
        file_obj.seek(0)  # Reset pointer for saving

        if file_size > Config.MAX_FILE_SIZE:
            max_mb = Config.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File size exceeds maximum allowed limit of {max_mb:.0f} MB"

        if file_size == 0:
            return False, "Uploaded file is empty"

        return True, ""

    @staticmethod
    def save_resume(user_id, file_obj):
        """
        Generates secure unique filename and saves PDF file to backend/uploads/resumes/.
        Returns (stored_filename, relative_path, file_size)
        """
        # Ensure uploads folder exists
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

        original_filename = secure_filename(file_obj.filename)
        # Clean filename fallback if secure_filename removes non-ASCII chars
        if not original_filename:
            original_filename = "resume.pdf"
        elif not original_filename.lower().endswith('.pdf'):
            original_filename += ".pdf"

        # Generate unique timestamped filename: <user_id>_<timestamp>_<filename>.pdf
        timestamp = int(time.time())
        clean_user_id = str(user_id).replace(" ", "_")
        stored_filename = f"{clean_user_id}_{timestamp}_{original_filename}"
        
        full_file_path = os.path.join(Config.UPLOAD_FOLDER, stored_filename)
        
        # Save file to disk
        file_obj.save(full_file_path)
        file_size = os.path.getsize(full_file_path)

        # Store path relative to backend root
        relative_path = os.path.join('uploads/resumes', stored_filename).replace('\\', '/')

        return stored_filename, relative_path, file_size
