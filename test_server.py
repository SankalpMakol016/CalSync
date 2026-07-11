from flask import Flask

app = Flask(__name__)

@app.get("/")
def home():
    return "Hello"

if __name__ == "__main__":
    print("Before run")
    app.run(host="127.0.0.1", port=5050, debug=False)