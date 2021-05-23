import numpy as np
import cv2
import base64
import hashlib
import random


def add_frame_limit(image):
    height, width = image.shape
    cv2.line(image, (0, 0), (0, height), (0, 0, 0), 4)
    cv2.line(image, (0, 0), (width, 0), (0, 0, 0), 4)
    cv2.line(image, (width, 0), (width, height), (0, 0, 0), 4)
    cv2.line(image, (0, height), (width, height), (0, 0, 0), 4)
    return image


class VisualCrypto:

    def __init__(self, k=2):
        self.k = k
        self.s_0 = None
        self.s_1 = None
        self.image = None
        self.shadows = []

    def makeBitMatrix(self):
        k = self.k
        kk = 2**k
        arr = np.zeros((k, kk))
        for i in range(k):
            c = (kk/ int(2**(i+1)))
            t = c
            flag1 = 0
            flag2 = 1
            for j in range(kk):
                if j==t:
                    t = t + c
                    f = flag1
                    flag1 = flag2
                    flag2 = f
                arr[i][j] = flag1
        # print()
        return arr

    def makeBaseMatrix(self):
        k = self.k
        a = self.makeBitMatrix()
        kk = int(2**k)
        l_0 = 0
        l_1 = 0
        self.s_0 = np.zeros((k, int(kk/2)))
        self.s_1 = np.zeros((k, int(kk/2)))
        for i in range(kk):
            s = 0
            for j in range(k):
                s = s + a[j][i]
            if s % 2 == 0:
                for j in range(k):
                    self.s_0[j][l_0] = a[j][i]
                l_0 = l_0 + 1
            else:
                for j in range(k):
                    self.s_1[j][l_1] = a[j][i]
                l_1 = l_1 + 1

        # print('\nS_0')
        # print(self.s_0)
        #
        # print('\nS_1')
        # print(self.s_1)

    def loadPicture(self, name):
        image1 = cv2.imread(name, 0)
        self.image = image1
        self.processImage()

    def processImage(self):
        h, w = self.image.shape
        for i in range(h):
            for j in range(w):
                if self.image[i][j] >= 128:
                    self.image[i][j] = 0
                else:
                    self.image[i][j] = 255

    def swapColumn(self, a):
        k = self.k
        for i in range(int(2**k)*int(2**k)):
            l = random.randrange(int(2**(k - 1)))
            m = random.randrange(int(2 ** (k - 1)))
            for j in range(k):
                if l != m:
                    c = a[j][l]
                    a[j][l] = a[j][m]
                    a[j][m] = c
        return a

    def splitImage(self):
        k = self.k
        h, w = self.image.shape
        raster1 = np.zeros((h, w*int(2**(k-1))))
        raster2 = raster1.copy()
        raster1 = [raster1, raster2]
        for i in range(h):
            for j in range(w):
                pixel = self.image[i][j]
                a = self.s_1
                if pixel == 0:
                    a = self.s_0
                a = self.swapColumn(a)
                for g in range(k):
                    s = a[g]
                    for d in range(int(2**(k-1))):
                        if s[d] == 0:
                            pixel = 0
                        else:
                            pixel = 255
                        raster1[g][i][j*int(2**(k-1)) + d] = pixel
        self.saveShadows(raster1)

    def saveShadows(self, raster):
        for i in range(len(raster)):
            self.shadows.append(add_frame_limit(raster[i]))
            # self.shadows.append(raster[i])
            # cv2.imwrite('result/shadow_{}.png'.format(i), raster[i])
        # res = ((raster[0] + raster[1]) / 2).astype(np.uint8)
        # cv2.imshow('t', res)
        # cv2.waitKey(0)


if __name__ == '__main__':
    for i in range(2):
        vc = VisualCrypto(2)
        vc.loadPicture("secret.png")
        vc.processImage()
        vc.makeBaseMatrix()
        vc.splitImage()
        res_to_db = vc.shadows[0]

        _, buffer = cv2.imencode('.png', res_to_db)
        byteArr = base64.b64encode(buffer)
        print("shadow hash {}".format(hashlib.md5(byteArr).digest()))
