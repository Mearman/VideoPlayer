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

fps_increment = 5

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
preIndex = 0
frame_rate = 30
bFirstInitUi = False

frame_trackbar = "frame"
speed_trackbar = "fps"

state_play = "play"
state_pause = "pause"
state_skip_fwd = "skip_fwd"
state_skip_fwd_5 = "skip_fwd_5"
state_skip_back = "skip_back"
state_skip_back_5 = "skip_back_5"
state_speed_increase = "speed_increase"
state_speed_decrease = "speed_decrease"
state_snapshot = "snapshot"
state_play_toggle = "play_toggle"
state_exit = "exit"

current_state = state_skip_fwd


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

		if current_state != state_pause or preIndex != i:
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
			if current_state != state_play:
				current_state = state_pause
			preIndex = i
			if not bFirstInitUi:
				bFirstInitUi = True

		preStatus = current_state
		current_state = {
			ord('s'): state_pause, ord('S'): state_pause,
			ord('w'): state_play, ord('W'): state_play,
			ord('a'): state_skip_back, ord('A'): state_skip_back,
			ord('d'): state_skip_fwd, ord('D'): state_skip_fwd,
			ord('-'): state_speed_decrease, ord('_'): state_speed_decrease,
			ord('+'): state_speed_increase, ord('='): state_speed_increase,
			ord('c'): state_snapshot, ord('C'): state_snapshot,
			ord(' '): state_play_toggle,
			2555904: state_skip_fwd,
			2424832: state_skip_back,
			2490368: state_skip_fwd_5,
			2621440: state_skip_back_5,
			-1: current_state,
			27: state_exit}[cv2.waitKeyEx(10)]

		if current_state == state_play:
			frame_rate = cv2.getTrackbarPos(speed_trackbar, window_video)
			if frame_rate > 0:
				sleep(1.0 / frame_rate)
				i += 1
			continue
		if current_state == state_pause:
			i = cv2.getTrackbarPos(frame_trackbar, window_video)
		if current_state == state_exit:
			break
		if current_state == state_skip_back:
			i -= 1

		if current_state == state_skip_fwd:
			i += 1
		if current_state == state_speed_decrease:
			frame_rate = max(frame_rate - fps_increment, 0)
			cv2.setTrackbarPos(speed_trackbar, window_video, frame_rate)
		if current_state == state_speed_increase:
			frame_rate = min(100, frame_rate + fps_increment)
			cv2.setTrackbarPos(speed_trackbar, window_video, frame_rate)
			current_state = state_play
		if current_state == state_snapshot:
			cv2.imwrite("./" + "Snap_" + str(i) + ".jpg", im)
			print("Snap of Frame", {}, "Taken!", i)
		if current_state == state_skip_fwd_5:
			i += 5
		if current_state == state_skip_back_5:
			i -= 5
			i = i if (i >= 0) else 0
		if current_state == state_play_toggle:
			current_state = state_pause if (preStatus == state_play) else state_play

	except KeyError:
		print("Invalid Key was pressed")
cv2.destroyWindow(window_video)
