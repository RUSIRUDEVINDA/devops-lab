from flask import Flask, request

app = Flask(__name__)


@app.get("/")
def home():
    return {"message": "Welcome to my DevOps lab"}


@app.get("/health")
def health():
    return {"status": "ok"}, 200


@app.get("/servers")
def servers():
    return {
        "servers": ["web-01", "db-01", "monitoring-01"]
    }


@app.get("/hello")
def hello():
    name = request.args.get("name", "guest")
    return {"message": f"Hello, {name}!"}


@app.post("/echo")
def echo():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {"error": "Send a JSON object"}, 400

    return {"received": data}, 200


@app.get("/demo-error")
def demo_error():
    return {"error": "Simulated server error"}, 500
