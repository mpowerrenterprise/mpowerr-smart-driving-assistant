import cv2 as cv
import mediapipe as mp
import time
import utils, math
import numpy as np
import playsound

# variables
frame_counter = 0
CEF_COUNTER = 0

# constants
CLOSED_EYES_FRAME = 30
FONTS = cv.FONT_HERSHEY_COMPLEX

# Left eyes indices
LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]

# right eyes indices
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]

map_face_mesh = mp.solutions.face_mesh

# Replace with video file path
camera = cv.VideoCapture('path/to/your/video.mp4')

# landmark detection function
def landmarksDetection(img, results, draw=False):
    img_height, img_width = img.shape[:2]
    mesh_coord = [(int(point.x * img_width), int(point.y * img_height)) for point in results.multi_face_landmarks[0].landmark]
    if draw:
        [cv.circle(img, p, 2, (0, 255, 0), -1) for p in mesh_coord]
    return mesh_coord

# Euclidean distance
def euclideanDistance(point, point1):
    x, y = point
    x1, y1 = point1
    return math.sqrt((x1 - x) ** 2 + (y1 - y) ** 2)

# Blinking Ratio
def blinkRatio(img, landmarks, right_indices, left_indices):
    rh_right, rh_left = landmarks[right_indices[0]], landmarks[right_indices[8]]
    rv_top, rv_bottom = landmarks[right_indices[12]], landmarks[right_indices[4]]
    lh_right, lh_left = landmarks[left_indices[0]], landmarks[left_indices[8]]
    lv_top, lv_bottom = landmarks[left_indices[12]], landmarks[left_indices[4]]
    
    rhDistance = euclideanDistance(rh_right, rh_left)
    rvDistance = euclideanDistance(rv_top, rv_bottom)
    lvDistance = euclideanDistance(lv_top, lv_bottom)
    lhDistance = euclideanDistance(lh_right, lh_left)
    
    reRatio = rhDistance / rvDistance
    leRatio = lhDistance / lvDistance
    return (reRatio + leRatio) / 2

with map_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
    start_time = time.time()
    while True:
        frame_counter += 1
        ret, frame = camera.read()
        if not ret:
            break

        frame = cv.resize(frame, None, fx=1.5, fy=1.5, interpolation=cv.INTER_CUBIC)
        rgb_frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
        results = face_mesh.process(rgb_frame)
        if results.multi_face_landmarks:
            mesh_coords = landmarksDetection(frame, results, False)
            ratio = blinkRatio(frame, mesh_coords, RIGHT_EYE, LEFT_EYE)

            utils.colorBackgroundText(frame, f'Ratio : {round(ratio, 2)}', FONTS, 0.7, (30, 100), 2, utils.PINK, utils.YELLOW)

            if ratio > 5:
                CEF_COUNTER += 1
                if CEF_COUNTER > CLOSED_EYES_FRAME:
                    utils.colorBackgroundText(frame, f'Drowsiness Alert...', FONTS, 1.7, (250, 150), 2, utils.YELLOW, pad_x=4, pad_y=6)
                    playsound.playsound(r'audio.mp3')
            else:
                CEF_COUNTER = 0

            cv.polylines(frame, [np.array([mesh_coords[p] for p in LEFT_EYE], dtype=np.int32)], True, utils.GREEN, 1, cv.LINE_AA)
            cv.polylines(frame, [np.array([mesh_coords[p] for p in RIGHT_EYE], dtype=np.int32)], True, utils.GREEN, 1, cv.LINE_AA)

        end_time = time.time() - start_time
        fps = frame_counter / end_time
        frame = utils.textWithBackground(frame, f'FPS: {round(fps, 1)}', FONTS, 1.0, (30, 50), bgOpacity=0.9, textThickness=2)

        frame = cv.resize(frame, (1280, 720))
        cv.imshow('frame', frame)
        key = cv.waitKey(2)
        if key == ord('q') or key == ord('Q'):
            break

    cv.destroyAllWindows()
    camera.release()
