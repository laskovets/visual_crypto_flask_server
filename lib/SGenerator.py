import cv2
import numpy as np
import random


def generate_password():
    #chars = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789'
    password = ''
    for i in range(random.randint(4, 8)):
        password += random.choice(chars)

    img = np.zeros([100, 100, 3], dtype=np.uint8)
    img.fill(255)  # or img[:] = 255

    cv2.putText(img, password[:4], color=(0, 0, 0), org=(2, 40), fontFace=cv2.FONT_HERSHEY_SIMPLEX, thickness=3, fontScale=1.1)
    cv2.putText(img, password[4:], color=(0, 0, 0), org=(2, 90), fontFace=cv2.FONT_HERSHEY_SIMPLEX, thickness=3, fontScale=1.1)
    # start resize
    scale_percent = 200

    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)

    dsize = (width, height)

    # resize image
    img = cv2.resize(img, dsize)
    # stop resize

    cv2.imwrite('secret.png', img)
    return password, img[:, :, 0]


if __name__ == '__main__':
    print('start generator')
    _, img = generate_password()
    cv2.imshow('secret', img)
    cv2.waitKey(0)
