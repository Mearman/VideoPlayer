import os
import sys
from time import sleep

import cv2
import numpy
import pandas


def flick(x):
	pass


if len(sys.argv) > 1:
	video = sys.argv[1]
else:
	print("No file name argument provided")
	valid_file = False
	while not valid_file:
		video = input("Full video path: ")
		valid_file = os.path.exists(video)
		if not valid_file:
			print("Sorry that wasn't valid")

window_video = video
windows_controls = "controls"

fps_increment = 5
big_skip = 5

cv2.namedWindow(window_video, cv2.WINDOW_NORMAL)
cv2.moveWindow(window_video, 500, 100)

cv2.namedWindow(windows_controls)
cv2.moveWindow(windows_controls, 100, 100)
print("\nControls:", "\n")
command_text_array = [
	"Space      Play/Pause",
	"Left/Right  Jump 1 frame",
	"Up/Down   Jump 5 frames",
	"+/-       Change FPS",
	"c/s           Save frame",
	"0-9        Toggle label 0-9",
	"esc/q      Quit", ]
help_text = "\n".join(command_text_array)
print(help_text, "\n")

font_size = 0.75
height_factor = 40
line_height = int(font_size * height_factor)
width_factor = 20
char_width = int(font_size * width_factor)

controls_height = int(line_height * (len(command_text_array) + 0.5))
controls_width = int(char_width * max([len(x) for x in command_text_array]))

controls = numpy.zeros((controls_height, controls_width), numpy.uint8)

y0, dy = line_height, line_height
for frame_index_current, line in enumerate(help_text.split('\n')):
	y = y0 + frame_index_current * dy
	cv2.putText(controls, line, (int(line_height / 2), y), cv2.FONT_HERSHEY_SIMPLEX, font_size, 255)

cap = cv2.VideoCapture(video)
frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
print("frame_count", frame_count)
temp_im = cap.read()[1]
cv2.resizeWindow(window_video, temp_im.shape[1] * 2, temp_im.shape[0] * 2)

df = pandas.DataFrame(False, index=range(0, int(frame_count)),
					  columns=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
print(df)

frame_index_current = 0
frame_index_previous = 0
frame_rate = 30
bFirstInitUi = False

frame_trackbar = "frame"
speed_trackbar = "fps"

state_play = "play"
state_pause = "pause"
state_skip_fwd = "skip_fwd"
state_skip_fwd_big = "state_skip_fwd_big"
state_skip_back = "skip_back"
state_skip_back_big = "state_skip_back_big"
state_speed_increase = "speed_increase"
state_speed_decrease = "speed_decrease"
state_snapshot = "snapshot"
state_play_toggle = "play_toggle"
state_exit = "exit"

current_state = state_skip_fwd


def create_track_bar():
	cv2.createTrackbar(frame_trackbar, window_video, 0, int(frame_count) - 1, flick)
	cv2.setTrackbarPos(frame_trackbar, window_video, 0)

	cv2.createTrackbar(speed_trackbar, window_video, 1, 100, flick)
	cv2.setTrackbarPos(speed_trackbar, window_video, frame_rate)


def process(im):
	return cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)


create_track_bar()

while True:
	cv2.imshow(windows_controls, controls)
	try:
		if current_state != state_pause or frame_index_previous != frame_index_current:
			if frame_index_current >= frame_count:
				frame_index_current = 0
			elif frame_index_current < 0:
				frame_index_current = int(frame_count - 1)

			cv2.setTrackbarPos(frame_trackbar, window_video, frame_index_current)
			if frame_index_previous != frame_index_current - 1:
				cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index_current)
				print("seek to", frame_index_current)

			print('index', frame_index_current)
			ret, im = cap.read()

			cv2.putText(im, str(frame_index_current), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
			df_current_row = df.loc[frame_index_current, :]
			df_string = ' '.join(str(int(d)) for d in df_current_row)
			print("df at", frame_index_current, df_string)
			cv2.putText(im, df_string, (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
						0.75,
						(128, 128, 128),
						1)
			cv2.imshow(window_video, im)
			if current_state != state_play:
				current_state = state_pause
			frame_index_previous = frame_index_current
			if not bFirstInitUi:
				bFirstInitUi = True

		preStatus = current_state
		current_state = {
			ord(' '): state_play_toggle,
			2555904: state_skip_fwd,
			2424832: state_skip_back,
			2490368: state_skip_fwd_big,
			2621440: state_skip_back_big,
			ord('+'): state_speed_increase, ord('='): state_speed_increase,
			ord('-'): state_speed_decrease, ord('_'): state_speed_decrease,
			ord('c'): state_snapshot, ord('C'): state_snapshot,
			ord('s'): state_snapshot, ord('s'): state_snapshot,
			-1: current_state,
			ord('q'): state_exit, ord('Q'): state_exit,
			27: state_exit
		}[cv2.waitKeyEx(10)]

		if current_state == state_play:
			frame_rate = cv2.getTrackbarPos(speed_trackbar, window_video)
			if frame_rate > 0:
				sleep(1.0 / frame_rate)
				frame_index_current += 1
			else:
				current_state = state_pause
			continue
		if current_state == state_pause:
			frame_index_current = cv2.getTrackbarPos(frame_trackbar, window_video)
		if current_state == state_exit:
			break
		if current_state == state_skip_back:
			frame_index_current -= 1
		if current_state == state_skip_fwd:
			frame_index_current += 1
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
			snapshot_filename = \
				"./" + filename.split(".")[0] + "_snapshot_" + \
				str(frame_index_current).rjust(5, '0') + ".jpg"
			cv2.imwrite(snapshot_filename, im)
			print("frame", frame_index_current, "snapshot saved to", snapshot_filename)
		if current_state == state_skip_fwd_big:
			frame_index_current += big_skip
		if current_state == state_skip_back_big:
			frame_index_current -= big_skip
		if current_state == state_play_toggle:
			current_state = state_pause if (preStatus == state_play) else state_play

	except KeyError:
		print("Invalid Key was pressed")
cv2.destroyAllWindows()

# cv2.destroyWindow(window_video)
