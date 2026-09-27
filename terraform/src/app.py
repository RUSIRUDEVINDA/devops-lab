from flask import FLASK

app = FLASK(__name__)

@app.route("/")
def hello():
	return "<h1>Hello world. I'm Rusiru!<h1>"

if __name__ == "__main__":
	app.run(debug=True)

