import lxc
import sys
import json
import requests
import fcntl
import signal
import time
import os

def set_timeout(num, callback):  
    def wrap(func):  
        def handle(signum, frame): 
            raise RuntimeError  
  
        def to_do(*args, **kwargs):  
            try:  
                if num > 0:
                    signal.signal(signal.SIGALRM, handle) 
                    signal.alarm(num)  
                r = func(*args, **kwargs)    
                if num > 0:
                   signal.alarm(0)
                return r  
            except RuntimeError as e:  
                callback()  
  
        return to_do    
    return wrap 

if __name__ == '__main__':
    task_id = sys.argv[1]
    f = open('clientnfs/jsondata'+str(task_id)+'.txt', 'r+')
    task = json.load(f)
    task['data']['status'] = "Runing"
    f.seek(0)
    f.truncate()
    json.dump(task, f)
    f.close() 
    
    def after_timeout():
        print('timeout')
        os.remove('clientnfs/jsondata'+str(task_id)+'.txt')
        url = "http://162.105.175.73/job/succeed"
        requests.get(url)
        sys.exit(0)

    timeout = 0
    if 'timeout' in task:
        timeout = int(task['timeout'])

    @set_timeout(timeout, after_timeout)
    def run_command(task):
        c = lxc.Container("slave")
        commandLine = task['commandLine']
        packagePath = ""
        if 'packagePath' in task:
            packagePath = task['packagePath']
            index = packagePath.rfind('/')
            packagePath = '/home'+packagePath[:index]
            print(packagePath)
        n = 1
        if 'maxRetryCount' in task:
            n = int(task["maxRetryCount"])
        if 'resource' in task:
            os.system('sudo lxc-cgroup -n slave cpuset.cpus "'+task['resource']['cpu']+'"')
            os.system('sudo lxc-cgroup -n slave memory.limit_in_bytes "'+task['resource']['cpu']+'"')
        if not c.running:
            c.start()
        flag = False
        redirect = ''
        if commandLine.find('>') == -1:
            redirect = ' >> /home/nfs/test.log'
        for i in range(n):
            if 'packagePath' in task:
                if not c.attach_wait(lxc.attach_run_command, ['bash', '-c', 'cd '+packagePath+' && '+commandLine+redirect]):
                    flag = True
                    break
            else:
                if not c.attach_wait(lxc.attach_run_command, ['bash', '-c', commandLine+redirect]):
                    flag = True
                    break
        return flag

    flag = run_command(task)
    if flag:
        task['data']['status'] = "Succeeded"
    else:
        task['data']['status'] = "Failed"

    f = open('clientnfs/jsondata'+str(task_id)+'.txt', 'r+')
    f.seek(0)
    f.truncate()
    json.dump(task, f)

    f.close()  
    
    url = "http://162.105.175.73/job/succeed"
    requests.get(url)    
