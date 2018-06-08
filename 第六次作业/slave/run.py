#!flask/bin/python2
from flask import Flask, jsonify
from flask import request
import requests
import json
import os
import subprocess
app = Flask(__name__)

@app.route('/task', methods=['POST'])
def task():  
    task_id = request.form['task_id'] 
    print task_id
    os.system('sudo python3 task_monitor.py ' + str(task_id) + ' &')
    return "task start"

@app.route('/kill', methods=['POST'])
def kill():         
    task_id = request.form['task_id']
    print task_id
    filename = "clientnfs/jsondata"+str(task_id)+".txt"
    os.remove(filename)
    url = "http://162.105.175.73/job/succeed"
    requests.get(url)
    return "task kill"

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
