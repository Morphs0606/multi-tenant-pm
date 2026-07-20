from fastapi import FastAPI

app = FastAPI(title="Multi-Tenant Project Management API")

@app.get("/health")
def health_check():
    return {"status": "ok"}