import cv2
import mediapipe as mp
import numpy as np
import time

# Initialize MediaPipe Hand solution
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

# Camera setup
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Updated keyboard layout
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "[]"]]

finalText = ""

# Click cooldown settings
last_click_time = 0
cooldown_time = 1.0  # 1 second cooldown between clicks
click_registered = False
selected_button = None


class Button():
    def __init__(self, pos, text, size=[50, 50]):
        self.pos = pos
        self.size = size
        self.text = text
        self.is_selected = False
        self.click_time = 0


def drawAll(img, buttonList, specialButtons):
    # Draw regular buttons
    for button in buttonList:
        x, y = button.pos
        w, h = button.size

        # Draw button
        if button.is_selected:
            cv2.rectangle(img, button.pos, (x + w, y + h), (190, 0, 150), cv2.FILLED)
        else:
            cv2.rectangle(img, button.pos, (x + w, y + h), (190, 100, 150), cv2.FILLED)

        # Draw text
        cv2.putText(img, button.text, (x + 9, y + 40),
                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

    # Draw special buttons
    for button in specialButtons:
        x, y = button.pos
        w, h = button.size

        # Draw button
        if button.is_selected:
            cv2.rectangle(img, button.pos, (x + w, y + h), (0, 100, 180), cv2.FILLED)
        else:
            cv2.rectangle(img, button.pos, (x + w, y + h), (0, 150, 180), cv2.FILLED)

        # Draw text - center the text
        text_size = cv2.getTextSize(button.text, cv2.FONT_HERSHEY_PLAIN, 1.5, 2)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2
        cv2.putText(img, button.text, (text_x, text_y),
                    cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)

    return img


# Function to calculate distance between two points
def calculate_distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


# Function to detect if hand is making a fist
def is_fist(hand_landmarks):
    # Get fingertip and pip (middle knuckle) landmarks for all fingers
    fingertips = [8, 12, 16, 20]  # Index, middle, ring, pinky fingertips
    pips = [6, 10, 14, 18]  # Corresponding middle knuckles

    # For a fist, all fingertips should be below their corresponding pips (y-coordinate is larger)
    # Note: MediaPipe uses normalized coordinates (0-1)
    fist_detected = True
    for tip, pip in zip(fingertips, pips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            fist_detected = False
            break

    return fist_detected


# Create regular button list
buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(Button([60 * j + 5, 60 * i + 5], key))

# Create special buttons (positioned below the text display area to avoid overlap)
specialButtons = [
    Button([5, 280], "Backspace", [150, 50]),
    Button([165, 280], "Clear All", [150, 50])
]

# Visual feedback variables
clicking = False
click_start_time = 0
click_animation_duration = 0.5  # Duration of the click animation in seconds

# Main loop
while True:
    success, img = cap.read()
    if not success:
        print("Failed to get frame from camera")
        break

    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Process the image for hand detection
    results = hands.process(img_rgb)

    # Draw buttons
    img = drawAll(img, buttonList, specialButtons)

    # Reset all button selections
    for button in buttonList:
        button.is_selected = False
    for button in specialButtons:
        button.is_selected = False

    current_time = time.time()

    # If hands are detected
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw hand landmarks
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Check if making a fist
            fist_detected = is_fist(hand_landmarks)

            # If making a fist, skip all interaction
            if fist_detected:
                clicking = False
                selected_button = None
                # Visual feedback for fist detection
                cv2.putText(img, "Fist detected - Interaction paused", (10, 470),
                            cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)
                continue

            # Get index finger tip coordinates
            index_finger_tip = hand_landmarks.landmark[8]
            index_x = int(index_finger_tip.x * img.shape[1])
            index_y = int(index_finger_tip.y * img.shape[0])

            # Get middle finger tip coordinates
            middle_finger_tip = hand_landmarks.landmark[12]
            middle_x = int(middle_finger_tip.x * img.shape[1])
            middle_y = int(middle_finger_tip.y * img.shape[0])

            # Calculate distance between index and middle finger
            distance = calculate_distance((index_x, index_y), (middle_x, middle_y))

            # Draw a circle at the index finger tip for visual feedback
            cv2.circle(img, (index_x, index_y), 10, (0, 255, 0), -1)

            # Check if index finger is over any regular button
            for button in buttonList:
                x, y = button.pos
                w, h = button.size

                if x < index_x < x + w and y < index_y < y + h:
                    button.is_selected = True

                    # Click gesture detected (fingers close)
                    if distance < 30:
                        # Start click animation if not already clicking
                        if not clicking:
                            clicking = True
                            click_start_time = current_time
                            selected_button = button
                    else:
                        # If fingers move apart, reset clicking state
                        clicking = False
                        selected_button = None

            # Check if index finger is over any special button
            for button in specialButtons:
                x, y = button.pos
                w, h = button.size

                if x < index_x < x + w and y < index_y < y + h:
                    button.is_selected = True

                    # Click gesture detected (fingers close)
                    if distance < 30:
                        # Start click animation if not already clicking
                        if not clicking:
                            clicking = True
                            click_start_time = current_time
                            selected_button = button
                    else:
                        # If fingers move apart, reset clicking state
                        clicking = False
                        selected_button = None
    else:
        # No hands detected, reset clicking state
        clicking = False
        selected_button = None

    # Handle click animation and registration
    if clicking:
        # Draw progress indicator - fill button gradually
        elapsed = current_time - click_start_time
        if elapsed < click_animation_duration:
            # Button is filling up (visual feedback)
            progress = elapsed / click_animation_duration
            x, y = selected_button.pos
            w, h = selected_button.size

            # Draw progress rectangle
            fill_width = int(w * progress)
            cv2.rectangle(img, (x, y), (x + fill_width, y + h), (0, 255, 0), cv2.FILLED)

            # Draw text
            if selected_button.text in ["Backspace", "Clear All"]:
                text_size = cv2.getTextSize(selected_button.text, cv2.FONT_HERSHEY_PLAIN, 1.5, 2)[0]
                text_x = x + (w - text_size[0]) // 2
                text_y = y + (h + text_size[1]) // 2
                cv2.putText(img, selected_button.text, (text_x, text_y),
                            cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)
            else:
                cv2.putText(img, selected_button.text, (selected_button.pos[0] + 9, selected_button.pos[1] + 40),
                            cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
        else:
            # Click completed
            if selected_button and (current_time - last_click_time) > cooldown_time:
                # Process the button click based on its function
                if selected_button.text == "Backspace":
                    if finalText:  # Only delete if there's text
                        finalText = finalText[:-1]
                elif selected_button.text == "Clear All":
                    finalText = ""  # Clear all text
                else:
                    finalText += selected_button.text

                last_click_time = current_time

                # Visual feedback for successful click
                x, y = selected_button.pos
                w, h = button.size
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), cv2.FILLED)

                if selected_button.text in ["Backspace", "Clear All"]:
                    text_size = cv2.getTextSize(selected_button.text, cv2.FONT_HERSHEY_PLAIN, 1.5, 2)[0]
                    text_x = x + (w - text_size[0]) // 2
                    text_y = y + (h + text_size[1]) // 2
                    cv2.putText(img, selected_button.text, (text_x, text_y),
                                cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)
                else:
                    cv2.putText(img, selected_button.text, (x + 9, y + 40),
                                cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

            # Reset clicking state
            clicking = False
            selected_button = None

    # Draw cooldown indicator
    cooldown_remaining = cooldown_time - (current_time - last_click_time)
    if cooldown_remaining > 0:
        # Draw cooldown progress bar
        cooldown_width = int(200 * (cooldown_remaining / cooldown_time))
        cv2.rectangle(img, (10, 350), (10 + cooldown_width, 370), (0, 0, 255), cv2.FILLED)
        cv2.putText(img, "Cooldown", (10, 345), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)

    # Display the text input area
    cv2.rectangle(img, (5, 200), (600, 270), (100, 0, 100), cv2.FILLED)
    cv2.putText(img, finalText, (30, 248), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

    # Display instructions
    cv2.putText(img, "Bring index & middle fingers close to click", (10, 400),
                cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    cv2.putText(img, "Hold position for click to register", (10, 420),
                cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    cv2.putText(img, "Make a fist to pause interaction", (10, 440),
                cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    cv2.putText(img, "Press 'q' to quit", (10, 460),
                cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

    # Show the image
    cv2.imshow("Virtual Keyboard", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
        break

cap.release()
cv2.destroyAllWindows()
hands.close()