from fastapi import FastAPI
app = FastAPI(title = "My Inventory API", description = "This is a simple inventory management API built with FastAPI.", version = "1.0.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Inventory API"}