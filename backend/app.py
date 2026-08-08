import os
import sys
import uvicorn
import gradio as gr

# Ensure backend directory is in python search path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set default production environment variables if not passed
os.environ.setdefault("DATABASE_URL", "postgresql://neondb_owner:npg_0ECf3HIsFZmc@ep-little-sun-ayfuto9q-pooler.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
os.environ.setdefault("ENV", "production")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("CORS_ORIGINS", "*")

# Import the existing FastAPI application
from app.main import app as fastapi_app

# Create a clean Gradio Web UI
with gr.Blocks(title="Freelance Rate Predictor API & UI", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🚀 Freelance Rate Predictor Backend & API")
    gr.Markdown(
        """
        Welcome to the **Freelance Rate Predictor API Service**!
        
        * **API Documentation (Swagger UI):** [Open Interactive Docs](/docs)
        * **API Alternative Docs (ReDoc):** [Open ReDoc](/redoc)
        * **Health Check Endpoint:** [Check Health Status](/health)
        * **Prediction REST Endpoint:** `POST /api/v1/predict`
        
        Powered by **FastAPI + LightGBM ML Pipeline (0.9956 R²)** and backed by **Neon.tech Serverless PostgreSQL**.
        """
    )

# Mount Gradio onto the existing FastAPI application at root
app = gr.mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"Starting Gradio + FastAPI on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
