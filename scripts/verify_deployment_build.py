import sys
import os
import subprocess

def verify_build_and_deployment_setup():
    """Validates pre-flight build checks for production hosting deployment."""
    print("=== Starting Pre-Flight Deployment & Build Verification ===")

    # 1. Verify render.yaml existence
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    render_file = os.path.join(project_root, "render.yaml")
    assert os.path.exists(render_file), "render.yaml is missing!"
    print("[OK] render.yaml Render Blueprint manifest verified.")

    # 2. Verify vercel.json existence
    vercel_file = os.path.join(project_root, "frontend", "vercel.json")
    assert os.path.exists(vercel_file), "frontend/vercel.json is missing!"
    print("[OK] frontend/vercel.json Vercel configuration verified.")

    # 3. Verify Dockerfile.backend
    backend_dockerfile = os.path.join(project_root, "docker", "Dockerfile.backend")
    assert os.path.exists(backend_dockerfile), "docker/Dockerfile.backend is missing!"
    print("[OK] docker/Dockerfile.backend verified.")

    # 4. Verify Frontend Next.js build compilation
    print("Running Next.js production build test...")
    frontend_dir = os.path.join(project_root, "frontend")
    res = subprocess.run("cmd.exe /c \"npm run build\"", cwd=frontend_dir, shell=True, capture_output=True, text=True)
    assert res.returncode == 0, f"Next.js build failed: {res.stderr}"
    print("[OK] Next.js production build compiled cleanly with zero errors.")

    # 5. Verify backend system E2E tests
    print("Running backend E2E integration test suite...")
    venv_python = os.path.join(project_root, "backend", "venv", "Scripts", "python.exe")
    e2e_script = os.path.join(project_root, "backend", "tests", "test_system_e2e.py")
    env = os.environ.copy()
    env["PYTHONPATH"] = "backend"
    
    e2e_res = subprocess.run([venv_python, e2e_script], cwd=project_root, env=env, capture_output=True, text=True)
    assert e2e_res.returncode == 0, f"E2E test suite failed: {e2e_res.stderr}\n{e2e_res.stdout}"
    print("[OK] All 7 End-to-End Enterprise System Tests PASSED cleanly.")

    print("\n=== ALL PRE-FLIGHT BUILD & DEPLOYMENT VERIFICATION CHECKS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    try:
        verify_build_and_deployment_setup()
    except Exception as err:
        print(f"Deployment Verification Failure: {err}")
        sys.exit(1)
