import cv2 as cv
import mediapipe as mp
import time
import math
import numpy as np
import playsound
import utils as utils
import matplotlib.pyplot as plt  # Import matplotlib for displaying images

# Constants and configuration
CLOSED_EYES_FRAME = 70
FONTS = cv.FONT_HERSHEY_COMPLEX
LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]

# Global variables
frame_counter = 0
CEF_COUNTER = 0

# Initialize MediaPipe FaceMesh
face_mesh = mp.solutions.face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Utility function to detect facial landmarks
def detect_landmarks(img, results, draw=False):
    height, width = img.shape[:2]
    landmarks = [(int(p.x * width), int(p.y * height)) for p in results.multi_face_landmarks[0].landmark]
    if draw:
        for landmark in landmarks:
            cv.circle(img, landmark, 2, (0, 255, 0), -1)
    return landmarks

# Calculate Euclidean distance
def euclidean_distance(point1, point2):
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

# Calculate blink ratio
def blink_ratio(landmarks, right_indices, left_indices):
    rh_distance = euclidean_distance(landmarks[right_indices[0]], landmarks[right_indices[8]])
    rv_distance = euclidean_distance(landmarks[right_indices[12]], landmarks[right_indices[4]])
    lh_distance = euclidean_distance(landmarks[left_indices[0]], landmarks[left_indices[8]])
    lv_distance = euclidean_distance(landmarks[left_indices[12]], landmarks[left_indices[4]])
    return (rh_distance / rv_distance + lh_distance / lv_distance) / 2

# Alarm function
def sound_alarm(file_path):
    playsound.playsound(file_path)

# Main pipeline function
def process_frame(frame):
    global CEF_COUNTER
    frame_resized = cv.resize(frame, None, fx=1.5, fy=1.5)
    rgb_frame = cv.cvtColor(frame_resized, cv.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        landmarks = detect_landmarks(frame_resized, results)
        ratio = blink_ratio(landmarks, RIGHT_EYE, LEFT_EYE)
        
        utils.colorBackgroundText(frame_resized, f'Ratio: {round(ratio, 2)}', FONTS, 0.7, (30, 100), 2, utils.PINK, utils.YELLOW)

        if ratio > 3.5:
            CEF_COUNTER += 1
            utils.colorBackgroundText(frame_resized, str(min(3, CEF_COUNTER // 25)), FONTS, 5, (430, 200), 6, utils.WHITE, utils.RED, pad_x=4, pad_y=6)
            
            if CEF_COUNTER > CLOSED_EYES_FRAME:
                utils.colorBackgroundText(frame_resized, 'Drowsiness Alert...', FONTS, 1.7, (250, 150), 2, utils.YELLOW, pad_x=4, pad_y=6)
                sound_alarm('warning.mp3')
        else:
            CEF_COUNTER = 0
        
        # Draw eye contours
        cv.polylines(frame_resized, [np.array([landmarks[i] for i in LEFT_EYE], np.int32)], True, utils.GREEN, 1, cv.LINE_AA)
        cv.polylines(frame_resized, [np.array([landmarks[i] for i in RIGHT_EYE], np.int32)], True, utils.GREEN, 1, cv.LINE_AA)
    
    return frame_resized

# Main function to capture video and display results
if __name__ == "__main__":
    cap = cv.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        output_frame = process_frame(frame)

        # Convert BGR to RGB for matplotlib
        rgb_output_frame = cv.cvtColor(output_frame, cv.COLOR_BGR2RGB)

        # Display frame using matplotlib
        plt.imshow(rgb_output_frame)
        plt.axis('off')  # Hide axes
        plt.show(block=False)
        plt.pause(0.001)  # Pause to allow the plot to update

    cap.release()
    cv.destroyAllWindows()
