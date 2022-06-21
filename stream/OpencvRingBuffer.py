import threading
import time
from queue import Queue
import numpy as np

class OpencvRingBuffer:
    def __init__(self,cap,proximate_output_fps=14,ring_size=50,keep_percentage=75,auto_keep_rate=True):
        self.items = [0 for i in range(ring_size)]
        self.queue = Queue(maxsize=ring_size)
        self.ring_size = ring_size #环形缓冲大小
        self.cap=cap    #cv2.VideoCapture(0)对象
        self.thread=threading.Thread(target=self.run)   #控制线程
        self.stopflag=0 #安全停止线程
        self.auto_keep_rate = auto_keep_rate
        self.proximate_output_fps = proximate_output_fps
        self.keep_percentage = int(keep_percentage) #为了匹配帧率，跳过帧数的比率
        self.event = threading.Event()
        self.frame_count = 0
        self.skip_frame_count = 0
        self.__set_skip()

    def __set_skip(self):
        self.keep_ids = np.linspace(0, 100, self.keep_percentage)
        self.keep_ids = [int(i) for i in self.keep_ids]

    def startcap(self): #开启捕捉
        self.stopflag=0
        self.thread.start()
        self.event.wait()
        print('--------------buffer thread start--------------')
    def stopcap(self): #停止捕捉
        self.stopflag=1
    def run(self): #线程
        self.event.set()
        start_time = time.time()
        while(self.stopflag==0):
            self.cap.grab()
            ret,img=self.cap.retrieve()
            if(ret):
                self.frame_count = self.frame_count+1
                if self.frame_count % 100 in self.keep_ids:
                    self.push(img)
                else:
                    self.skip_frame_count = self.skip_frame_count+1
                if self.frame_count % 250 == 0:
                    cost = time.time() - start_time
                    rec_fps = 250 / cost
                    start_time = time.time()
                    print(
                        '--------------skip frame:',  self.skip_frame_count,
                        'total:'+str(self.frame_count),
                        'skip-rate:'+str(self.skip_frame_count/self.frame_count), 
                        'rec-fps:%.2f' % rec_fps,
                        '--------------')
                    if self.auto_keep_rate:
                        self.keep_percentage = int(self.proximate_output_fps / rec_fps * 100)
                        print('--------------auto keep rate:'+str(self.keep_percentage)+'%--------------')
                        self.__set_skip()
                        pass
            else:
                print("Plz check camera\n")
                time.sleep(0.5)
    def push(self,img):
        if self.queue.full():
            print('--------------cv buffer full--------------')
            for i in range(int(self.ring_size*0.3)): self.queue.get_nowait()
        self.queue.put_nowait(img)
    def __try_get_frame(self,timeout):
        try:
            img = self.queue.get(block=True, timeout=timeout)
            return True, img
        except Exception as e:
            return False, None
    def getnew(self):#返回格式和cap.read()一致
        ret, img = self.__try_get_frame(0.5)
        if ret:
            return ret, img
        print('--------------cv buffer empty--------------')
        ret, img = self.__try_get_frame(2)
        if ret:
            return ret, img
        print('--------------cv buffer empty 2 second--------------')
        ret, img = self.__try_get_frame(2)
        if ret:
            return ret, img
        print('--------------cv buffer empty return null--------------')
        return False, None