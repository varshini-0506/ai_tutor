from flask import Flask, request, jsonify
import aiml

app = Flask(__name__)
kernel = aiml.Kernel()
kernel.learn("bot/basic.aiml")
kernel.learn("bot/progress.aiml")

@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json.get("message")
    resp = kernel.respond(msg)
    return jsonify({"reply": resp})

if __name__ == "__main__":
    app.run(port=5001, debug=True)
