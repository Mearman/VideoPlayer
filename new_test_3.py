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


command_text_array = [
	"Space     Play/Pause",
	"Left/Right     Jump 1 frame",
	"Up/Down     Jump 5 frames",
	"+/-     Change FPS",
	"c     Save frame",
	"esc     Quit", ]
help_text = "\n".join(command_text_array)
print(help_text)

font_size = 0.75
height_factor = 40
line_height = int(font_size * height_factor)
width_factor = 20
char_width = int(font_size * width_factor)

controls_height = int(line_height * (len(command_text_array) + 0.5))
controls_width = int(char_width * max([len(x) for x in command_text_array]))

controls = numpy.zeros((controls_height, controls_width), numpy.uint8)

y0, dy = line_height, line_height
for current_frame, line in enumerate(help_text.split('\n')):
	y = y0 + current_frame * dy
	cv2.putText(controls, line, (int(line_height / 2), y), cv2.FONT_HERSHEY_SIMPLEX, font_size, 255)

cap = cv2.VideoCapture(video)
tots = cap.get(cv2.CAP_PROP_FRAME_COUNT)

current_frame = 0
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

		if current_state != state_pause or preIndex != current_frame:
			if current_frame == tots - 1:
				current_frame = 0

			cv2.setTrackbarPos(frame_trackbar, window_video, current_frame)
			if preIndex != current_frame - 1:
				cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
				print('call seek')

			print('index', current_frame)
			ret, im = cap.read()
			displayW = 1280.0
			r = displayW / im.shape[1]
			dim = (int(displayW), int(im.shape[0] * r))
			im = cv2.resize(im, dim, interpolation=cv2.INTER_AREA)

			cv2.putText(im, str(current_frame), (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 1)
			cv2.imshow(window_video, im)
			if current_state != state_play:
				current_state = state_pause
			preIndex = current_frame
			if not bFirstInitUi:
				bFirstInitUi = True

		preStatus = current_state
		current_state = {
			ord(' '): state_play_toggle,
			2555904: state_skip_fwd,
			2424832: state_skip_back,
			2490368: state_skip_fwd_5,
			2621440: state_skip_back_5,
			ord('+'): state_speed_increase, ord('='): state_speed_increase,
			ord('-'): state_speed_decrease, ord('_'): state_speed_decrease,
			ord('c'): state_snapshot, ord('C'): state_snapshot,
			-1: current_state,
			27: state_exit}[cv2.waitKeyEx(10)]

		if current_state == state_play:
			frame_rate = cv2.getTrackbarPos(speed_trackbar, window_video)
			if frame_rate > 0:
				sleep(1.0 / frame_rate)
				current_frame += 1
			continue
		if current_state == state_pause:
			current_frame = cv2.getTrackbarPos(frame_trackbar, window_video)
		if current_state == state_exit:
			break
		if current_state == state_skip_back:
			current_frame -= 1
		if current_state == state_skip_fwd:
			current_frame += 1
		if current_state == state_speed_decrease:
			frame_rate = max(frame_rate - fps_increment, 0)
			cv2.setTrackbarPos(speed_trackbar, window_video, frame_rate)
		if current_state == state_speed_increase:
			frame_rate = min(100, frame_rate + fps_increment)
			cv2.setTrackbarPos(speed_trackbar, window_video, frame_rate)
			current_state = state_play
		if current_state == state_snapshot:
			split_video_string = video.replace("\\", "/").split("/")
			filename = split_video_string[len(split_video_string) - 1]
			snapshot_filename = "./" + filename.split(".")[0] + "_snapshot_" + str(current_frame).rjust(5, '0') + ".jpg"
			cv2.imwrite(snapshot_filename, im)
			print("Snap of Frame", current_frame, "saved to", snapshot_filename)
		if current_state == state_skip_fwd_5:
			current_frame += 5
		if current_state == state_skip_back_5:
			current_frame -= 5
			current_frame = current_frame if (current_frame >= 0) else 0
		if current_state == state_play_toggle:
			current_state = state_pause if (preStatus == state_play) else state_play

	except KeyError:
		print("Invalid Key was pressed")
cv2.destroyWindow(window_video)
