# Introduction
ML-Frabeller is a Python based video frame labelleling tool aimed at laballeing video datasets for machine learning model training.
This tool uses OpenCV for its GUI and to allow frame by frame playback.

The video can be played through with variable FPS and skipped forward and backward frame-by-frame.

When scrubbing through frames, arbitrary labels of 0 - 9 can be assigned with the 0-9 keys on a frame-by-frame basis. The labels are automatically exported and load to and from a csv in the same directory as the video.

## Dependency installation
```
pip install opencv-python
pip install pandas
pip install numpy
```

## Usage:

`$ python frame_labeller.py videos/video_file.mp4`

When no params are passed, you'll be prompted to provide a valid file 

```
$ python frame_labeller.py videos/video_file.mp4
No file name argument provided
Full video path:
```

## Keyboard commands
```
Space       Play/Pause
Left/Right  Jump 1 frame
Up/Down     Jump 5 frames
+/-         Change FPS
c           Capture frame
s           Save csv of labels
0-9         Toggle label 0-9
esc/q       Quit
```
