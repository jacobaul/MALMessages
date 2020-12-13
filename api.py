from flask import Flask, jsonify, request
import main
import datetime
import time
import sys

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>(Very) Unofficial MyAnimeList chat api</h1> <h2>Endpoints:</h2> <li>/get_new_since?date=Y-m-d-H-M-S </li><li>/get_new_since_user?date=Y-m-d-H-M-S&user=USERNAME</li><li>/get_n_combined_user?n=5&user=USERNAME</li>"

@app.route('/get_new_since')
def get_new_since():
    username = request.headers.get('username')
    password = request.headers.get('password')
    request_date = request.args.get('date',
            default = (datetime.datetime.now() - datetime.timedelta(days=3)).strftime('%Y-%m-%d-%H-%M-%S'),
            type=str)
    date = datetime.datetime.strptime(request_date,'%Y-%m-%d-%H-%M-%S')
    main.login(username,password)
    messages = main.get_new_since(date)
    main.logout()
    return jsonify(messages)


@app.route('/get_new_since_user')
def get_new_since_user():
    username = request.headers.get('username')
    password = request.headers.get('password')
    request_date = request.args.get('date',
            default = (datetime.datetime.now() - datetime.timedelta(days=3)).strftime('%Y-%m-%d-%H-%M-%S'),
            type=str)
    request_user = request.args.get('user', default = '', type=str)
    date = datetime.datetime.strptime(request_date,'%Y-%m-%d-%H-%M-%S')
    main.login(username,password)
    messages = main.get_new_since_user(date, request_user)
    main.logout()
    return jsonify(messages)

@app.route('/get_n_combined_user')
def get_n_combined_user():
    username = request.headers.get('username')
    password = request.headers.get('password')
    request_n = request.args.get('n', default = '10', type=int)
    request_user = request.args.get('user', default = '', type=str)
    n = int(request_n)
    main.login(username,password)
    messages = main.get_n_combined_user(n, request_user)
    main.logout()
    return jsonify(messages)



if __name__ == "__main__":
    app.run(host='0.0.0.0')
