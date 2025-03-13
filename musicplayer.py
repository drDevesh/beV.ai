import cv2
import mediapipe as mp
import pygame
import os

# Initialize Mediapipe hands module
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Initialize Pygame and load music files
pygame.mixer.init()

# Define the location of your .mp3 files stored locally in the project directory
songs_directory = r'C:\gest'  # Folder where .mp3 files are stored

# List of available songs
songs = [f for f in os.listdir(songs_directory) if f.endswith('.mp3')]

# If no songs are available in the directory, display an error and exit
if len(songs) == 0:
    print("No songs found in the specified directory!")
    exit()

# Initialize the player state
current_song_index = 0
song_playing = False
volume = 0.5  # Set initial volume to 50%

# Function to play music
def play_music():
    global song_playing
    pygame.mixer.music.load(os.path.join(songs_directory, songs[current_song_index]))
    pygame.mixer.music.set_volume(volume)  # Set volume when playing
    pygame.mixer.music.play()
    song_playing = True

# Function to pause/resume music
def toggle_pause_music():
    global song_playing
    if song_playing:
        pygame.mixer.music.pause()
        song_playing = False
    else:
        pygame.mixer.music.unpause()
        song_playing = True

# Function to play the next song
def next_song():
    global current_song_index
    current_song_index = (current_song_index + 1) % len(songs)
    play_music()

# Function to exit the program and run controlcenter.py
def exit_program():
    global cap
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    print("Exiting program and launching controlcenter.py...")
    os.system('python controlcentre.py')  # Run controlcenter.py
    exit()

# OpenCV video capture
cap = cv2.VideoCapture(0)

# Get screen dimensions for dynamic button placement
screen_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
screen_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Button configuration
button_width = 120
button_height = 120
button_spacing = 20  # Minimal spacing between buttons

# Individual button position adjustment functions

def adjust_play_button_position():
    # Centered horizontally
    play_x = screen_width // 2 - button_width - button_spacing
    play_y = screen_height // 2 - button_height // 2
    return (play_x, play_y, button_width, button_height)

def adjust_pause_button_position():
    # Exactly in the middle
    pause_x = screen_width // 2
    pause_y = screen_height // 2 - button_height // 2
    return (pause_x, pause_y, button_width, button_height)

def adjust_next_button_position():
    # Slightly right of center
    next_x = screen_width // 2 + button_width + button_spacing
    next_y = screen_height // 2 - button_height // 2
    return (next_x, next_y, button_width, button_height)

def adjust_exit_button_position():
    # Top-left corner
    exit_x = 500
    exit_y = 10
    return (exit_x, exit_y, button_width, button_height)

# Volume bar dimensions (moved below the exit button on the left side)
def adjust_volume_bar_position():
    volume_bar_x = 20  # Align with the exit button on the left
    volume_bar_y = adjust_exit_button_position()[1] + button_height + button_spacing  # Below the exit button
    volume_bar_width = 30
    volume_bar_height = 300  # Height for the volume bar
    return (volume_bar_x, volume_bar_y, volume_bar_width, volume_bar_height)

# Hand gestures' thresholds
THUMB_TIP = mp_hands.HandLandmark.THUMB_TIP
INDEX_FINGER_TIP = mp_hands.HandLandmark.INDEX_FINGER_TIP

# Gesture detection functions
def count_fingers(hand_landmarks):
    open_fingers = 0
    for finger_tip in [INDEX_FINGER_TIP]:
        finger = hand_landmarks.landmark[finger_tip]
        if finger.y < hand_landmarks.landmark[THUMB_TIP].y:  # Simple check to determine if the finger is open
            open_fingers += 1
    return open_fingers

# Fullscreen mode
cv2.namedWindow("Music Player with Gestures", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Music Player with Gestures", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Main loop for gesture detection
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

        # Get individual button positions
        play_button = adjust_play_button_position()
        pause_button = adjust_pause_button_position()
        next_button = adjust_next_button_position()
        exit_button = adjust_exit_button_position()
        volume_bar = adjust_volume_bar_position()

        # Draw virtual buttons (play, pause, next, exit) on the screen
        cv2.rectangle(frame, play_button[:2], (play_button[0] + play_button[2], play_button[1] + play_button[3]), (0, 255, 0), 2)
        cv2.putText(frame, "Play", (play_button[0] + 35, play_button[1] + 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.rectangle(frame, pause_button[:2], (pause_button[0] + pause_button[2], pause_button[1] + pause_button[3]), (0, 0, 255), 2)
        cv2.putText(frame, "Pause", (pause_button[0] + 35, pause_button[1] + 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.rectangle(frame, next_button[:2], (next_button[0] + next_button[2], next_button[1] + next_button[3]), (255, 0, 0), 2)
        cv2.putText(frame, "Next", (next_button[0] + 35, next_button[1] + 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Make the Exit button highly visible in the left corner (bright yellow)
        cv2.rectangle(frame, exit_button[:2], (exit_button[0] + exit_button[2], exit_button[1] + exit_button[3]), (0, 255, 255), 2)
        cv2.putText(frame, "Exit", (exit_button[0] + 35, exit_button[1] + 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        # Draw the volume bar below the exit button (left side)
        cv2.rectangle(frame, (volume_bar[0], volume_bar[1]), (volume_bar[0] + volume_bar[2], volume_bar[1] + volume_bar[3]), (128, 128, 128), 2)
        # Fill the volume level based on current volume
        volume_level_y = int(volume_bar[3] * (1 - volume)) + volume_bar[1]
        cv2.rectangle(frame, (volume_bar[0], volume_level_y), (volume_bar[0] + volume_bar[2], volume_bar[1] + volume_bar[3]), (0, 255, 0), -1)

        # Check hand landmarks and gestures
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get the index finger tip position
                index_finger_tip = hand_landmarks.landmark[INDEX_FINGER_TIP]
                h, w, _ = frame.shape
                finger_x, finger_y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)

                # Gesture: If the finger points to the play button
                if play_button[0] < finger_x < play_button[0] + play_button[2] and play_button[1] < finger_y < play_button[1] + play_button[3]:
                    if not song_playing:  # Only play if not already playing
                        play_music()
                        print("Play Gesture Detected")

                # Gesture: If the finger points to the pause button
                elif pause_button[0] < finger_x < pause_button[0] + pause_button[2] and pause_button[1] < finger_y < pause_button[1] + pause_button[3]:
                    toggle_pause_music()
                    print("Pause Gesture Detected")

                # Gesture: If the finger points to the next button
                elif next_button[0] < finger_x < next_button[0] + next_button[2] and next_button[1] < finger_y < next_button[1] + next_button[3]:
                    next_song()
                    print("Next Gesture Detected")

                # Gesture: If the finger points to the exit button
                elif exit_button[0] < finger_x < exit_button[0] + exit_button[2] and exit_button[1] < finger_y < exit_button[1] + exit_button[3]:
                    exit_program()

                # Gesture: Adjust volume if pointing at the volume bar
                if volume_bar[0] < finger_x < volume_bar[0] + volume_bar[2] and volume_bar[1] < finger_y < volume_bar[1] + volume_bar[3]:
                    volume = 1 - (finger_y - volume_bar[1]) / volume_bar[3]
                    volume = max(0, min(volume, 1))  # Ensure volume stays between 0 and 1
                    pygame.mixer.music.set_volume(volume)
                    print(f"Volume adjusted to: {volume * 100:.0f}%")

        # Display the video feed
        cv2.imshow("Music Player with Gestures", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release resources
cap.release()
cv2.destroyAllWindows()
