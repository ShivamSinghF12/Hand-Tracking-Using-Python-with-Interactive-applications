import cv2
import mediapipe as mp
import numpy as np
import math
import time
import random 
import pygame
import os
import sys

# Initializing MediaPipe, OpenCV utilities
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils
# Inititalizing Pygame
pygame.init()
pygame.mixer.init()


# Open the webcam with a higher resolution
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Create a blank canvas for drawing (real time drawing because the frame froze before when drawing)
frame_height = 720
frame_width = 1280
canvas = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)


#Funtion for resource pathing of sound and image file for executable
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

# Access images
pencil_image_path = resource_path(r"C:\Users\shiva\OneDrive\Desktop\HANDTRACKER\images/pencil.png")#r for raw string
eraser_image_path = resource_path(r"C:\Users\shiva\OneDrive\Desktop\HANDTRACKER\images/eraser.png")

# Access sounds
sound1_path = resource_path(r"C:\Users\shiva\OneDrive\Desktop\HANDTRACKER\sounds/DO.wav")
sound2_path = resource_path(r"C:\Users\shiva\OneDrive\Desktop\HANDTRACKER\sounds/RE.wav")
sound3_path = resource_path(r"C:\Users\shiva\OneDrive\Desktop\HANDTRACKER\sounds/MI.wav")
sound4_path = resource_path(r"C:\Users\shiva\OneDrive\Desktop\HANDTRACKER\sounds/FA.wav")
sound5_path = resource_path(r"C:\Users\shiva\OneDrive\Desktop\HANDTRACKER\sounds/SOL.wav")
sound6_path = resource_path(r"C:\Users\shiva\OneDrive\Desktop\HANDTRACKER\sounds/LA.wav")
sound7_path = resource_path(r"C:\Users\shiva\OneDrive\Desktop\HANDTRACKER\sounds/TI.wav")
                         
             # VARIABLES DECLARATION SECTION 

# PIANO VARIABLES AND SOUND FILES
    # Load piano sounds
keys = {
    "C": pygame.mixer.Sound(sound1_path),
    "D": pygame.mixer.Sound(sound2_path),
    "E": pygame.mixer.Sound(sound3_path),
    "F": pygame.mixer.Sound(sound4_path),
    "G": pygame.mixer.Sound(sound5_path),
    "A": pygame.mixer.Sound(sound6_path),
    "B": pygame.mixer.Sound(sound7_path)
}

# Define piano keys as screen sections
num_keys = len(keys)
key_width = frame_width // num_keys
key_height = 100  # Height of each piano key 
key_y_pos = frame_height // 2  # Center the keys vertically
key_names = list(keys.keys())
key_played = [False] * num_keys  # Track whether a note is currently playing

# Button variables
piano_start_button_pos = (frame_width - 220, 500)
piano_close_button_pos = (frame_width- 220 , 600)
piano_toggle_button_size = (170, 60)
piano_active = False  # Flag to manage piano mode state
 
# GAME VARIABLES 
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
score = 0
mole_radius = 40
mole_image_path = resource_path(r"C:\Users\shiva\OneDrive\Desktop\HANDTRACKER\images/mole.png")  
mole_image = cv2.imread(mole_image_path, cv2.IMREAD_UNCHANGED)  
mole_image = cv2.resize(mole_image, (mole_radius * 2, mole_radius * 2))
mole_pos = (random.randint(mole_radius, frame_width - mole_radius), random.randint(100, frame_height - mole_radius))
last_mole_time = time.time()
mole_interval = 1.5  # Time interval in seconds between mole appearances

# Start Button variables
# Loading the Start Button image
start_button_image_path = resource_path(r"C:\Users\shiva\OneDrive\Desktop\HANDTRACKER\images/startgame.png") 
start_button_image = cv2.imread(start_button_image_path, cv2.IMREAD_UNCHANGED) 

# Resize the image to match the button size 
button_pos = (1050, 200)  # Button position
button_size = (210, 90)  # Button size (width, height)
start_button_image = cv2.resize(start_button_image, (button_size[0], button_size[1]))
game_active = False  # Flag to track game state
close_button_pos = (1050, 300)
close_button_size = (210, 90)
countdown_active = False  # Flag to manage countdown state
countdown_duration = 3  # Countdown 3..2..1
countdown_start_time = None  # Variable to store the start time of countdown
spawn_x_min, spawn_y_min = 100, 200  # Top-left corner
spawn_x_max, spawn_y_max = 800, 600  #bottom right corner

# DRAWING MODE VARIABLES
# DRAWING ERASING TOGGLE VARIABLES
drawing_mode = False
eraser_mode = False
last_tap_time = 0  # For implementing tap delay (in seconds)
tap_delay_seconds = 0.5  # Set delay to 0.5 seconds (tap delay so that there are not repeated button presses)

# Variables for control panel
control_panel_visible = False  # Track visibility of the control panel
control_panel_x = 0  # X position of the control panel (top)
control_panel_y = 0  # Y position of the control panel (top)
control_panel_width = 1280  # Width of the control panel
control_panel_height = 150  # Height of the control panel (increased for the new button)
button_width = 200  # Width of each button in control panel
button_height = 100  # Height of each button

# Define available colors and button positions
colors = {
    'red': (0, 0, 255),
    'green': (0, 255, 0),
    'blue': (255, 0, 0),
    'yellow': (0, 255, 255),
    'white': (255, 255, 255)
}
selected_color = colors['green']  # Default color for drawing

# Color button positions in the control panel
color_button_positions = {
    'red': (1050, 400),
    'green': (1050, 500),
    'blue': (1050, 600),
    'yellow': (1150, 400),
    'white': (1150, 500)
}
color_button_size = (50, 50)  # Size of color buttons

# images for drawing and eraser icons
drawing_icon = cv2.imread(pencil_image_path) 
eraser_icon = cv2.imread(eraser_image_path)  

# Resizing images to button sizes (Resizing because changing from written text to image)
drawing_icon = cv2.resize(drawing_icon, (button_width, button_height))
eraser_icon = cv2.resize(eraser_icon, (button_width, button_height))


# Buffer to store previous points for smoother lines
drawing_history = []
pinched = False  # Track if the pinch gesture is active

            
        # FUNCTION DEFINITION AREA


# FUNCTIONS FOR DRAWING PANEL
# Function to draw control panel (top)
def draw_control_panel(frame):
    # Draw control panel background
    cv2.rectangle(frame, (control_panel_x, control_panel_y),
                  (control_panel_x + control_panel_width, control_panel_y + control_panel_height), (200, 200, 200), -1)
    cv2.putText(frame, "Control Panel", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    # Draw buttons for different actions
    # Draw "Drawing Mode" button with the image icon
    frame[50:50+button_height, 10:10+button_width] = drawing_icon

    # Draw "Eraser Mode" button with the image icon
    frame[50:50+button_height, 220:220+button_width] = eraser_icon

    cv2.rectangle(frame, (430, 50),
                  (button_width + 430, 50 + button_height), (0, 0, 255), -1)
    cv2.putText(frame, "Clear Canvas", (440, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    cv2.rectangle(frame, (640, 50),
                  (button_width + 640, 50 + button_height), (0, 255, 255), -1)
    cv2.putText(frame, "Save", (650, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    # Add Close Control Panel button
    cv2.rectangle(frame, (850, 50),
                  (button_width + 850, 50 + button_height), (255, 255, 0), -1)
    cv2.putText(frame, "Close Panel", (860, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    for color, pos in color_button_positions.items():
        color_bgr = colors[color]
        cv2.rectangle(frame, pos, (pos[0] + color_button_size[0], pos[1] + color_button_size[1]), color_bgr, -1)
        if selected_color == color_bgr:
            cv2.rectangle(frame, pos, (pos[0] + color_button_size[0], pos[1] + color_button_size[1]), (255, 255, 255), 2)  # Highlight selected color

# Function to draw the "Show Panel" button
def draw_show_panel_button(frame):
    cv2.rectangle(frame, (frame_width - 220, 45),
                  (frame_width - 10, 50 + button_height), (127, 5, 45), -1)
    cv2.putText(frame, "Show Drawing", (frame_width - 200, 90),
                cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 0.8, (255, 145, 200), 2)
    cv2.putText(frame, "Panel", (frame_width - 190, 125),
                cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 0.8, (255, 145, 200), 2)

# Function to smooth the drawing (using line interpolation)
def smooth_drawing(last_point, current_point, canvas):
    # Draw a line between the last and current points (for smoothness)
    cv2.line(canvas, last_point, current_point, selected_color, 10)

# Function to handle the control panel interaction with tap delay
def check_button_click(x, y):
    global drawing_mode, eraser_mode, canvas, control_panel_visible, last_tap_time, selected_color
    current_time = time.time()
    if current_time - last_tap_time > tap_delay_seconds:  # Check if enough time has passed
        last_tap_time = current_time  # Update last tap time
        
        if control_panel_visible:
            # Drawing Mode Button
            if (10 <= x <= button_width + 10 and 50 <= y <= 50 + button_height):
                drawing_mode = True
                eraser_mode = False
                print("Switched to Drawing Mode")
            # Eraser Mode Button
            elif (220 <= x <= button_width + 220 and 50 <= y <= 50 + button_height):
                eraser_mode = True
                drawing_mode = False
                print("Switched to Eraser Mode")
            # Clear Canvas Button
            elif (430 <= x <= button_width + 430 and 50 <= y <= 50 + button_height):
                canvas = np.zeros_like(canvas)  # Clear the canvas
                print("Canvas Cleared")
            # Save Button
            elif (640 <= x <= button_width + 640 and 50 <= y <= 50 + button_height):
                # Ensure `frame_with_canvas` is updated with the latest drawing
                frame_with_canvas = cv2.addWeighted(frame, 1, canvas, 0.5, 0)
                save_path = "drawing.png"  
                cv2.imwrite(save_path, frame_with_canvas)  # Save the combined image
                print(f"Drawing saved to {save_path}")
            # Close Control Panel Button
            elif (850 <= x <= button_width + 850 and 50 <= y <= 50 + button_height):
                control_panel_visible = False  # Hide the control panel
                print("Control Panel Closed")

            for color, pos in color_button_positions.items():
                if (pos[0] <= x <= pos[0] + color_button_size[0]) and (pos[1] <= y <= pos[1] + color_button_size[1]):
                    selected_color = colors[color]
                    print(f"Selected color: {color.capitalize()}")

        else:
            # Show Panel Button (visible when the control panel is not visible)
            if (frame_width - 220 <= x <= frame_width - 10 and 50 <= y <= 50 + button_height):
                control_panel_visible = True  # Show the control panel
                print("Control Panel Opened")

# Function to check if index and thumb are pinched
def check_pinched(hand_landmarks, frame_width, frame_height):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    
    thumb_x, thumb_y = int(thumb_tip.x * frame_width), int(thumb_tip.y * frame_height)
    index_x, index_y = int(index_tip.x * frame_width), int(index_tip.y * frame_height)

    # Calculate Euclidean distance between thumb tip and index finger tip
    distance = math.sqrt((index_x - thumb_x) ** 2 + (index_y - thumb_y) ** 2)
    return distance < 40  # Return True if pinch distance is less than threshold
                
    
            #FUNCTIONS FOR WHACK A MOLE

# Function to check if index finger is close enough to "whack" the mole
def is_near_object(hand_x, hand_y, obj_x, obj_y, threshold=50):
    distance = math.sqrt((hand_x - obj_x) ** 2 + (hand_y - obj_y) ** 2)
    return distance < threshold

# Function to check if the start button is tapped
def is_button_tapped(hand_x, hand_y, button_x, button_y, button_w, button_h):
    return (button_x <= hand_x <= button_x + button_w) and (button_y <= hand_y <= button_y + button_h)

def close_game_button(hand_x, hand_y, button_x, button_y, button_w, button_h):
    return (button_x <= hand_x <= button_x + button_w) and (button_y <= hand_y <= button_y + button_h)


           #FUNCTIONS FOR SCREEN PIANO 
# Helper function to play a note if a key is touched within the key's region
def play_note_if_touched(hand_x, hand_y):
    if key_y_pos <= hand_y < key_y_pos + key_height:  # Ensure finger is within the vertical range of the keys
        for i in range(num_keys):
            key_x_start = i * key_width
            key_x_end = (i + 1) * key_width
            if key_x_start <= hand_x < key_x_end:
                if not key_played[i]:  # Play only if not already playing
                    keys[key_names[i]].play()
                    key_played[i] = True
                break
        else:
            # Reset keys if no fingers are touching them
            for j in range(num_keys):
                key_played[j] = False
    else:
        # Reset keys if finger is outside the key area
        for j in range(num_keys):
            key_played[j] = False

# Function to check if a button is tapped
def is_button_tapped(hand_x, hand_y, button_x, button_y, button_w, button_h):
    return (button_x <= hand_x <= button_x + button_w) and (button_y <= hand_y <= button_y + button_h)

 
# THE MAIN LOOOP
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # Flip the frame horizontally for a mirror effect
    frame = cv2.flip(frame, 1)

    # Convert BGR to RGB for MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame to detect hands
    results = hands.process(frame_rgb)

    # Display Start Button if the game is not active
    if not game_active:
        if not control_panel_visible:
        # Draw the start button
            # Overlay the Start Button image
            top_left_x, top_left_y = button_pos
            bottom_right_x, bottom_right_y = top_left_x + button_size[0], top_left_y + button_size[1]

            # Ensure image stays within frame boundaries
            if top_left_x >= 0 and top_left_y >= 0 and bottom_right_x <= frame_width and bottom_right_y <= frame_height:
                roi = frame[top_left_y:bottom_right_y, top_left_x:bottom_right_x]  # Region of interest on the frame

            # Handle transparency as the image has an alpha channel
                if start_button_image.shape[2] == 4:  # RGBA image
                    alpha_button = start_button_image[:, :, 3] / 255.0  # Normalize alpha channel
                    alpha_frame = 1.0 - alpha_button

                    for c in range(3):  # Blend RGB channels
                        roi[:, :, c] = (alpha_button * start_button_image[:, :, c] + alpha_frame * roi[:, :, c])
                else:
                # No transparency, directly overlay the button image (if change in future)
                    roi[:, :, :] = start_button_image[:, :, :3]

                # Put the modified ROI back into the frame
                frame[top_left_y:bottom_right_y, top_left_x:bottom_right_x] = roi
        
    # Check for hand landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw hand landmarks on the frame
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get the index and thumb finger tips (needed for pinch gesture)
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

            # Convert landmarks to screen coordinates
            index_x, index_y = int(index_finger_tip.x * frame_width), int(index_finger_tip.y * frame_height)
            thumb_x, thumb_y = int(thumb_finger_tip.x * frame_width), int(thumb_finger_tip.y * frame_height)

#DRAWING PANEL LOGIC
            # Check for pinch and drawing behavior
            if check_pinched(hand_landmarks, frame_width, frame_height):
                if drawing_mode:
                    if len(drawing_history) > 0:
                        last_point = drawing_history[-1]
                        smooth_drawing(last_point, (index_x, index_y), canvas)  # Draw smoothly
                    drawing_history.append((index_x, index_y))
                elif eraser_mode:
                    cv2.circle(canvas, (index_x, index_y), 20, (0, 0, 0), -1)  # Erase

            else:
                # Clear drawing history when unpinched
                if len(drawing_history) > 0:
                    drawing_history.clear()

            # Check for button clicks (tap gesture)
            check_button_click(index_x, index_y)

#GAME LOGIC
            # Start button tapped to initiate the game with countdown
            if not game_active and is_button_tapped(index_x, index_y, button_pos[0], button_pos[1], button_size[0], button_size[1]):
                countdown_active = True
                countdown_start_time = time.time()  # Start countdown timer
                score = 0  # Reset score at game start
                last_mole_time = time.time()  # Reset mole timer
                print("Countdown started...")
            if game_active:
                cv2.putText(frame, "CAN U WHACK THE MOLE, PUT YOUR HAND IN THE BLUE BOX", (frame_height-700,frame_width-1100 ), cv2.FONT_HERSHEY_SIMPLEX, 1, (245, 106, 76), 2)
                cv2.rectangle(frame, (spawn_x_min, spawn_y_min), (spawn_x_max, spawn_y_max), (255, 255, 0), 2)
                # Check if the mole was "whacked"
                if is_near_object(index_x, index_y, mole_pos[0], mole_pos[1]):
                    score += 1  # Increase score
                    print(f"Score: {score}")
                    # Move mole to a new random position immediately upon "whacking"
                    mole_pos = (
                        random.randint(spawn_x_min + mole_radius, spawn_x_max - mole_radius),
                        random.randint(spawn_y_min + mole_radius, spawn_y_max - mole_radius))
                    last_mole_time = time.time()  # Reset mole timer
            
            # Close game button
            if game_active and close_game_button(index_x, index_y, close_button_pos[0], close_button_pos[1], close_button_size[0], close_button_size[1]):
                game_active = False

                        # Check if the start button is tapped to activate the piano
            if not piano_active and is_button_tapped(index_x, index_y, piano_start_button_pos[0], piano_start_button_pos[1], button_size[0], button_size[1]):
                piano_active = True
                print("Piano Mode Activated!")

#PIANO LOGIC
            # Check if the start button is tapped to activate the piano
            if not piano_active and is_button_tapped(index_x, index_y, piano_start_button_pos[0], piano_start_button_pos[1], button_size[0], button_size[1]):
                piano_active = True
                print("Piano Mode Activated!")

            # Check if the close button is tapped to deactivate the piano
            if piano_active and is_button_tapped(index_x, index_y, piano_close_button_pos[0], piano_close_button_pos[1], button_size[0], button_size[1]):
                piano_active = False
                print("Piano Mode Deactivated!")
                # Reset key states
                key_played = [False] * num_keys
            
            if piano_active and is_button_tapped(index_x, index_y, button_pos[0], button_pos[1], button_size[0], button_size[1]):
                cv2.putText(frame, "CLOSE PIANO FIRST!!", (frame_height-700,frame_width-1200 ), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 250), 2)

            # If piano mode is active, check for key interactions
            if piano_active:
                play_note_if_touched(index_x, index_y)

    if control_panel_visible:
        countdown_active = False
        game_active = False
        piano_active = False

    # Show countdown without freezing
    if countdown_active:
        elapsed_time = time.time() - countdown_start_time  # Calculate elapsed time
        countdown_number = countdown_duration - int(elapsed_time)  # Calculate current countdown number

        # Display countdown on screen
        if countdown_number > 0:
            cv2.putText(frame, str(countdown_number), (frame_width // 2 - 50, frame_height // 2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 0, 0), 10, cv2.LINE_AA)
        else:
            # Show "GO!" briefly
            cv2.putText(frame, "GO!", (frame_width // 2 - 100, frame_height // 2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 10, cv2.LINE_AA)

            # Countdown finished, start game
            game_active = True
            countdown_active = False  # Reset countdown flag
            print("Game Started!")
                    

    # If the game is active, show the mole and update the score
    if game_active:
        # Display the mole (drawn as a red circle) on the frame
        #cv2.circle(frame, mole_pos, mole_radius, (0, 0, 255), -1)
        mole_x, mole_y = mole_pos  # Extract x, y coordinates
        top_left_x = mole_x - mole_radius
        top_left_y = mole_y - mole_radius

        # Ensure the mole image stays within frame boundaries
        if top_left_x >= 0 and top_left_y >= 0 and top_left_x + mole_image.shape[1] <= frame_width and top_left_y + mole_image.shape[0] <= frame_height:
        # Extract region of interest (ROI) from the frame
            roi = frame[top_left_y:top_left_y + mole_image.shape[0], top_left_x:top_left_x + mole_image.shape[1]]

         # Handle transparency as the mole image has an alpha channel
            if mole_image.shape[2] == 4:  # RGBA image
                alpha_mole = mole_image[:, :, 3] / 255.0  # Normalize alpha channel
                alpha_frame = 1.0 - alpha_mole

                for c in range(3):  # Loop over RGB channels
                    roi[:, :, c] = (alpha_mole * mole_image[:, :, c] + alpha_frame * roi[:, :, c])
            else:
                # No alpha channel, simply replace the ROI
                roi[:, :, :] = mole_image[:, :, :3]

            # Put the modified ROI back into the frame
            frame[top_left_y:top_left_y + mole_image.shape[0], top_left_x:top_left_x + mole_image.shape[1]] = roi

        # Display the score on the screen
        cv2.putText(frame, f"Score: {score}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Check if enough time has passed to move the mole to a new position
        if time.time() - last_mole_time > mole_interval:
            mole_pos = (random.randint(spawn_x_min + mole_radius, spawn_x_max - mole_radius),
                        random.randint(spawn_y_min + mole_radius, spawn_y_max - mole_radius)
                        )
            last_mole_time = time.time()

        # Display the Close Game button
        cv2.rectangle(frame, close_button_pos, (close_button_pos[0] + close_button_size[0], close_button_pos[1] + close_button_size[1]), (0, 0, 255), -1)
        cv2.putText(frame, "Close Game", (close_button_pos[0] + 10, close_button_pos[1] + 55), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Show the control panel or the show panel button
    if not game_active and not piano_active :
        if control_panel_visible:
            draw_control_panel(frame)
        else:
            draw_show_panel_button(frame)

    #Hiding other feature buttons when 1 feature is active
    # Reset the canvas when the game is active
    if game_active :
        piano_active = False
        control_panel_visible = False  
        canvas = np.zeros_like(canvas)
    #Reset the canvas when piano is active    
    if piano_active :
        countdown_active = False
        game_active = False
        control_panel_visible = False
        canvas = np.zeros_like(canvas)

    # Display the piano keys if piano mode is active
    if piano_active:
        # Draw piano keys on the frame
        for i in range(num_keys):
            key_x_start = i * key_width
            key_x_end = (i + 1) * key_width
            color = (255, 255, 255) if not key_played[i] else (200, 200, 200)  # Lighten color when pressed
            cv2.rectangle(frame, (key_x_start, key_y_pos), (key_x_end, key_y_pos + key_height), color, -1)
            cv2.putText(frame, key_names[i], (key_x_start + 20, key_y_pos + key_height - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        # Draw the "Close Piano" button
        cv2.rectangle(frame, piano_close_button_pos, (piano_close_button_pos[0] + piano_toggle_button_size[0], piano_close_button_pos[1] + piano_toggle_button_size[1]), (0, 0, 255), -1)
        cv2.putText(frame, "Close Piano", (piano_close_button_pos[0] + 10, piano_close_button_pos[1] + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    else:
        if not control_panel_visible: # only draw start piano when control panel is not visible so that it doesnt interfere 
            # Draw the "Start Piano" button
            cv2.rectangle(frame, piano_start_button_pos, (piano_start_button_pos[0] + piano_toggle_button_size[0], piano_start_button_pos[1] + piano_toggle_button_size[1]), (0, 255, 0), -1)
            cv2.putText(frame, "Start Piano", (piano_start_button_pos[0] + 10, piano_start_button_pos[1] + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Combine the canvas with the frame
    frame_with_canvas = cv2.addWeighted(frame, 1, canvas, 0.5, 0)

    # Display the frame with the drawing and hand tracking
    cv2.imshow("Hand Tracking based drawing, game and piano", frame_with_canvas)

    # Exit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'): #if its not closing on tapping q make sure ur capslock is off!
        break

cap.release()
cv2.destroyAllWindows()
pygame.quit()
