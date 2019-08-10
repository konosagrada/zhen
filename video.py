import cv2
import os

START_TIME = 45000
content_BG_ROI = (0, 0, 50, 80)
title_BG_ROI = (710, 440, 718, 510)
content_ROI = (36, 200, 250, 350)
title_ROI = (50, 457, 600, 512)
face_ROI = (366, 20, 700, 300)


def calculate(image1, image2):
    # 灰度直方图算法
    # 计算单通道的直方图的相似值
    hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
    # 计算直方图的重合度
    degree = 0
    for i in range(len(hist1)):
        if hist1[i] != hist2[i]:
            degree = degree + \
                     (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
        else:
            degree = degree + 1
    degree = degree / len(hist1)
    return degree


def classify_hist_with_split(image1, image2, size=(256, 256)):
    # RGB每个通道的直方图相似度
    # 将图像resize后，分离为RGB三个通道，再计算每个通道的相似值
    image1 = cv2.resize(image1, size)
    image2 = cv2.resize(image2, size)
    sub_image1 = cv2.split(image1)
    sub_image2 = cv2.split(image2)
    sub_data = 0
    for im1, im2 in zip(sub_image1, sub_image2):
        sub_data += calculate(im1, im2)
    sub_data = sub_data / 3
    return sub_data


face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
face_cascade.load('./haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
eye_cascade.load('haarcascade_eye.xml')


def check_eye(frame, name):
    face = frame[face_ROI[1]:face_ROI[3], face_ROI[0]:face_ROI[2]]
    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 3)
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 3, cv2.CASCADE_SCALE_IMAGE, (10, 10))
        if len(eyes) >= 2:
            first_x = 0
            first_y = 0
            i = 0
            for (ex, ey, ew, eh) in eyes:
                if first_x == 0:
                    first_x = ex
                    first_y = ey
                    cv2.rectangle(face, (x + ex, y + ey), (x + ex + ew, y + ey + eh),
                                  (255, 0, 0))
                    cv2.rectangle(face, (x, y), (x + w, y + h),
                                  (255, 255, 0))
                    i += 1
                    continue
                if abs(ex - first_x) < 10 or abs(ey - first_y) > 10:
                    continue
                if w > ex + ew or h > ey + eh:
                    cv2.rectangle(face, (x + ex, y + ey), (x + ex + ew, y + ey + eh),
                                  (255, 0, 0))
                    cv2.rectangle(face, (x, y), (x + w, y + h),
                                  (255, 255, 0))
                    i += 1
                    first_x = ex
                    first_y = ey
            if i >= 2:
                cv2.imwrite(dir + name + '.jpg', frame)
                return True
    return False


def check_content(curr_frame, prev_frame, name, pre_content_bg_image):
    cur_content_bg_image = frame[content_BG_ROI[1]:content_BG_ROI[3], content_BG_ROI[0]:content_BG_ROI[2]]
    if classify_hist_with_split(cur_content_bg_image, pre_content_bg_image) > 0.7:
        curr_image = curr_frame[content_ROI[1]:content_ROI[3], content_ROI[0]:content_ROI[2]]
        prev_image = prev_frame[content_ROI[1]:content_ROI[3], content_ROI[0]:content_ROI[2]]
        if classify_hist_with_split(curr_image, prev_image) < 0.7:
            # cv2.imwrite(dir + name + 'curr_image.jpg', curr_image)
            # cv2.imwrite(dir + name + 'prev_image.jpg', prev_image)
            cv2.imwrite(dir + name + '.jpg', frame)
            return 1
    else:
        return 2
    return 0


def check_title(curr_frame, prev_frame, name, pre_title_bg_image):
    cur_title_bg_image = frame[title_BG_ROI[1]:title_BG_ROI[3], title_BG_ROI[0]:title_BG_ROI[2]]
    if classify_hist_with_split(cur_title_bg_image, pre_title_bg_image) < 0.8:
        curr_image = curr_frame[title_ROI[1]:title_ROI[3], title_ROI[0]:title_ROI[2]]
        prev_image = prev_frame[title_ROI[1]:title_ROI[3], title_ROI[0]:title_ROI[2]]
        if classify_hist_with_split(curr_image, prev_image) < 0.87:
            # cv2.imwrite(dir + name + 'curr_image.jpg', curr_frame)
            # cv2.imwrite(dir + name + 'prev_image.jpg', prev_image)
            cv2.imwrite(dir + name + '.jpg', frame)
            return True
    return False


if __name__ == "__main__":
    videopath = ['0104', '0103', '0102', '0101']
    for i in videopath:
        dir = 'E:/PythonProjects/zhen/result/' + i + '/'
        os.makedirs(dir, 0o777, True)
        cap = cv2.VideoCapture(str(i + '.mp4'))
        curr_frame = None
        prev_frame_1 = None
        prev_frame_2 = None
        prev_frame_3 = None
        prev_frame_4 = None
        content_bg_image = None
        title_bg_image = None
        content_flower = False
        title_flower = False
        fruit = False
        success, frame = cap.read()
        other_content = False
        while (success):
            time = cap.get(cv2.CAP_PROP_POS_MSEC)
            if time > START_TIME:
                name = '{:0>2d}_{:0>2d}_{:0>2d}'.format(int(time // 60000), int(time % 60000 // 1000),
                                                        int(time % 1000 // 40))
                print(name)

                if time < START_TIME + 100:
                    content_bg_image = frame[content_BG_ROI[1]:content_BG_ROI[3], content_BG_ROI[0]:content_BG_ROI[2]]
                    title_bg_image = frame[title_BG_ROI[1]:title_BG_ROI[3], title_BG_ROI[0]:title_BG_ROI[2]]
                    cv2.imwrite(dir + name + '.jpg', frame)

                curr_frame = frame
                if curr_frame is not None and prev_frame_3 is not None:
                    content_flower = check_content(curr_frame, prev_frame_3, name, content_bg_image)
                    if content_flower == 2:
                        if not other_content:
                            cv2.imwrite(dir + name + '.jpg', frame)
                        other_content = True
                        cv2.imshow('image', frame)
                        cv2.waitKey(1)
                        prev_frame_3 = prev_frame_2
                        prev_frame_2 = prev_frame_1
                        prev_frame_1 = curr_frame
                        success, frame = cap.read()
                        continue

                    other_content = False
                    title_flower = check_title(curr_frame, prev_frame_3, name, title_bg_image)
                    if content_flower == 1 or title_flower:
                        fruit = True
                    if fruit:
                        if check_eye(curr_frame, name):
                            fruit = False
                cv2.imshow('image', frame)
                cv2.waitKey(1)
                prev_frame_3 = prev_frame_2
                prev_frame_2 = prev_frame_1
                prev_frame_1 = curr_frame
            success, frame = cap.read()
        cap.release()
