import os

from fastapi import FastAPI

app = FastAPI(title="Python service", version="0.1.0")


@app.get("/")
def root():
    return {"message": "Hello from Python service"}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
