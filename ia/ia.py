from flask import Flask, request, jsonify

flask = Flask(__name__)

@flask.route('/ia', methods=['POST'])
def send_data():
    flask.logger.info("get data")
    data = request.get_json()
    return jsonify(data)

if __name__ == '__main__':
    flask.run(host='0.0.0.0', port=5052, debug=True)