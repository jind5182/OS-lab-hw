#!flask/bin/python2
from flask import Flask, jsonify
from flask import send_file
from flask import request
import requests
import json
import Queue
import fcntl
import os

app = Flask(__name__)

@app.route('/job/task', methods=['POST'])
def post_job():
    if not request.json:
        abort(400)
    
    f = open('task_id.txt', 'r+')
    task_id = int(f.readline())
    task_id = task_id + 1
    f.seek(0)
    f.write(str(task_id))
    f.close()

    task = request.json
    ret = {} 
    ret['code'] = 0
    ret['message'] = ""
    
    test_no = "test"+str(task_id)
    print test_no
    ret['task_id'] = test_no
    task = dict(task.items()+ret.items())
    task['data'] = {
        "container_id": "container1",
        "node_id": "slave",
        "status": "Pending"
    }    

    ret = json.dumps(ret)
    f = open('clientnfs/jsondata'+str(task_id)+'.txt', 'w+')
    
    f.seek(0)
    json.dump(task, f)
    f.close()

    f = open("slavestatus.txt")
    slave = int(f.read())
    f.close()
    print slave
    if slave == 0:
        f = open("slavestatus.txt", 'r+')
        f.write(str(1))
        f.close()
        url = "http://162.105.175.74/task"
        body = {"task_id": task_id}
        print body
        response = requests.post(url, data=body)
        print response, response.content
        f = open("nowtask_id.txt", 'r+')
        nowtask_id = int(f.readline())
        nowtask_id = nowtask_id + 1
        f.seek(0)
        f.write(str(nowtask_id))
        f.close()
          
    return ret

@app.route('/job/status/<task_id>')
def get_jobstatus(task_id):
    task_id = int(task_id[4:])
    ret = {}
    if os.path.exists('clientnfs/jsondata'+str(task_id)+'.txt'):
        f = open('clientnfs/jsondata'+str(task_id)+'.txt')
        task = json.load(f)
        f.close()
        ret['code'] = task['code']
        ret['data'] = task['data']
        ret['message'] = task['message']
    else:
        ret['code'] = 0
        ret['data'] = None
        ret['message'] = ""
    ret = json.dumps(ret)
    
    return ret

@app.route('/job/kill', methods=['POST'])
def kill_job():
    if not request.json:
        abort(400)
    
    task_id = int(request.json['task_id'][4:])
    filename = "clientnfs/jsondata"+str(task_id)+".txt"
    f = open("nowtask_id.txt")
    nowtask_id = int(f.readline())
    f.close()
    ret = {}
    ret['code'] = 0
    if os.path.exists(filename):
        ret['data'] = "success"
        ret['message'] = ""
        if nowtask_id == task_id:
            url = "http://162.105.175.74/kill"
            body = {"task_id": task_id}
            print body
            response = requests.post(url, data=body)
            print response
        else:
            os.remove(filename)
    else:
        ret['data'] = "failure"
        ret['message'] = "no such task"
    ret = json.dumps(ret)

    return ret

@app.route('/job/succeed')
def succeed():
    print "task finish"
    
    f = open("nowtask_id.txt")
    nowtask_id = int(f.readline())
    f.close()
    f = open("task_id.txt")
    task_id = int(f.readline())
    f.close()
    if nowtask_id < task_id:
        url = "http://162.105.175.74/task"
        body = {"task_id": nowtask_id+1}
        print body
        response = requests.post(url, data=body)
        print response, response.content
        f = open("nowtask_id.txt", 'r+')
        nowtask_id = int(f.readline())
        nowtask_id = nowtask_id + 1
        f.seek(0)
        f.write(str(nowtask_id))
        f.close()
    else:
        f = open("slavestatus.txt", 'r+')
        f.write(str(0))
        f.close()
    return "ok"

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
