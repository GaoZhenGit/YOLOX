import time
import subprocess as sp
from threading import Thread


class RtmpPush:
    def __init__(self, rtmp_url, fps, width, height):
        width = int(width)
        height = int(height)
        sizeStr = str(width) + 'x' + str(height)
        hz = int(1000.0 / fps)
        print ('------------------size:'+ sizeStr + ' fps:' + str(fps) + ' hz:' + str(hz) + '------------------')
        command = ['ffmpeg',
                '-hwaccel','cuvid',
                '-y',
                '-f', 'rawvideo',
                '-vcodec', 'rawvideo',
                '-pix_fmt', 'bgr24',
                '-s', "{}x{}".format(width, height),
                '-r', str(fps),
                '-i', '-',
                '-c:v', 'h264_nvenc',
                '-keyint_min', '60',
                '-g', '40',
                '-pix_fmt', 'yuv420p',
                '-preset', 'llhq',
                '-b:v', '2.5M',
                '-maxrate', '3M',
                '-bufsize','5000k',
                # '-vf', 'drawtext="drawtext=fontsize=160:text=\'%\{localtime\:%T\}\'"',
                '-f', 'flv',
                '-flvflags', 'no_duration_filesize',
                rtmp_url]
        self.pipe = sp.Popen(command, stdin=sp.PIPE) #,shell=False
        pass

    def push(self, frame):
        self.pipe.stdin.write(frame.tostring())
    
    def release(self):
        self.pipe.terminate()
        pass