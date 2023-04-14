from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/")
def hello_world():  # put application's code here
	return "Hello World!"


@app.route("/quiz-info", methods=["GET"])
def get_quiz_info():
	return {"size": 0, "scores": []}, 200


if __name__ == "__main__":
	app.run()
