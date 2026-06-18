import cv2
import numpy as np
import time


def take_photo():
    cap = cv2.VideoCapture("/dev/video4")

    if not cap.isOpened():
        print("Camera inaccessible")
        return

    ret, frame = cap.read()

    if not ret:
        print("Impossible de lire une frame")
        return

    # afficher la photo
    cv2.imshow("Photo", frame)

    # sauvegarder sur disque
    cv2.imwrite("photo.jpg", frame)

    print("Photo sauvegardée : photo.jpg")

    cv2.waitKey(0)  # attend une touche
    cap.release()
    cv2.destroyAllWindows()


take_photo()