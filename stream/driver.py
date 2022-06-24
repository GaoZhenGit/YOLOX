from time import sleep
import requests
from multiprocessing import Process
from multiprocessing import Queue

multiprocess_queue:Queue = None

# should call in sub process
def needSubProcessStop():
    ret = multiprocess_queue is not None and not multiprocess_queue.empty()
    if ret:
        from loguru import logger as LOGGER
        LOGGER.info('receive stop signal from main process')
        multiprocess_queue.get(False)
    return ret

def setSavePath(path):
    if multiprocess_queue is not None:
        multiprocess_queue.put(path)
    

def getRequest(url:str,param):
    printColor('request:',url,'param:'+str(param))
    x = requests.post(url=url,json=param)
    code = x.status_code
    printColor('code:',code)
    if code == 200:
        return x.json()
    else:
        return None

def isLiveStart():
    ret = getRequest('http://3.88.236.75:8080/login', {'user':{'email':'gaozhen@connect.hku.hk','password':'123'}})
    printColor(ret['result'])

class Driver:
    def __init__(self) -> None:
        pass
    
    def execYolo(self):
        self.q = Queue()
        args = (
            "webcam",
            "-f",
            "exps/example/yolox_voc/yolox_voc_s.py",
            "-c",
            "best_ckpt.pth",
            "--camid",
            "rtmp://18.166.154.193/live/abc",
            "--push",
            "rtmp://18.166.154.193/live/livestream",
            "--ofps",
            "14",
            "--conf",
            "0.25",
            "--nms",
            "0.45",
            "--tsize",
            "1280",
            "--device",
            "gpu",
            "--fp16",
            "--save_result",
            self.q
        )
        import sys,os 
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from tools import demo
        self.process = Process(target=demo.run_from_other_process, args=args, name='YoloProcess')
        self.process.start()
        printColor('yolo process start!')

    def stopYolo(self):
        self.q.put('stop')
        self.process.join()
        printColor('yolo process stop!')

    def getSavePath(self):
        path = self.q.get(False)
        if not path.endswith('.mp4'):
            path = path + '.mp4'
        return path

def printColor(text:str):
    print('\033[32m' + text + '\033[0m')
if __name__ == '__main__':
    driver = Driver()
    driver.execYolo()
    sleep(20)
    printColor('stop process!')
    driver.stopYolo()
    printColor('sub save to:' + driver.getSavePath())
