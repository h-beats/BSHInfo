from flask import Flask, Response
import os, json

app = Flask(__name__)

@app.route('/')
def home():
    with app.open_resource(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/data/output.json') as f:
        contents = f.read()
        resp = Response(contents, status=200, mimetype="application/json")
        return resp 
    

def main():
    app.run(debug=True, port=8080)

if __name__ == '__main__':
    main()