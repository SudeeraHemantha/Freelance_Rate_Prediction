import os
import sys
import spaces
import gradio as gr
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure backend directory is in python search path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set default production environment variables if not passed
os.environ.setdefault("DATABASE_URL", "postgresql://neondb_owner:npg_0ECf3HIsFZmc@ep-little-sun-ayfuto9q-pooler.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
os.environ.setdefault("ENV", "production")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("CORS_ORIGINS", "*")

# Import the existing FastAPI application and routers
from app.main import app as fastapi_app
from app.api.v1 import predict_router

# Define a ZeroGPU-compatible prediction function for Gradio & Hugging Face
@spaces.GPU
def predict_gig_payout(platform: str, primary_tech: str, complexity_level: str, estimated_hours: float, urgency: str, has_auth: bool, has_apis: bool):
    """ZeroGPU inference function for Gradio interface."""
    try:
        if hasattr(fastapi_app.state, "rate_predictor") and fastapi_app.state.rate_predictor is not None:
            import pandas as pd
            input_df = pd.DataFrame([{
                "platform": platform,
                "primary_tech": primary_tech,
                "project_type": "Custom Development",
                "complexity_level": complexity_level,
                "estimated_hours": float(estimated_hours),
                "urgency": urgency,
                "has_auth": int(has_auth),
                "has_third_party_apis": int(has_apis)
            }])
            pred = fastapi_app.state.rate_predictor.predict(input_df)[0]
            hourly = pred / max(1.0, float(estimated_hours))
            return f"Predicted Total Payout: ${pred:,.2f} | Effective Rate: ${hourly:.2f}/hr"
        return "Model is initializing on server. Please try again in a few seconds."
    except Exception as err:
        return f"Prediction status: {err}"

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
    
    with gr.Row():
        with gr.Column():
            platform_in = gr.Dropdown(["Upwork", "Fiverr", "Toptal", "Freelancer"], value="Upwork", label="Freelance Platform")
            tech_in = gr.Dropdown(["Python", "React", "Node.js", "PostgreSQL", "Go", "Rust", "Django", "Tensorflow", "Flutter", "Kubernetes", "TypeScript", "Docker"], value="Python", label="Primary Technology")
            complexity_in = gr.Dropdown(["Low", "Medium", "High"], value="Medium", label="Project Complexity")
            hours_in = gr.Number(value=40.0, label="Estimated Hours")
            urgency_in = gr.Dropdown(["Low", "Medium", "High", "Urgent"], value="Medium", label="Urgency")
            auth_in = gr.Checkbox(label="Requires Authentication / Database Auth", value=True)
            apis_in = gr.Checkbox(label="Requires 3rd-Party APIs", value=True)
            btn = gr.Button("Calculate Estimated Rate & Payout", variant="primary")
        with gr.Column():
            out = gr.Textbox(label="Prediction Result", lines=3)
            
    btn.click(
        fn=predict_gig_payout,
        inputs=[platform_in, tech_in, complexity_in, hours_in, urgency_in, auth_in, apis_in],
        outputs=out
    )

# Mount FastAPI app onto Gradio Block's app so all API endpoints are accessible
app = gr.mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"Starting Gradio with ZeroGPU queue on port {port}...")
    demo.queue().launch(server_name="0.0.0.0", server_port=port)
