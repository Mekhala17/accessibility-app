# gesture_utils.py
import copy
import itertools
import cv2 as cv
import numpy as np

# ---------------------- Preprocessing ----------------------
def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)

    base_x, base_y = temp_landmark_list[0]
    for idx, point in enumerate(temp_landmark_list):
        temp_landmark_list[idx][0] -= base_x
        temp_landmark_list[idx][1] -= base_y

    temp_landmark_list = list(itertools.chain.from_iterable(temp_landmark_list))
    max_value = max(map(abs, temp_landmark_list)) or 1

    return [v / max_value for v in temp_landmark_list]


def pre_process_point_history(image, point_history):
    image_width, image_height = image.shape[1], image.shape[0]

    temp_point_history = copy.deepcopy(point_history)
    if not temp_point_history:
        return []

    base_x, base_y = temp_point_history[0]
    processed = []

    for point in temp_point_history:
        processed.append(
            (point[0] - base_x) / image_width
        )
        processed.append(
            (point[1] - base_y) / image_height
        )

    return processed


# ---------------------- Landmark Utilities ----------------------
def calc_bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_array = np.empty((0, 2), int)
    for landmark in landmarks.landmark:
        x = min(int(landmark.x * image_width), image_width - 1)
        y = min(int(landmark.y * image_height), image_height - 1)
        landmark_array = np.append(landmark_array, [[x, y]], axis=0)

    x, y, w, h = cv.boundingRect(landmark_array)
    return [x, y, x + w, y + h]


def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
    landmark_points = []

    for landmark in landmarks.landmark:
        x = min(int(landmark.x * image_width), image_width - 1)
        y = min(int(landmark.y * image_height), image_height - 1)
        landmark_points.append([x, y])

    return landmark_points


# ---------------------- Drawing Utilities ----------------------
def draw_bounding_rect(use_brect, image, brect):
    if use_brect:
        cv.rectangle(
            image,
            (brect[0], brect[1]),
            (brect[2], brect[3]),
            (0, 0, 0),
            2,
        )
    return image


def draw_info_text(image, brect, handedness, hand_sign_text="", finger_gesture_text=""):
    label = handedness.classification[0].label
    if hand_sign_text:
        label = f"{label}: {hand_sign_text}"

    cv.rectangle(
        image,
        (brect[0], brect[1] - 30),
        (brect[2], brect[1]),
        (0, 0, 0),
        -1,
    )

    cv.putText(
        image,
        label,
        (brect[0] + 5, brect[1] - 7),
        cv.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        1,
        cv.LINE_AA,
    )

    if finger_gesture_text:
        cv.putText(
            image,
            f"Gesture: {finger_gesture_text}",
            (brect[0], brect[3] + 30),
            cv.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 0, 0),
            4,
            cv.LINE_AA,
        )
        cv.putText(
            image,
            f"Gesture: {finger_gesture_text}",
            (brect[0], brect[3] + 30),
            cv.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 255),
            2,
            cv.LINE_AA,
        )

    return image


def draw_point_history(image, point_history):
    for i, point in enumerate(point_history):
        if point[0] != 0 and point[1] != 0:
            cv.circle(
                image,
                (int(point[0]), int(point[1])),
                1 + i // 2,
                (152, 251, 152),
                2,
            )
    return image


def draw_info(image, fps, mode, number=-1):
    cv.putText(
        image,
        f"FPS: {int(fps)}",
        (10, 30),
        cv.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 0, 0),
        4,
        cv.LINE_AA,
    )
    cv.putText(
        image,
        f"FPS: {int(fps)}",
        (10, 30),
        cv.FONT_HERSHEY_SIMPLEX,
        1.0,
        (255, 255, 255),
        2,
        cv.LINE_AA,
    )
    return image
