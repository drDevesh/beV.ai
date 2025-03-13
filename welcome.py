import cv2
import numpy as np
import mediapipe as mp
import os
import subprocess

# Initialize Mediapipe hands module
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Hand gestures' thresholds
INDEX_FINGER_TIP = mp_hands.HandLandmark.INDEX_FINGER_TIP

# OpenCV window setup
cv2.namedWindow("Berry.ai Welcome", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Berry.ai Welcome", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Button positions
get_in_button = (200, 300, 200, 100)  # x, y, width, height
exit_button = (500, 500, 200, 100)    # x, y, width, height

# Function to draw buttons
def draw_buttons(frame):
    # Draw the 'Get In' button
    cv2.rectangle(frame, (get_in_button[0], get_in_button[1]),
                  (get_in_button[0] + get_in_button[2], get_in_button[1] + get_in_button[3]), (0, 255, 0), -1)
    cv2.putText(frame, "Get In", (get_in_button[0] + 40, get_in_button[1] + 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Draw the 'Exit' button
    cv2.rectangle(frame, (exit_button[0], exit_button[1]),
                  (exit_button[0] + exit_button[2], exit_button[1] + exit_button[3]), (0, 0, 255), -1)
    cv2.putText(frame, "Exit", (exit_button[0] + 60, exit_button[1] + 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

# Function to check if a button is clicked by the finger
def is_button_clicked(x, y, button):
    return button[0] < x < button[0] + button[2] and button[1] < y < button[1] + button[3]

# OpenCV video capture
cap = cv2.VideoCapture(0)

# Welcome screen loop
with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame horizontally for a mirror-like effect
        frame = cv2.flip(frame, 1)

        # Convert the frame color to RGB (for Mediapipe)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # Draw the title
        cv2.putText(frame, "Berry.ai", (300, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

        # Draw buttons
        draw_buttons(frame)

        # Process hand landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get the index finger tip position
                index_finger_tip = hand_landmarks.landmark[INDEX_FINGER_TIP]
                h, w, _ = frame.shape
                finger_x, finger_y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)

                # Check if 'Get In' button is clicked
                if is_button_clicked(finger_x, finger_y, get_in_button):
                    cv2.rectangle(frame, (get_in_button[0], get_in_button[1]),
                                  (get_in_button[0] + get_in_button[2], get_in_button[1] + get_in_button[3]), (255, 255, 255), 2)
                    cv2.putText(frame, "Loading...", (350, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.imshow("Berry.ai Welcome", frame)
                    cv2.waitKey(1000)
                    # Run the control centre
                    subprocess.Popen(['python', 'controlcentre.py'])
                    cap.release()
                    cv2.destroyAllWindows()
                    exit()

                # Check if 'Exit' button is clicked
                if is_button_clicked(finger_x, finger_y, exit_button):
                    cv2.rectangle(frame, (exit_button[0], exit_button[1]),
                                  (exit_button[0] + exit_button[2], exit_button[1] + exit_button[3]), (255, 255, 255), 2)
                    cv2.putText(frame, "Exiting...", (350, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.imshow("Berry.ai Welcome", frame)
                    cv2.waitKey(1000)
                    cap.release()
                    cv2.destroyAllWindows()
                    exit()

        # Display the frame
        cv2.imshow('Berry.ai Welcome', frame)

        # Exit on 'q' key press (optional manual exit)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
