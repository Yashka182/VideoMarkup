import cv2, os, sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--name', help='name of video file', type=str)

centers = []


def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(param[0], ",", param[1], ",", x,",",y)
        centers.append([param[0], param[1], x, y])


args = parser.parse_args()
fname = os.path.basename(args.name)[:-4]  # filename without extentsion
caseName = os.path.dirname(args.name).split("\\")[-1]  # filename without extentsion
video = cv2.VideoCapture(args.name)  # Read video
fps = video.get(cv2.CAP_PROP_FPS)
max_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

if not video.isOpened():
    print("Could not open video")
    sys.exit()

ok, frame = video.read()
if not ok:
    print("Cannot read video file")
    sys.exit()

frame_num = 1

while ok and frame_num <= max_frames:

    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1) & 0xFF

    if ord("1") <= key <= ord("9"):
        cv2.setMouseCallback("Frame", click_event, [frame_num, chr(key)])
        mouse = cv2.waitKey(0)

    ok, frame = video.read()
    frame_num += 1

video.release()

with open(f'{caseName}_{fname}' + 'Centers' + '.txt', 'a') as f:
    for center in centers:
        f.write(f'{center[0]} {center[1]} {center[2]} {center[3]}\n')
# close all windows
cv2.destroyAllWindows()