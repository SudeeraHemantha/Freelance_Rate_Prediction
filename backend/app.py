import uvicorn
import os
import sys

# Ensure backend directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the FastAPI app
from app.main import app

if __name__ == "__main__":
    # Hugging Face expects the app to run on port 7860
    port = int(os.environ.get("PORT", 7860))
    print(f"Starting FastAPI on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
