from fastapi import FastAPI

app = FastAPI(title="My Inventory API", description="This API allows you to manage your inventory items.", version="1.0.0")

@app.get("/", description="This API allows you to manage your inventory items.")
def read_root():
    return {
        "title": "My Inventory API",
        "version": "1.0.0",
        "message": "Welcome to the Inventory API!"}

@app.get("/health", description="Check whether the API is running.")
def health_check():
    return {"status": "ok"}