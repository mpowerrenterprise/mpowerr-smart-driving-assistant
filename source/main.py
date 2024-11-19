import cv2
import mediapipe as mp
import time
from scipy.spatial import distance as dist
import pygame
import matplotlib.pyplot as plt
from pyfirmata import Arduino
import threading

# Constants
EAR_THRESHOLD = 0.3
CONSECUTIVE_FRAMES = 20
SERVO_ANGLES = [180, 0]

# Initialize MediaPipe FaceMesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5)

# Eye landmarks (left and right)
LEFT_EYE_POINTS = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_POINTS = [362, 385, 387, 263, 373, 380]

# Initialize variables
frame_counter = 0
alarm_on = False

# Initialize pygame mixer for sound playback
pygame.mixer.init()

# Connect to Arduino
board = Arduino('COM6')  # Change if necessary
pin_13 = board.get_pin('d:13:o')  # Pin 13 (LED)
servo_pin = board.get_pin('d:9:s')  # Pin 9 (Servo)
servo_pin.write(180)

# Functions for drowsiness detection
def eye_aspect_ratio(eye):
    """Calculate the Eye Aspect Ratio (EAR)."""
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def play_alarm_sound():
    """Play the alarm sound in a separate thread."""
    pygame.mixer.music.load(r"C:/Users/Nithushan Mohan/Desktop/safe_driving_system/source/Audio-Files/audio.mp3")
    pygame.mixer.music.play()

def start_alarm_sound_thread():
    """Start the alarm sound in a new thread."""
    alarm_thread = threading.Thread(target=play_alarm_sound)
    alarm_thread.start()

def blink_led():
    """Blink the LED 10 times."""
    for _ in range(10):
        pin_13.write(1)  # Turn LED on
        time.sleep(1)
        pin_13.write(0)  # Turn LED off
        time.sleep(1)

def move_servo():
    """Move the servo motor between angles."""
    servo_pin.write(180)
    time.sleep(1)
    servo_pin.write(0)
    time.sleep(8)
    servo_pin.write(180)

def start_blink_led_and_servo():
    """Start LED blinking and servo movement in separate threads."""
    led_thread = threading.Thread(target=blink_led)
    servo_thread = threading.Thread(target=move_servo)
    led_thread.start()
    servo_thread.start()

def display_alert(frame):
    """Display drowsiness alert on the frame."""
    cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

def process_frame(frame):
    """Process each frame to detect drowsiness."""
    global frame_counter, alarm_on

    # Convert frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Extract eye landmarks
            left_eye = [(int(face_landmarks.landmark[i].x * frame.shape[1]),
                         int(face_landmarks.landmark[i].y * frame.shape[0])) for i in LEFT_EYE_POINTS]
            right_eye = [(int(face_landmarks.landmark[i].x * frame.shape[1]),
                          int(face_landmarks.landmark[i].y * frame.shape[0])) for i in RIGHT_EYE_POINTS]

            # Calculate EAR for both eyes
            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)
            ear = (left_ear + right_ear) / 2.0

            # Check if EAR is below threshold
            if ear < EAR_THRESHOLD:
                frame_counter += 1
                if frame_counter >= CONSECUTIVE_FRAMES and not alarm_on:
                    alarm_on = True
                    print("Drowsiness detected! Triggering alarm.")
                    start_alarm_sound_thread()  # Start sound in new thread
                    start_blink_led_and_servo()  # Start LED and servo in separate threads

                    # Display alert on frame
                    display_alert(frame)
            else:
                frame_counter = 0
                alarm_on = False

            # Draw eye landmarks on the frame
            for (x, y) in left_eye + right_eye:
                cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)

    return frame

def main():
    """Main loop for drowsiness detection."""
    # Start video capture
    cap = cv2.VideoCapture(1)
    
    # Initialize Matplotlib for displaying frames
    plt.ion()
    fig, ax = plt.subplots()

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        
        # Process the frame
        frame = process_frame(frame)

        # Display frame using Matplotlib
        ax.clear()  # Clear previous frame
        ax.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  # Display current frame
        ax.axis('off')  # Hide axes for clean display
        plt.pause(0.01)  # Pause to update the plot

    # Release resources
    cap.release()
    plt.close()
    board.exit()  # Close Arduino connection

if __name__ == "__main__":
    main()
