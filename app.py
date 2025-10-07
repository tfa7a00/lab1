from flask import Flask, request, jsonify
#test changes
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
    app.run(host="0.0.0.0", port=5000)
