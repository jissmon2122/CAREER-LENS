import os
from app import create_app
from app.config import Config

app = create_app()

if __name__ == '__main__':
    # Ensure uploads directory exists on startup
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    print("[SERVER] Starting Career Lens Backend Server...")
    print(f"[INFO] Server running at: http://127.0.0.1:5000")
    print(f"[INFO] Resume upload folder: {Config.UPLOAD_FOLDER}")
    
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
