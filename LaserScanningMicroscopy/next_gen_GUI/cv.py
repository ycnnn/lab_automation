import numpy as np
import cv2 as cv
import numpy as np

def show():
    frame = np.random.normal(size=(1000,1000,3)).astype(np.float32)
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    cv.imshow('frame', gray)
    cv.waitKey(0)
    # cv.destroyAllWindows()

show()
cv.destroyAllWindows()


