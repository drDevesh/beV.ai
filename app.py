import cv2
import mediapipe as mp
import pyautogui
import subprocess
import time
import streamlit as st
import numpy as np

# Set page layout for Streamlit app
st.set_page_config(layout="wide")

# Initialize mediapipe hand detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)
mp_draw = mp.solutions.drawing_utils

# Streamlit placeholders for video and status
video_placeholder = st.empty()
status_placeholder = st.empty()

# Buttons (Streamlit UI)
st.sidebar.title("Gesture-Controlled System")
button_selected = st.sidebar.radio(
    "Choose a program to run:",
    ("Flappy Bird", "Ninja Game", "Virtual Drum", "Music Player", "Whiteboard", "Exit")
)

# Function to start games or applications
def start_application(app_name):
    try:
        if app_name == "Flappy Bird":
            subprocess.Popen([r"C:\gest\venv\Scripts\python.exe", "flappygame.py"])
        elif app_name == "Ninja Game":
            subprocess.Popen([r"C:\gest\venv\Scripts\python.exe", "ninja.py"])
        elif app_name == "Virtual Drum":
            subprocess.Popen([r"C:\gest\venv\Scripts\python.exe", "virtualdrum.py"])
        elif app_name == "Music Player":
            subprocess.Popen([r"C:\gest\venv\Scripts\python.exe", "musicplayer.py"])
        elif app_name == "Whiteboard":
            subprocess.Popen([r"C:\gest\venv\Scripts\python.exe", "whiteboard.py"])
        elif app_name == "Exit":
            st.stop()
    except Exception as e:
        st.error(f"Error launching {app_name}: {e}")

# Check if webcam is available
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    st.error("Error: Cannot open webcam")
    exit()

# Screen dimensions
screen_width, screen_height = pyautogui.size()

# Timer for displaying the welcome message
start_time = time.time()
welcome_message_duration = 5  # Display "Welcome to Berry.ai" for 5 seconds

try:
    while True:
        success, img = cap.read()
        if not success or img is None:
            st.error("Failed to capture image.")
            break

        # Resize and flip the frame
        img = cv2.resize(img, (640, 480))  # Fit the Streamlit window size
        img = cv2.flip(img, 1)

        # Convert the image to RGB (Mediapipe requires RGB)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Process the image for hand landmarks
        results = hands.process(img_rgb)

        # Get the current time
        elapsed_time = time.time() - start_time

        if elapsed_time <= welcome_message_duration:
            # Display "Welcome to Berry.ai" message in the center
            cv2.putText(img, "Welcome to Berry.ai", 
                        (int(640 / 2 - 150), int(480 / 2)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        else:
            if results.multi_hand_landmarks:
                landmarks = results.multi_hand_landmarks[0].landmark

                # Get the tip of the index finger (landmark 8)
                index_tip = landmarks[8]

                # Calculate the position of the index finger
                index_x, index_y = int(index_tip.x * 640), int(index_tip.y * 480)

                # Draw landmarks and connections
                mp_draw.draw_landmarks(img, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)

                # Simulate click detection for each button
                if button_selected == "Flappy Bird":
                    start_application("Flappy Bird")
                elif button_selected == "Ninja Game":
                    start_application("Ninja Game")
                elif button_selected == "Virtual Drum":
                    start_application("Virtual Drum")
                elif button_selected == "Music Player":
                    start_application("Music Player")
                elif button_selected == "Whiteboard":
                    start_application("Whiteboard")
                elif button_selected == "Exit":
                    st.warning("Exiting the application...")
                    cap.release()
                    break

        # Display the frame in the Streamlit app
        video_placeholder.image(img, channels="RGB")

        # Allow users to exit the loop by pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    st.error(f"An error occurred: {e}")

finally:
    cap.release()
    cv2.destroyAllWindows()
