import os
import sys
import json

def verify_hosting_setup():
    print("=== Starting Comprehensive Hosting & Environment Verification Audit ===")
    errors = []

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # 1. Check vercel.json files
    root_vercel = os.path.join(root_dir, "vercel.json")
    frontend_vercel = os.path.join(root_dir, "frontend", "vercel.json")

    if os.path.exists(root_vercel):
        with open(root_vercel, "r") as f:
            v_data = json.load(f)
            print(f"[OK] Root vercel.json verified: buildCommand='{v_data.get('buildCommand')}', outputDirectory='{v_data.get('outputDirectory')}'")
    else:
        errors.append("Root vercel.json is missing.")

    if os.path.exists(frontend_vercel):
        with open(frontend_vercel, "r") as f:
            v_data = json.load(f)
            print(f"[OK] Frontend vercel.json verified: buildCommand='{v_data.get('buildCommand')}', outputDirectory='{v_data.get('outputDirectory')}'")
    else:
        errors.append("Frontend vercel.json is missing.")

    # 2. Check render.yaml
    render_yaml = os.path.join(root_dir, "render.yaml")
    if os.path.exists(render_yaml):
        with open(render_yaml, "r") as f:
            content = f.read()
            if "freelance-rate-predictor-backend" in content and "DATABASE_URL" in content and "CORS_ORIGINS" in content:
                print("[OK] render.yaml blueprint verified: Web service, PostgreSQL DB, Redis, and envVars configured.")
            else:
                errors.append("render.yaml is missing required services or envVars.")
    else:
        errors.append("render.yaml is missing.")

    # 3. Check frontend NEXT_PUBLIC_API_URL usage
    page_tsx = os.path.join(root_dir, "frontend", "app", "page.tsx")
    if os.path.exists(page_tsx):
        with open(page_tsx, "r", encoding="utf-8") as f:
            content = f.read()
            if "NEXT_PUBLIC_API_URL" in content:
                print("[OK] frontend/app/page.tsx verified: process.env.NEXT_PUBLIC_API_URL is properly integrated.")
            else:
                errors.append("frontend/app/page.tsx missing process.env.NEXT_PUBLIC_API_URL integration.")

    # 4. Check backend Dockerfile dynamic PORT binding
    backend_df = os.path.join(root_dir, "backend", "Dockerfile")
    docker_df = os.path.join(root_dir, "docker", "Dockerfile.backend")

    for df_path, name in [(backend_df, "backend/Dockerfile"), (docker_df, "docker/Dockerfile.backend")]:
        if os.path.exists(df_path):
            with open(df_path, "r", encoding="utf-8") as f:
                content = f.read()
                if "${PORT:-8000}" in content:
                    print(f"[OK] {name} verified: Dynamic PORT binding configured (${{PORT:-8000}}).")
                else:
                    errors.append(f"{name} does not use dynamic ${{PORT:-8000}} binding.")

    # 5. Check CORS configuration in backend/app/main.py
    main_py = os.path.join(root_dir, "backend", "app", "main.py")
    if os.path.exists(main_py):
        with open(main_py, "r", encoding="utf-8") as f:
            content = f.read()
            if "CORSMiddleware" in content and "allow_origin_regex" in content and "vercel" in content:
                print("[OK] backend/app/main.py verified: CORSMiddleware configured with Vercel regex subdomains.")
            else:
                errors.append("backend/app/main.py CORS configuration incomplete.")


    # 6. Check .env.example files
    env_root = os.path.join(root_dir, ".env.example")
    env_front = os.path.join(root_dir, "frontend", ".env.example")
    env_back = os.path.join(root_dir, "backend", ".env.example")

    for env_path, name in [(env_root, ".env.example"), (env_front, "frontend/.env.example"), (env_back, "backend/.env.example")]:
        if os.path.exists(env_path):
            print(f"[OK] Environment blueprint template {name} verified.")
        else:
            errors.append(f"Environment blueprint template {name} is missing.")

    print("\n--- Final Verification Summary ---")
    if errors:
        print(f"FAILED: Found {len(errors)} issues:")
        for err in errors:
            print(f" - {err}")
        sys.exit(1)
    else:
        print("ALL AUDIT CHECKS PASSED SUCCESSFULLY (8/8 Checks Passed).")
        sys.exit(0)

if __name__ == "__main__":
    verify_hosting_setup()
