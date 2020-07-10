import sys
from time import sleep

import cv2
import numpy


def flick(x):
	pass


if len(sys.argv) <= 1:
	print('not set file name')
	exit()

video = sys.argv[1]

window_video = video
windows_controls = "controls"

cv2.namedWindow(window_video, cv2.WINDOW_NORMAL)
cv2.moveWindow(window_video, 100, 100)
cv2.resizeWindow(window_video, 500, 100)

cv2.namedWindow(windows_controls)
# cv2.moveWindow('controls', 250, 50)

controls = numpy.zeros((50, 750), numpy.uint8)
cv2.putText(controls,
			"Space: Play/Pause, Left/Right: 1 frame jump, Up/Down: 5 frame jump, +/-: playback speed, Esc: Exit",
			(40, 20),
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)

cap = cv2.VideoCapture(video)
tots = cap.get(cv2.CAP_PROP_FRAME_COUNT)

i = 0
status = 'next_frame'
preIndex = 0
frame_rate = 30
bFirstInitUi = False

frame_trackbar = "frame"
speed_trackbar = "fps"


def create_track_bar():
	cv2.createTrackbar(frame_trackbar, window_video, 0, int(tots) - 1, flick)
	cv2.setTrackbarPos(frame_trackbar, window_video, 0)

	cv2.createTrackbar(speed_trackbar, window_video, 1, 100, flick)
	cv2.setTrackbarPos(speed_trackbar, window_video, frame_rate)


def process(im):
	return cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)


create_track_bar()

while True:
	cv2.imshow(windows_controls, controls)
	try:

		if status != 'stay' or preIndex != i:
			if i == tots - 1:
				i = 0

			cv2.setTrackbarPos(frame_trackbar, window_video, i)
			if preIndex != i - 1:
				cap.set(cv2.CAP_PROP_POS_FRAMES, i)
				print('call seek')

			print('index', i)
			ret, im = cap.read()
			displayW = 1280.0
			r = displayW / im.shape[1]
			dim = (int(displayW), int(im.shape[0] * r))
			im = cv2.resize(im, dim, interpolation=cv2.INTER_AREA)

			cv2.putText(im, str(i), (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 1)
			cv2.imshow(window_video, im)
			if status != 'play':
				status = 'stay'
			preIndex = i
			if not bFirstInitUi:
				bFirstInitUi = True

		preStatus = status
		status = {
			ord('s'): 'stay', ord('S'): 'stay',
			ord('w'): 'play', ord('W'): 'play',
			ord('a'): 'prev_frame', ord('A'): 'prev_frame',
			ord('d'): 'next_frame', ord('D'): 'next_frame',
			ord('-'): 'slow', ord('_'): 'slow',
			ord('+'): 'fast', ord('='): 'fast',
			ord('c'): 'snap', ord('C'): 'snap',
			ord('j'): 'next_5_frame', ord('J'): 'next_5_frame',
			ord('h'): 'pre_5_frame', ord('H'): 'pre_5_frame',
			ord(' '): 'play_pause', ord(' '): 'play_pause',
			2555904: 'next_frame',
			2424832: 'prev_frame',
			2490368: 'next_5_frame',
			2621440: 'pre_5_frame',
			-1: status,
			27: 'exit'}[cv2.waitKeyEx(10)]

		if status == 'play':
			frame_rate = cv2.getTrackbarPos(speed_trackbar, window_video)
			sleep(1.0 / frame_rate)
			i += 1
			continue
		if status == 'stay':
			i = cv2.getTrackbarPos(frame_trackbar, window_video)
		if status == 'exit':
			break
		if status == 'prev_frame':
			i -= 1

		if status == 'next_frame':
			i += 1
		if status == 'slow':
			frame_rate = max(frame_rate - 5, 0)
			cv2.setTrackbarPos(speed_trackbar, window_video, frame_rate)
		if status == 'fast':
			frame_rate = min(100, frame_rate + 5)
			cv2.setTrackbarPos(speed_trackbar, window_video, frame_rate)
			status = 'play'
		if status == 'snap':
			cv2.imwrite("./" + "Snap_" + str(i) + ".jpg", im)
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
cv2.destroyWindow(window_video)
