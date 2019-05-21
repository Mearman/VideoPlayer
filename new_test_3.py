import cv2
import numpy as np
import sys
from time import sleep


def flick(x):
    pass


if len(sys.argv) <= 1:
      print('not set file name')
      exit()


video = sys.argv[1]


windName = video

#cv2.namedWindow(windName,cv2.WINDOW_NORMAL)
cv2.namedWindow(windName)
cv2.moveWindow(windName, 100, 100)
cv2.resizeWindow(windName, 500, 100)

#cv2.namedWindow('controls')
#cv2.moveWindow('controls', 250, 50)

#controls = np.zeros((50, 750), np.uint8)
#cv2.putText(controls, "W/w: Play, S/s: Stay, A/a: Prev, D/d: Next, E/e: Fast, Q/q: Slow, Esc: Exit",
#            (40, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)

cap = cv2.VideoCapture(video)
tots = cap.get(cv2.CAP_PROP_FRAME_COUNT)


i = 0
status = 'next_frame'
preIndex = 0
frame_rate = 30
bFirstInitUi = False



def create_track_bar():
    cv2.createTrackbar('S', windName, 0, int(tots)-1, flick)
    cv2.setTrackbarPos('S', windName, 0)

    cv2.createTrackbar('F', windName, 1, 100, flick)
    cv2.setTrackbarPos('F', windName, frame_rate)



def process(im):
    return cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)


create_track_bar()

while True:
  #cv2.imshow("controls",controls)
  try:

    if status != 'stay' or preIndex != i:
        if i == tots-1:
            i = 0
        
        cv2.setTrackbarPos('S', windName, i)
        if preIndex != i-1 :
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            print('call seek')
        
        
                
        #print('preindex i',preIndex,i)
        ret, im = cap.read()
        displayW = 1280.0
        r = displayW / im.shape[1]
        dim = (int(displayW), int(im.shape[0] * r))
        im = cv2.resize(im, dim, interpolation=cv2.INTER_AREA)

        cv2.putText(im,  str(i), (10, 30),#putText(图片，添加的文字，左上角坐标，字体，字体大小，颜色，字体粗细)
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 1)
        cv2.imshow(windName, im)
        if status != 'play':
            status = 'stay'
        preIndex = i
        if not bFirstInitUi:
            bFirstInitUi  = True
            

    preStatus = status
    status = {ord('s'): 'stay', ord('S'): 'stay',
              ord('w'): 'play', ord('W'): 'play',
              ord('a'): 'prev_frame', ord('A'): 'prev_frame',
              ord('d'): 'next_frame', ord('D'): 'next_frame',
              ord('q'): 'slow', ord('Q'): 'slow',
              ord('e'): 'fast', ord('E'): 'fast',
              ord('c'): 'snap', ord('C'): 'snap',
              ord('j'): 'next_5_frame', ord('J'): 'next_5_frame',
              ord('h'): 'pre_5_frame', ord('H'): 'pre_5_frame',
              ord(' '): 'play_pause', ord(' '): 'play_pause',  # 空格
              2555904: 'next_5_frame',  # 后方向键
              2424832: 'pre_5_frame',  # 后方向键
              2490368: 'next_frame',  # 向上方向
              2621440: 'prev_frame',  # 向下方向
              -1: status,
              27: 'exit'}[cv2.waitKeyEx(10)]

    if status == 'play':
      frame_rate = cv2.getTrackbarPos('F', windName)
      sleep(1.0/frame_rate)
      i += 1
      continue
    if status == 'stay':
      i = cv2.getTrackbarPos('S', windName)
    if status == 'exit':
        break
    if status == 'prev_frame':
        i -= 1

    if status == 'next_frame':
        i += 1
    if status == 'slow':
        frame_rate = max(frame_rate - 5, 0)
        cv2.setTrackbarPos('F', windName, frame_rate)
    if status == 'fast':
        frame_rate = min(100, frame_rate+5)
        cv2.setTrackbarPos('F', windName, frame_rate)
        status = 'play'
    if status == 'snap':
        cv2.imwrite("./"+"Snap_"+str(i)+".jpg", im)
        print("Snap of Frame", {}, "Taken!", i)
    if status == 'next_5_frame':
        i += 5
    if status == 'pre_5_frame':
        i -= 5
        i = i if (i >= 0) else 0
    if status == 'play_pause':
        status = 'stay' if (preStatus == 'play') else 'play'

  except KeyError:
      print("Invalid Key was pressed")
cv2.destroyWindow(windName)
