from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/insights')
def api_insights():
    return jsonify({'opportunities': [], 'risks': []})

if __name__ == "__main__":
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(rule)
    app.run(debug=True, port=5000)
