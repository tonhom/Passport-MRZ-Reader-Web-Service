# USAGE
# python detect_mrz.py --images examples

# import the necessary packages
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
import imutils
import cv2
import pytesseract
from mrz.checker.td3 import TD3CodeChecker
from data_fixer import passport_fixer


def get_passport_data(path):
    # initialize a rectangular and square structuring kernel
    rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
    sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (27, 27))

    image = cv2.imread(path)
    imgHeight = image.shape[0]
    imgWidth = image.shape[1]
    if imgWidth < imgHeight:
        image = cv2.rotate(image, rotateCode=cv2.ROTATE_90_COUNTERCLOCKWISE)
        
    image = imutils.resize(image, height=600)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # gray = cv2.bitwise_not(gray)

    # smooth the image using a 3x3 Gaussian, then apply the blackhat
    # morphological operator to find dark regions on a light background
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    # cv2.imshow("Gray", gray)
    # cv2.waitKey()
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rectKernel)
    # cv2.imshow("Blackhat", blackhat)
    # cv2.waitKey()

    # compute the Scharr gradient of the blackhat image and scale the
    # result into the range [0, 255]
    gradX = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    gradX = np.absolute(gradX)
    (minVal, maxVal) = (np.min(gradX), np.max(gradX))
    gradX = (255 * ((gradX - minVal) / (maxVal - minVal))).astype("uint8")

    # apply a closing operation using the rectangular kernel to close
    # gaps in between letters -- then apply Otsu's thresholding method
    gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKernel)
    thresh = cv2.threshold(
        gradX, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # perform another closing operation, this time using the square
    # kernel to close gaps between lines of the MRZ, then perform a
    # serieso of erosions to break apart connected components
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sqKernel)
    # cv2.imshow("tresh", thresh)
    # cv2.waitKey()
    thresh = cv2.erode(thresh, None, iterations=4)
    # cv2.imshow("Erode", thresh)
    # cv2.waitKey()

    # during thresholding, it's possible that border pixels were
    # included in the thresholding, so let's set 5% of the left and
    # right borders to zero
    p = int(image.shape[1] * 0.05)
    thresh[:, 0:p] = 0
    thresh[:, image.shape[1] - p:] = 0

    # find contours in the thresholded image and sort them by their
    # size
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[-2]
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

    # loop over the contours
    for c in cnts:
        # compute the bounding box of the contour and use the contour to
        # compute the aspect ratio and coverage ratio of the bounding box
        # width to the width of the image
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)
        crWidth = w / float(gray.shape[1])

        # cv2.imshow("Image", image[y:y + h, x:x + w].copy())

    # check to see if the aspect ratio and coverage width are within
    # acceptable criteria
        # print(ar, crWidth)
        if ar > 5 and crWidth > 0.6:
            # pad the bounding box since we applied erosions and now need
            # to re-grow it
            pX = int((x + w) * 0.03)
            pY = int((y + h) * 0.03)
            (x, y) = (x - pX, y - pY)
            (w, h) = (w + (pX * 2), h + (pY * 2))

            # extract the ROI from the image and draw a bounding box
            # surrounding the MRZ
            roi = image[y:y + h, x:x + w].copy()
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            break
        else:
            roi = None

    # show the output images
    # cv2.imshow("Image", image)
    if roi is not None:
        config = ("--oem 0 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ<1234567890")
        # config = ("--oem 3 --psm 6 --tessdata-dir ./Trained -l eng+ocrb")
        # config = ("--oem 0")
        # cv2.imshow("ROI", roi)
        # cv2.waitKey()
        roiGray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        roiBlackhat = cv2.morphologyEx(roiGray, cv2.MORPH_BLACKHAT, rectKernel)
        roiThresh = cv2.threshold(
            roiBlackhat, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # coords = np.column_stack(np.where(roiThresh > 0))
        # angle = cv2.minAreaRect(coords)[-1]
        # # the `cv2.minAreaRect` function returns values in the
        # # range [-90, 0); as the rectangle rotates clockwise the
        # # returned angle trends to 0 -- in this special case we
        # # need to add 90 degrees to the angle
        # if angle < -45:
        #     angle = -(90 + angle)

        # # otherwise, just take the inverse of the angle to make
        # # it positive
        # else:
        #     angle = -angle

        # # rotate the image to deskew it
        # (h, w) = roiBlackhat.shape[:2]
        # center = (w // 2, h // 2)
        # M = cv2.getRotationMatrix2D(center, angle, 1.0)
        # rotated = cv2.warpAffine(
        #     roiBlackhat, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        # print(angle)

        # roiBitwise = cv2.bitwise_not(roi)
        # roiThresh = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # cv2.imshow("ROTATED", roiThresh)
        # cv2.waitKey()
        # pytesseract.image_to_string(Image.open("./imagesStackoverflow/xyz-small-gray.png"),lang="eng",boxes=False,config="--psm 4 --oem 3 -c tessedit_char_whitelist=-01234567890XYZ:"))
        text = pytesseract.image_to_string(roiThresh, config=config)
        # print(text)

        # enhancing text from ocr engine
        text = text.replace(" ", "")
        textList = text.split("\n")
        textEnhanced = []
        for txt in textList:
            l = len(txt) > 44
            if l > 44:
                textEnhanced.append(txt[0:44])
            elif l < 44:
                complement = txt + "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
                textEnhanced.append(complement[0:44])
            else:
                textEnhanced.append(txt)
        # print(textEnhanced)
        text = "\n".join(textEnhanced)

        td3_check = TD3CodeChecker(text)
        fields = td3_check.fields()
        # print(fields)
        # print(fields.surname.replace("0", "O"))

        # if bd > current then minus 1 century (human age = 0-99)
        now = datetime.datetime.now()
        oneCentury = relativedelta(years=100)

        bd = None
        try:
            bd = datetime.datetime.strptime(fields.birth_date, '%y%m%d')
            if bd > now:
                bd = bd - oneCentury
        except Exception as identifier:
            bd = None

        exp = None
        try:
            exp = datetime.datetime.strptime(fields.expiry_date, '%y%m%d')
        except Exception as identifier:
            exp = None

        # print(bd.strftime('%Y-%m-%d'))
        try:
            resp = {
                'surname': "" if fields.surname == "None" else fields.surname.replace("0", "O"),
                'given_names': "" if fields.name == "None" else fields.name.replace("0", "O"),
                'country_code': fields.country,
                'passport_number': passport_fixer(fields.document_number),
                'nationality': fields.nationality,
                'sex': 'M' if fields.sex == 'H' else fields.sex,
                'birth_date': bd.strftime('%Y-%m-%d') if bd is not None else None,
                'expiry_date': exp.strftime('%Y-%m-%d') if exp is not None else None
            }
            return resp
        except Exception as identifier:
            return None
    else:
        return None
