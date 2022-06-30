import os
import json

class ResultSaver:
    def __init__(self) -> None:
        self.frame_ret_list = []
        pass

    def save_frame(self, outputs):
        cls_map = {}
        for obj in outputs:
            clz = str(int(obj[-1]))
            if clz not in cls_map:
                cls_map[clz] = 1
            else:
                cls_map[clz] += 1
        self.frame_ret_list.append(cls_map)
        pass

    def dump(self, des):
        with open(des,'w') as f:
            j = json.dumps(self.frame_ret_list)
            f.write(j)
            f.flush()
        return des
