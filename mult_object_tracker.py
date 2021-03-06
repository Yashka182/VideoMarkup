# https://github.com/sachinruk/Video_bbox

import cv2, os, sys
import argparse

# create directories to store individual frames and their labels
# parse the arguments used to call this script
parser = argparse.ArgumentParser()
parser.add_argument('--name', help='name of video file', type=str)
parser.add_argument('--max_obj', help='Maximum number of objects followed', type=int, default=6)
parser.add_argument('--max_frames', help='Maximum number of objects followed', type=int, default=500)
parser.add_argument('--thresh', help='Threshold for scene changes', type=float, default=2)
args = parser.parse_args()
max_obj = args.max_obj
# max_frames = args.max_frames
thresh = args.thresh

fname = os.path.basename(args.name)[:-4]  # filename without extentsion
caseName = os.path.dirname(args.name).split("\\")[-1]  # filename without extentsion
video = cv2.VideoCapture(args.name)  # Read video
fps = video.get(cv2.CAP_PROP_FPS)
max_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

label_dir = f"./labels/{caseName}"
image_dir = f"./images/{caseName}/{fname}"
os.makedirs(label_dir, exist_ok=True)
os.makedirs(image_dir, exist_ok=True)

for f in os.listdir(label_dir):
    if f.__contains__(fname):
        os.remove(os.path.join(label_dir, f))
for f in os.listdir(image_dir):
    os.remove(os.path.join(image_dir, f))

# Exit if video not opened
if not video.isOpened():
    print("Could not open video")
    sys.exit()

# Read first frame
ok, frame = video.read()
if not ok:
    print("Cannot read video file")
    sys.exit()

# h, w, _ = frame.shape
# import pdb; pdb.set_trace()
h = w = 608
initBB = None

waitKeyDelay = 200
useTracker = True

frame_num = 1
prev_mean = 0
while ok and frame_num <= max_frames:
    frame_diff = abs(frame.mean() - prev_mean)
    prev_mean = frame.mean()

    # frame = cv2.resize(frame, (h, w))
    name = f'{caseName}/' + fname  # + '_' + str(frames).zfill(4)
    origFrame = frame.copy()

    cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Frame", 1920, 1080)
    if not useTracker:
        cv2.imshow("Frame", frame)

    key = cv2.waitKey(waitKeyDelay) & 0xFF

    # if the 's' key is selected, we are going to "select" a bounding
    # box to track
    if key == ord("s") or frame_num == 1 or frame_diff > thresh:
        if(useTracker):
            trackers = cv2.MultiTracker_create()
            for i in range(max_obj):
                # select the bounding box of the object we want to track (make
                # sure you press ENTER or SPACE after selecting the ROI)
                initBB = cv2.selectROI("Frame", frame, fromCenter=False)
                # create a new object tracker for the bounding box and add it
                # to our multi-object tracker
                if initBB[2] == 0 or initBB[3] == 0:  # if no width or height
                    break
                # # start OpenCV object tracker using the supplied bounding box
                tracker = cv2.TrackerCSRT_create()
                trackers.add(tracker, frame, initBB)
        else:
            initBB = cv2.selectROI("Frame", frame, fromCenter=False)

    elif key == ord("q"):
        break

    if useTracker and initBB is not None:
        (tracking_ok, boxes) = trackers.update(frame)

        # save image and bounding box
        if tracking_ok:
            if len(boxes) > 0:  # if there is a box that is being tracked
                with open(label_dir + f'/{fname}' + '.txt', 'a') as f:
                    for bbox in boxes:
                        p1 = (int(bbox[0]), int(bbox[1]))
                        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                        cv2.rectangle(frame, p1, p2, (0, 255, 0), 2, 1)
                        # centre = [0.5*(p1[1]+p2[1])/w, 0.5*(p1[0]+p2[0])/h]
                        # width, height = (bbox[3]/w, bbox[2]/h)ss
                        f.write(f'{frame_num} {bbox[0]:.6f} {bbox[1]:.6f} {bbox[2]:.6f} {bbox[3]:.6f}\n')
                cv2.imwrite(image_dir + f'/{frame_num}' + '.jpg', frame)
        else:
            initBB = None

    if not useTracker:
        with open(label_dir + f'/{fname}' + '.txt', 'a') as f:
            p1 = (int(initBB[0]), int(initBB[1]))
            p2 = (int(initBB[0] + initBB[2]), int(initBB[1] + initBB[3]))
            cv2.rectangle(frame, p1, p2, (0, 255, 0), 2, 1)
            # centre = [0.5*(p1[1]+p2[1])/w, 0.5*(p1[0]+p2[0])/h]
            # width, height = (bbox[3]/w, bbox[2]/h)ss
            f.write(f'{frame_num} {initBB[0]:.6f} {initBB[1]:.6f} {initBB[2]:.6f} {initBB[3]:.6f}\n')

    cv2.imwrite(image_dir + f'/{frame_num}' + '.jpg', frame)

    cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Frame", 1920, 1080)
    cv2.imshow("Frame", frame)

    ok, frame = video.read()
    frame_num += 1

video.release()
# close all windows
cv2.destroyAllWindows()
