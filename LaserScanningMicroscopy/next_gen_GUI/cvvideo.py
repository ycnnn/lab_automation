import numpy as np
import cv2 as cv
import numpy as np
import time

def show():
    width = 500
    start = time.time()
    for i in range(120):
        frame = np.random.normal(size=(width*3,width,3)).astype(np.float32)
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        cv.imshow('frame', gray)
    
        if cv.waitKey(1) == -1:
            pass
    end = time.time()
    frame = np.ones((width*3,width,3)).astype(np.float32)
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    cv.imshow('frame', gray)
    print((end-start)/120)
    if cv.waitKey(1) == -1:
        cv.destroyAllWindows()
        return

show()




