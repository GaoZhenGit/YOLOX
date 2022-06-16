import threading
import time
from queue import Queue

class OpencvRingBuffer:
    def __init__(self,cap,ring_size=50,skip_rate=0.5):
        self.items = [0 for i in range(ring_size)]
        self.queue = Queue(maxsize=ring_size)
        self.ring_size = ring_size #环形缓冲大小
        self.cap=cap    #cv2.VideoCapture(0)对象
        self.thread=threading.Thread(target=self.run)   #控制线程
        self.stopflag=0 #安全停止线程
        self.skip_per_frame = int(1.0/(1-skip_rate))#为了匹配帧率，跳过帧数的比率
        self.event = threading.Event()
        self.frame_count = 0
        self.skip_frame_count = 0

    def startcap(self): #开启捕捉
        self.stopflag=0
        self.thread.start()
        self.event.wait()
        print('--------------buffer thread start--------------')
    def stopcap(self): #停止捕捉
        self.stopflag=1
    def run(self): #线程
        self.event.set()
        while(self.stopflag==0):
            self.cap.grab()
            ret,img=self.cap.retrieve()
            if(ret):
                self.frame_count = self.frame_count+1
                if self.frame_count % self.skip_per_frame != 0:
                    self.push(img)
                else:
                    self.skip_frame_count = self.skip_frame_count+1
                if self.frame_count % 250 == 0:
                    print('--------------skip frame:', self.skip_frame_count,'skip rate:', (self.skip_frame_count/self.frame_count), '--------------')
            else:
                print("Plz check camera\n")
                time.sleep(0.5)
    def push(self,img):
        if self.queue.full():
            print('--------------cv buffer full--------------')
            for i in range(int(self.ring_size*0.3)): self.queue.get_nowait()
        self.queue.put_nowait(img)
    def getnew(self):#返回格式和cap.read()一致
        try:
            img = self.queue.get(block=True, timeout=5)
            return True, img
        except Exception as e:
            print('--------------cv buffer empty--------------')
            return False, None