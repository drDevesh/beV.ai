import pygame
import random
import cv2
import mediapipe as mp

# Initialize pygame for the Snake game
pygame.init()

# Set up screen dimensions for the snake game
screen_width = 600
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Snake Game with Hand Gestures')

# Set up colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Set up snake variables
snake_size = 20
snake_body = [(100, 50), (90, 50), (80, 50)]  # Initial snake position
snake_direction = "RIGHT"  # Initial direction
speed = 15  # Snake speed
score = 0

# Set up food variables
food_pos = [random.randrange(1, screen_width // snake_size) * snake_size,
            random.randrange(1, screen_height // snake_size) * snake_size]
food_spawn = True

# Set up the clock for frame rate control
clock = pygame.time.Clock()

# Set up font for score display
font = pygame.font.SysFont("times new roman", 35)

# Initialize Mediapipe hand detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)
mp_draw = mp.solutions.drawing_utils

# Set up the webcam for hand tracking
cap = cv2.VideoCapture(0)

# Function to display the score
def show_score(choice, color, font, size):
    score_text = font.render("Score: " + str(score), True, color)
    screen.blit(score_text, (0, 0))

# Function to draw the snake
def draw_snake(snake_body):
    for block in snake_body:
        pygame.draw.rect(screen, GREEN, pygame.Rect(block[0], block[1], snake_size, snake_size))

# Function to move the snake based on hand movement
def move_snake(snake_body, new_head):
    snake_body.insert(0, new_head)
    snake_body.pop()

# Game loop
running = True
snake_moving = False  # Snake should not move until hand is detected

while running:
    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # OpenCV - Hand tracking logic
    success, img = cap.read()
    if not success:
        print("Failed to capture image.")
        break

    # Flip the image horizontally for better user experience
    img = cv2.flip(img, 1)

    # Convert the image to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Process the image to detect hand landmarks
    results = hands.process(img_rgb)

    # Check if any hand is detected
    if results.multi_hand_landmarks:
        # Get landmarks for the first hand detected
        landmarks = results.multi_hand_landmarks[0].landmark

        # Get the tip of the index finger (landmark 8)
        index_tip = landmarks[8]

        # Map the index finger position to the Pygame screen dimensions
        index_x, index_y = int(index_tip.x * screen_width), int(index_tip.y * screen_height)

        # Set snake head's position to hand's position
        new_head = (index_x, index_y)

        # If snake hasn't started moving, enable movement
        if not snake_moving:
            snake_moving = True

        # Move the snake if hand is detected
        if snake_moving:
            move_snake(snake_body, new_head)

    # Fill the background with white
    screen.fill(WHITE)

    # Draw the snake
    draw_snake(snake_body)

    # Draw the food
    pygame.draw.rect(screen, RED, pygame.Rect(food_pos[0], food_pos[1], snake_size, snake_size))

    # Check if snake head is at the food position (snake eats the food)
    if snake_body[0] == tuple(food_pos):
        score += 10
        # Generate new food
        food_pos = [random.randrange(1, screen_width // snake_size) * snake_size,
                    random.randrange(1, screen_height // snake_size) * snake_size]
        # Add a new block to the snake's body (snake grows)
        snake_body.append(snake_body[-1])

    # Display the score
    show_score(1, BLACK, font, 20)

    # Update the Pygame display
    pygame.display.update()

    # Control the speed of the snake
    clock.tick(speed)

cap.release()
cv2.destroyAllWindows()
pygame.quit()
