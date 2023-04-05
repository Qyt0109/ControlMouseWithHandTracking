import cv2
import pyautogui
from cvzone.HandTrackingModule import HandDetector
import numpy as np

cap = cv2.VideoCapture(1)
cv2.namedWindow("Dao Quyet beta test")
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

detector = HandDetector(detectionCon=0.8, maxHands=2)
screen_size = pyautogui.size()
wrist_xr, wrist_yr,wrist_xl, wrist_yl = 50,50,50,50
x_screen, y_screen = 50, 50
is_clicked = False
prev_x_screen = prev_y_screen = None

left_hand_areas = {
    (100,100,200,200): 'w',
    (200, 150, 300, 250): 'a',
    (0, 150, 100, 250): 'd',
    (100, 200, 200, 300): 's'
}

right_hand_areas = {
    (350,150,550,400):None
}
    #{"x1": 300, "y1": 100, "x2": 500, "y2": 350}

def calc_finger_distance(lm_list):
    x1, y1 = lm_list[4][1:3]
    x2, y2 = lm_list[8][1:3]
    return np.linalg.norm(np.array([x2,y2])-np.array([x1,y1]))

prev_x_screen, prev_y_screen = None, None
while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    hands, frame = detector.findHands(frame, flipType=False, draw=True)
    # Draw hand areas
    for areas, color in zip([left_hand_areas, right_hand_areas], [(255, 0, 0), (0, 255, 0)]):
        for area in areas:
            cv2.rectangle(frame, (area[0], area[1]), (area[2], area[3]), color, 2)

    for hand in hands:
        if hand["type"] == "Right":
            wrist_xr, wrist_yr = hand['lmList'][9][0], hand['lmList'][9][1]
            x_screen = (wrist_xr - 350) * screen_size[0] / 200
            y_screen = (wrist_yr - 150) * screen_size[1] / 250

            # Click or release mouse button
            if calc_finger_distance(hand["lmList"]) < 45:
                if not is_clicked:
                    pyautogui.mouseDown(x_screen, y_screen)
                    is_clicked = True
            else:
                if is_clicked:
                    pyautogui.mouseUp(x_screen, y_screen)
                    is_clicked = False
            
            # Move mouse cursor
            if prev_x_screen != x_screen or prev_y_screen != y_screen:
                pyautogui.moveTo(x_screen, y_screen)
                prev_x_screen, prev_y_screen = x_screen, y_screen

        elif hand["type"] == "Left":
            wrist_xl, wrist_yl = hand['lmList'][9][0], hand['lmList'][9][1]
            for area, action in left_hand_areas.items():
                x1, x2, y1, y2 = area
                if x1 <= wrist_xl <= x2 and y1 <= wrist_yl <= y2:
                    if action:
                        pyautogui.press(action)

    print(wrist_xl,wrist_yl,wrist_xr,wrist_yr)
    # Draw a circle at the coordinates of the wrist
    cv2.circle(frame, (wrist_xr, wrist_yr), 5, (0, 0, 255), -1)
    # Show the coordinates next to the point
    cv2.putText(frame, f'({wrist_xr}, {wrist_yr})', (wrist_xr + 10, wrist_yr), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    # Draw a circle at the coordinates of the wrist
    cv2.circle(frame, (wrist_xl, wrist_yl), 5, (0, 0, 255), -1)
    # Show the coordinates next to the point
    cv2.putText(frame, f'({wrist_xl}, {wrist_yl})', (wrist_xl + 10, wrist_yl), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    cv2.imshow('frame', frame)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()