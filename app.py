from flask import Flask, make_response, request
from flask_cors import CORS
from api.generate_pdf import generate_pdf

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["POST"])
def index():
  body = request.json
  content = generate_pdf(body['settings'], body['cards'])
  resp = make_response(bytes(content), 201)
  resp.headers.add('Content-type', 'application/pdf')
  return resp
