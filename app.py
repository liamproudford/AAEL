from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/characters')
def get_characters():
    response = requests.get("https://swapi.dev/api/people/")
    data = response.json()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)