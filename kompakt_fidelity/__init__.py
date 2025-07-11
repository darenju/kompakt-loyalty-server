from flask import Flask, make_response, request
from flask_cors import CORS
from .api.generate_pdf import generate_pdf
from .api.generate_epub import generate_epub

def create_app():
  app = Flask(__name__)
  CORS(app)

  @app.route("/pdf", methods=["POST"])
  def pdf():
    body = request.json
    content = generate_pdf(body['settings'], body['cards'])
    resp = make_response(bytes(content), 201)
    resp.headers.add('Content-type', 'application/pdf')
    return resp
  
  @app.route("/epub", methods=["POST"])
  def epub():
    body = request.json
    content = generate_epub(body['settings'], body['cards'])
    resp = make_response(bytes(content), 201)
    resp.headers.add('Content-type', 'application/epub+zip')
    return resp

  return app
