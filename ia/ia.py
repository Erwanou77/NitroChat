from flask import Flask, request, jsonify
import codecs


flask = Flask(__name__)

print(f"bit")
@flask.route('/ia', methods=['POST'])
def send_data():
    # data = codecs.decode(request., 'hex').decode('utf-8')
    print(f"aled")
    data = request.get_json()
    print(f"Sent data: {data}")
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    flask.run(host='0.0.0.0', port=5052, debug=True)