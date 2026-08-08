import os
import sys

# Add backend directory to Python path
root_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(root_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Set production environment variables
os.environ.setdefault("DATABASE_URL", "postgresql://neondb_owner:npg_0ECf3HIsFZmc@ep-little-sun-ayfuto9q-pooler.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
os.environ.setdefault("ENV", "production")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("CORS_ORIGINS", "*")

# Import Gradio demo and FastAPI app from backend app module
from app import demo, app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"Launching Freelance Rate Predictor on Hugging Face Spaces port {port}...")
    demo.queue().launch(server_name="0.0.0.0", server_port=port)
