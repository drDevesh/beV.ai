import cv2
import mediapipe as mp
import numpy as np
import pygame
import random
import subprocess

# Initialize Mediapipe hands module
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils  # For drawing landmarks and connections

# Initialize Pygame and load drum sounds
pygame.init()
drum1_sound = pygame.mixer.Sound('mixkit-drum-joke-accent-579.wav')
drum2_sound = pygame.mixer.Sound('mixkit-short-bass-hit-2299.wav')
drum3_sound = pygame.mixer.Sound('mixkit-tribal-dry-drum-558.wav')
drum4_sound = pygame.mixer.Sound('mixkit-tribal-dry-drum-558.wav')  # New sound
drum5_sound = pygame.mixer.Sound('mixkit-heavy-sword-hit-2794.wav')  # New sound

# Function to play a drum sound
def play_drum(drum_sound):
    pygame.mixer.Sound.play(drum_sound)

# OpenCV video capture
cap = cv2.VideoCapture(0)

# Define drum zones as circles: (center_x, center_y, radius)
drum1_zone = (175, 175, 75)  # x, y, radius
drum2_zone = (375, 175, 75)
drum3_zone = (575, 175, 75)
drum4_zone = (175, 375, 75)  # Additional drum
drum5_zone = (375, 375, 75)  # Additional drum

# Define the exit button area (top-left corner)
exit_button_zone = (75, 75, 50)  # x, y, radius for the exit button

# Initial background color
bg_color = (0, 0, 0)

# Create a named window and set it to full screen
cv2.namedWindow('Virtual Drum Kit', cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty('Virtual Drum Kit', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

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

        # Set the background color of the frame
        frame[:] = bg_color

        # Draw drum zones as circles
        cv2.circle(frame, (drum1_zone[0], drum1_zone[1]), drum1_zone[2], (0, 0, 255), 2)
        cv2.circle(frame, (drum2_zone[0], drum2_zone[1]), drum2_zone[2], (0, 255, 0), 2)
        cv2.circle(frame, (drum3_zone[0], drum3_zone[1]), drum3_zone[2], (255, 0, 0), 2)
        cv2.circle(frame, (drum4_zone[0], drum4_zone[1]), drum4_zone[2], (255, 255, 0), 2)  # Yellow for new drum
        cv2.circle(frame, (drum5_zone[0], drum5_zone[1]), drum5_zone[2], (0, 255, 255), 2)  # Cyan for new drum

        # Draw exit button in top-left corner
        cv2.circle(frame, (exit_button_zone[0], exit_button_zone[1]), exit_button_zone[2], (255, 255, 255), -1)  # White exit button
        cv2.putText(frame, 'Exit', (exit_button_zone[0] - 25, exit_button_zone[1] + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        # If hand landmarks are detected
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks and connections (lines) on the frame
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get coordinates of the tip of the index finger
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                h, w, _ = frame.shape
                finger_x, finger_y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)

                # Check if the finger is in any of the drum zones (circle area detection)
                def is_inside_circle(zone, x, y):
                    return np.sqrt((x - zone[0]) ** 2 + (y - zone[1]) ** 2) < zone[2]

                # Drum 1
                if is_inside_circle(drum1_zone, finger_x, finger_y):
                    play_drum(drum1_sound)
                    bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Change background color randomly

                # Drum 2
                elif is_inside_circle(drum2_zone, finger_x, finger_y):
                    play_drum(drum2_sound)
                    bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

                # Drum 3
                elif is_inside_circle(drum3_zone, finger_x, finger_y):
                    play_drum(drum3_sound)
                    bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

                # Drum 4 (New)
                elif is_inside_circle(drum4_zone, finger_x, finger_y):
                    play_drum(drum4_sound)
                    bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

                # Drum 5 (New)
                elif is_inside_circle(drum5_zone, finger_x, finger_y):
                    play_drum(drum5_sound)
                    bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

                # Exit button
                elif is_inside_circle(exit_button_zone, finger_x, finger_y):
                    print("Exit button clicked. Returning to control center.")
                    # Close the game and return to control center
                    cap.release()
                    cv2.destroyAllWindows()
                    pygame.quit()
                    subprocess.Popen([r"C:\gest\venv\Scripts\python.exe", "controlcentre.py"])
                    exit()  # Close the current session

        # Display the frame
        cv2.imshow('Virtual Drum Kit', frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
pygame.quit()
