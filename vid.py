import cv2
import numpy as np
import time


def take_vid(cam : str):

    cap = cv2.VideoCapture(cam)

    ret, frame = cap.read()
    h, w, _ = frame.shape

    # image finale vide (simulation de fauchée)
    sat_image = np.zeros_like(frame)

    y = 0

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        #Prise de la bande
        strip_height = h
        strip = frame[y:y+strip_height, :, :]



        # on copie dans l'image finale
        sat_image[y:y+strip_height, :, :] = strip

        # avance comme une fauchée satellite
        y += strip_height

        # reset quand on arrive en bas
        if y >= h:
            y = 0

            # option : effacer pour nouveau passage
            # sat_image[:] = 0

        cv2.imshow("Satellite sweep simulation", sat_image)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


take_vid("/dev/video4")