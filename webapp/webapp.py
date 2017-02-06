from flask import Flask, render_template, jsonify, abort, make_response, redirect, url_for, request
import json
import requests

#
# own package
#
import config

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/scan', methods=['POST','GET'])
def scan():

    list_scan = []
    for scan in request.json.get('list_scan'):
        print (scan)
        list_scan.append(str(scan))

    url = request.json.get('url')

    payload = {"list_scan":list_scan, "url":url}
    
    server_api = config.SERVER_API
    request_api = requests.post(server_api+'/scan', data=payload)
    try:
        print (payload)
        print (request_api.json())
    except:
        pass
    return (jsonify(request_api.json()))
    


if __name__ == '__main__':
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
