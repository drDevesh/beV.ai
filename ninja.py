import pygame
import cv2
import mediapipe as mp
import random
import math
import os

# Initialize pygame
pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)  # Fullscreen mode
clock = pygame.time.Clock()

# Game variables
fruit_radius = 30
fruits = []
bombs = []
fruit_velocity = 5
score = 0
game_over = False
bomb_chance = 0.02  # Probability of a bomb appearing

# Button variables
button_font = pygame.font.Font(None, 36)
button_color = (255, 255, 255)
restart_button = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 50, 200, 50)
exit_button = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 150, 200, 50)

# Initialize Mediapipe for hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Open the webcam
cap = cv2.VideoCapture(0)

# Define fruit colors
fruit_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # Red, Green, Blue, Yellow
bomb_color = (255, 0, 0)  # Only the bomb will be red

def create_fruit():
    """Generate a new fruit with random position and velocity."""
    x = random.randint(fruit_radius, screen_width - fruit_radius)
    y = screen_height + fruit_radius  # Start off-screen
    return {"x": x, "y": y, "color": random.choice(fruit_colors), "velocity": fruit_velocity}

def create_bomb():
    """Generate a new bomb."""
    x = random.randint(fruit_radius, screen_width - fruit_radius)
    y = screen_height + fruit_radius  # Start off-screen
    return {"x": x, "y": y, "color": bomb_color, "velocity": fruit_velocity}

def draw_objects(objects):
    """Draw the fruits or bombs (colored balls) on the screen."""
    for obj in objects:
        pygame.draw.circle(screen, obj["color"], (obj["x"], obj["y"]), fruit_radius)

def move_objects(objects):
    """Move fruits and bombs down the screen."""
    for obj in objects:
        obj["y"] -= obj["velocity"]

def detect_collision(obj, hand_x, hand_y):
    """Check if a fruit or bomb is sliced by the hand gesture."""
    distance = math.sqrt((obj["x"] - hand_x) ** 2 + (obj["y"] - hand_y) ** 2)
    return distance < fruit_radius

def detect_button_collision(button, hand_x, hand_y):
    """Check if hand gesture is over a button."""
    return button.collidepoint(hand_x, hand_y)

def draw_button(text, rect):
    """Draw a button on the screen."""
    pygame.draw.rect(screen, button_color, rect)
    button_text = button_font.render(text, True, (0, 0, 0))
    screen.blit(button_text, (rect.x + (rect.width - button_text.get_width()) // 2,
                             rect.y + (rect.height - button_text.get_height()) // 2))

def game_over_screen(hand_x=None, hand_y=None):
    """Display game over message, score, and buttons."""
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 74)
    game_over_text = font.render("Game Over!", True, (255, 255, 255))
    score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
    screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2,
                                 screen_height // 2 - 50))
    screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2,
                             screen_height // 2 + 50))

    # Draw restart and exit buttons
    draw_button("Restart", restart_button)
    draw_button("Exit", exit_button)

    # Draw hand tracking pointer (circle) if hand is detected
    if hand_x is not None and hand_y is not None:
        pygame.draw.circle(screen, (255, 255, 255), (hand_x, hand_y), 10)  # White circle as pointer

        # Check for hand collision with the buttons
        if detect_button_collision(restart_button, hand_x, hand_y):
            main_game()  # Restart the game if hand touches the restart button

        if detect_button_collision(exit_button, hand_x, hand_y):
            pygame.quit()
            cap.release()
            cv2.destroyAllWindows()
            os.system('python controlcentre.py')  # Run the controlcenter.py script
            exit()

    pygame.display.update()

def draw_text(text, font, color, x, y):
    """Render text at a specific position on the screen."""
    rendered_text = font.render(text, True, color)
    screen.blit(rendered_text, (x, y))

# Main game loop
def main_game():
    global fruits, bombs, score, game_over
    fruits = []
    bombs = []
    score = 0
    game_over = False
    hello_world_font = pygame.font.Font(None, 36)  # Font for the "Hello World" text

    while True:
        screen.fill((0, 0, 0))

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Capture frame from webcam
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Flip the frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        hand_x, hand_y = None, None
        if results.multi_hand_landmarks:
            # Get hand landmarks
            hand_landmarks = results.multi_hand_landmarks[0]
            index_tip = hand_landmarks.landmark[8]  # Index finger tip landmark

            # Convert hand position to pygame window coordinates
            hand_x = int(index_tip.x * screen_width)
            hand_y = int(index_tip.y * screen_height)

            # Draw the hand tracking pointer (white circle)
            pygame.draw.circle(screen, (255, 255, 255), (hand_x, hand_y), 10)

        # If game over, show game over screen
        if game_over:
            game_over_screen(hand_x, hand_y)
            continue

        # Add new fruits and bombs periodically
        if random.random() < 0.02:  # Add a new fruit with a 2% chance every frame
            fruits.append(create_fruit())

        if random.random() < bomb_chance:  # Add a new bomb with a specified probability
            bombs.append(create_bomb())

        # Move fruits and bombs
        move_objects(fruits)
        move_objects(bombs)

        # Check if any fruit is cut by hand gesture
        if hand_x is not None and hand_y is not None:
            for fruit in fruits[:]:
                if detect_collision(fruit, hand_x, hand_y):
                    fruits.remove(fruit)  # Remove the fruit
                    score += 1  # Increase score

            for bomb in bombs[:]:
                if detect_collision(bomb, hand_x, hand_y):
                    game_over = True  # End the game if the bomb is touched
                    bombs.remove(bomb)

        # Remove fruits and bombs that fall off the screen
        fruits = [fruit for fruit in fruits if fruit["y"] > -fruit_radius]
        bombs = [bomb for bomb in bombs if bomb["y"] > -fruit_radius]

        # Draw fruits and bombs
        draw_objects(fruits)
        draw_objects(bombs)

        # Display score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        # Draw "Hello World" text in the top right corner
        draw_text("if you hit the red circle you need to restart", hello_world_font, (255, 255, 255), screen_width - 100, 10)

        # Game over condition (if all fruits are cut or fall)
        if len(fruits) == 0 and len(bombs) == 0 and score > 0:
            game_over = True

        # Update the display
        pygame.display.update()
        clock.tick(30)

# Start the game
main_game()

# Cleanup
cap.release()
cv2.destroyAllWindows()
pygame.quit()
