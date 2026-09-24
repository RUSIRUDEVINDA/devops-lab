from flask import Flask

app = Flask(__name__)


@app.get("/")
def home():
    return {"message": "Welcome to my DevOps lab"}


@app.get("/health")
def health():
    return {"status": "ok"}, 200
