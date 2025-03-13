import cv2
import numpy as np
import mediapipe as mp
import os

# Initialize Mediapipe hands module
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Define color options (palette)
colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255)]  # Red, Green, Blue, Yellow
color_names = ["Red", "Green", "Blue", "Yellow"]
color_buttons = [(10, 10, 50, 50), (70, 10, 50, 50), (130, 10, 50, 50), (190, 10, 50, 50)]  # Button positions
current_color = colors[0]

# Create a blank board to draw on
board = np.ones((600, 800, 3), dtype="uint8") * 255

# Clear board function
def clear_board():
    global board
    board = np.ones((600, 800, 3), dtype="uint8") * 255

# Function to exit and run controlcenter.py
def exit_and_run_control_center():
    print("Exiting and launching controlcentre.py...")
    cap.release()
    cv2.destroyAllWindows()
    os.system('python controlcentre.py')

# OpenCV video capture
cap = cv2.VideoCapture(0)

# Hand gestures' thresholds
INDEX_FINGER_TIP = mp_hands.HandLandmark.INDEX_FINGER_TIP
THUMB_TIP = mp_hands.HandLandmark.THUMB_TIP

# Variables to control drawing
drawing = False
last_point = None

# Fullscreen mode
cv2.namedWindow("Virtual Board", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Virtual Board", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Main loop
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

        # Draw the color palette
        for i, button in enumerate(color_buttons):
            color = colors[i]
            cv2.rectangle(frame, button[:2], (button[0] + button[2], button[1] + button[3]), color, -1)
            cv2.putText(frame, color_names[i], (button[0], button[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Add a clear button
        clear_button = (260, 10, 80, 50)
        cv2.rectangle(frame, clear_button[:2], (clear_button[0] + clear_button[2], clear_button[1] + clear_button[3]), (0, 0, 0), 2)
        cv2.putText(frame, "Clear", (clear_button[0] + 10, clear_button[1] + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        # Add an exit button
        exit_button = (350, 10, 80, 50)
        cv2.rectangle(frame, exit_button[:2], (exit_button[0] + exit_button[2], exit_button[1] + exit_button[3]), (0, 0, 255), 2)
        cv2.putText(frame, "Exit", (exit_button[0] + 15, exit_button[1] + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Process hand landmarks for drawing
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get the index finger tip position
                index_finger_tip = hand_landmarks.landmark[INDEX_FINGER_TIP]
                h, w, _ = frame.shape
                finger_x, finger_y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)

                # Check if the index finger is over any color button to select color
                for i, button in enumerate(color_buttons):
                    if button[0] < finger_x < button[0] + button[2] and button[1] < finger_y < button[1] + button[3]:
                        current_color = colors[i]
                        cv2.rectangle(frame, button[:2], (button[0] + button[2], button[1] + button[3]), (255, 255, 255), 2)

                # Check if the index finger is over the clear button to clear the board
                if clear_button[0] < finger_x < clear_button[0] + clear_button[2] and clear_button[1] < finger_y < clear_button[1] + clear_button[3]:
                    clear_board()

                # Check if the index finger is over the exit button to exit
                if exit_button[0] < finger_x < exit_button[0] + exit_button[2] and exit_button[1] < finger_y < exit_button[1] + exit_button[3]:
                    exit_and_run_control_center()

                # Check if the index finger is raised for drawing
                if hand_landmarks.landmark[INDEX_FINGER_TIP].y < hand_landmarks.landmark[THUMB_TIP].y:
                    if last_point is None:
                        last_point = (finger_x, finger_y)
                    else:
                        cv2.line(board, last_point, (finger_x, finger_y), current_color, 5)
                        last_point = (finger_x, finger_y)
                else:
                    last_point = None

        # Resize the board to match the frame size before combining
        resized_board = cv2.resize(board, (frame.shape[1], frame.shape[0]))

        # Combine the frame and the drawing board
        combined_frame = cv2.addWeighted(frame, 0.5, resized_board, 0.5, 0)

        # Display the frame with the drawing board
        cv2.imshow('Virtual Board', combined_frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
