import os
from app import create_app
from app.config import Config

app = create_app()

# Ensure upload directory exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"[WSGI] Starting Career Lens Backend Server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
