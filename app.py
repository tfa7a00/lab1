from flask import Flask, request, jsonify
import time, logging

from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
metrics.info("app_info", "Application info", version="1.0.0")

#test bandit
#PASSWORD = "admin123"  # bad practice

app = Flask(__name__)
@app.route("/")
def home():
    return "use /add, /subtract, /multiply, /divide with parameters a and b"


@app.route("/add")
def add():
    a = float(request.args.get("a", 0))
    b = float(request.args.get("b", 0))
    return jsonify({"result": a + b})

@app.route("/subtract")
def subtract():
    a = float(request.args.get("a", 0))
    b = float(request.args.get("b", 0))
    return jsonify({"result": a - b})

@app.route("/multiply")
def multiply():
    a = float(request.args.get("a", 0))
    b = float(request.args.get("b", 0))
    return jsonify({"result": a * b})

@app.route("/divide")
def divide():
    a = float(request.args.get("a", 0))
    b = float(request.args.get("b", 1))
    if b == 0:
        return jsonify({"error": "Division by zero"}), 400
    return jsonify({"result": a / b})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000) #debug=True is not secure in prod




logging.basicConfig(filename='app.log', level=logging.INFO)

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def log_request(response):
    duration = time.time() - request.start_time
    logging.info(f"{request.path} took {duration:.3f}s")
    return response
