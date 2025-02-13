from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({'message': 'Le back est fonctionnel !'})

@app.route('/api/items', methods=['GET', 'POST'])
def handle_items():
    if request.method == 'GET':
        items = [
            {'id': 1, 'name': 'Item 1'},
            {'id': 2, 'name': 'Item 2'}
        ]
        return jsonify(items)
    
    elif request.method == 'POST':
        new_item = request.get_json()
        return jsonify({'message': 'Item created', 'item': new_item}), 201

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)