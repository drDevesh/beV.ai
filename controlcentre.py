import cv2
import mediapipe as mp
import pyautogui
import subprocess
import time

# Initialize mediapipe hand detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)
mp_draw = mp.solutions.drawing_utils

# Set up the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Cannot open webcam")
    exit()

# Screen width and height (for mouse movement bounds)
screen_width, screen_height = pyautogui.size()

# Set the desired window width and height
window_width, window_height = screen_width, screen_height  # Set to full screen dimensions

# Create some buttons on the display
buttons = [
    {"label": "Flappy Bird", "x": 200, "y": 100, "w": 200, "h": 60},
    {"label": "Ninja Game", "x": 200, "y": 200, "w": 200, "h": 50},
    {"label": "Virtual Drum", "x": 200, "y": 300, "w": 200, "h": 50},
    {"label": "Music Player", "x": 200, "y": 400, "w": 200, "h": 50},
    {"label": "Whiteboard", "x": 200, "y": 500, "w": 200, "h": 50},
    {"label": "Exit", "x": 200, "y": 600, "w": 200, "h": 50},
]

def is_button_clicked(x, y, button):
    """Check if hand position is within the button's area."""
    return button["x"] < x < button["x"] + button["w"] and button["y"] < y < button["y"] + button["h"]

# Function to start the Flappy Bird game
def start_flappy_game():
    try:
        print("Starting Flappy Bird game...")
        cap.release()
        cv2.destroyAllWindows()
        subprocess.Popen([r"C:\gest\venv\Scripts\python.exe", "flappygame.py"])
    except Exception as e:
        print(f"Error launching Flappy Bird game: {e}")

# Function to start the Ninja Game
def start_ninja_game():
    try:
        print("Starting Ninja game...")
        cap.release()
        cv2.destroyAllWindows()
        subprocess.Popen([r"C:\gest\venv\Scripts\python.exe", "ninja.py"])
    except Exception as e:
        print(f"Error launching Ninja game: {e}")

# Function to start the Virtual Drum
def start_virtual_drum():
    try:
        print("Starting Virtual Drum...")
        cap.release()
        cv2.destroyAllWindows()
        subprocess.Popen([r"C:\gest\venv\Scripts\python.exe", "virtualdrum.py"])
    except Exception as e:
        print(f"Error launching Virtual Drum: {e}")

# Function to start the Music Player
def start_music_player():
    try:
        print("Starting Music Player...")
        cap.release()
        cv2.destroyAllWindows()
        subprocess.Popen([r"C:\gest\venv\Scripts\python.exe", "musicplayer.py"])
    except Exception as e:
        print(f"Error launching Music Player: {e}")

# Function to start the Whiteboard
def start_whiteboard():
    try:
        print("Starting Whiteboard...")
        cap.release()
        cv2.destroyAllWindows()
        subprocess.Popen([r"C:\gest\venv\Scripts\python.exe", "whiteboard.py"])
    except Exception as e:
        print(f"Error launching Whiteboard: {e}")

# Timer for displaying the welcome message
start_time = time.time()
welcome_message_duration = 5  # Display "Welcome to Berry.ai" for 5 seconds

try:
    # Set up the display window in full screen mode
    cv2.namedWindow("Virtual Mouse", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Virtual Mouse", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while cap.isOpened():
        success, img = cap.read()
        if not success or img is None:
            print("Failed to capture image.")
            break

        # Resize the captured frame to the full screen size
        img = cv2.resize(img, (window_width, window_height))
        
        # Flip the image horizontally for better user experience
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
                        (int(window_width / 2 - 300), int(window_height / 2)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)
        else:
            if results.multi_hand_landmarks:
                # Get landmarks for the first hand detected
                landmarks = results.multi_hand_landmarks[0].landmark
                
                # Get the tip of the index finger (landmark 8)
                index_tip = landmarks[8]
                
                # Calculate the position of the index finger
                index_x, index_y = int(index_tip.x * window_width), int(index_tip.y * window_height)

                # Move the mouse based on the position of the index finger
                pyautogui.moveTo(index_x, index_y)

                # Draw landmarks and connections
                mp_draw.draw_landmarks(img, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)

                # Check if any button is clicked
                for button in buttons:
                    if is_button_clicked(index_x, index_y, button):
                        print(f"Button '{button['label']}' clicked!")
                        
                        # Perform action based on the button clicked
                        if button["label"] == "Flappy Bird":
                            start_flappy_game()
                            break
                        elif button["label"] == "Ninja Game":
                            start_ninja_game()
                            break
                        elif button["label"] == "Virtual Drum":
                            start_virtual_drum()
                            break
                        elif button["label"] == "Music Player":
                            start_music_player()
                            break
                        elif button["label"] == "Whiteboard":
                            start_whiteboard()
                            break
                        elif button["label"] == "Exit":
                            print("Exiting the application...")
                            cap.release()
                            cv2.destroyAllWindows()
                            exit()  # Exit the program cleanly

                    # Draw the buttons on the screen
                    cv2.rectangle(img, (button["x"], button["y"]), 
                                  (button["x"] + button["w"], button["y"] + button["h"]), 
                                  (0, 255, 0), 3)
                    cv2.putText(img, button["label"], 
                                (button["x"] + 10, button["y"] + 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            else:
                # If no hand is detected, display the alert after welcome message duration
                cv2.putText(img, "please get your hands in the cameras sight!!", 
                            (int(window_width / 2 - 300), int(window_height / 2)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

        # Display the frame with the hand tracking and buttons
        cv2.imshow("Virtual Mouse", img)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    cap.release()
    cv2.destroyAllWindows()
