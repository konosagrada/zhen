import cv2
import os

videopath = ['0913', '0917']
OUTPUT_DIR = 'E:/yxmz/0809/'
START_TIME = 39 * 1000
END_TIME = (29 * 60 + 20) * 1000
FIRST_WORD_RANGE = [300, 450, 340, 470]
WORD_RANGE = [180, 436, 660, 475]
WORD_THRESH = 220
GRADUAL_TIME = 1000


def check_word(image):
    return (image ** 2).sum() / image.size * 100 > 4


def check_different(pre_image, cur_image):
    if pre_word is None:
        return True
    en =((cur_image - pre_image) ** 2).sum() / pre_image.size * 100
    print(en)
    return 3 < ((cur_image - pre_image) ** 2).sum() / pre_image.size * 100 < 40



if __name__ == "__main__":
    for i in videopath:
        dir = OUTPUT_DIR + i + '/'
        os.makedirs(dir, 0o777, True)
        cap = cv2.VideoCapture(str(i + '.mp4'))
        success = True
        pre_word = None
        sun_shine_time = 0
        save_image = False
        while success:
            success, curr_frame = cap.read()
            if not success:
                break
            time = cap.get(cv2.CAP_PROP_POS_MSEC)
            time_str = '{:0>2d}m{:0>2d}s{:0>2d}ms'.format(int(time // 60000), int(time % 60000 // 1000),
                                                          int(time % 1000 // 40))
            print('\r>>  时间:' + time_str, end='')
            if time < START_TIME:
                continue
            if time > END_TIME:
                continue
            if sun_shine_time > time:
                save_image = True
                continue

            capture = curr_frame[:, :, 0]
            first_words = capture[FIRST_WORD_RANGE[1]:FIRST_WORD_RANGE[3], FIRST_WORD_RANGE[0]:FIRST_WORD_RANGE[2]]
            words = capture[WORD_RANGE[1]:WORD_RANGE[3], WORD_RANGE[0]:WORD_RANGE[2]]

            _, first_words = cv2.threshold(first_words, WORD_THRESH, 255, cv2.THRESH_BINARY)
            if check_word(first_words):
                _, curr_words = cv2.threshold(words, WORD_THRESH, 255, cv2.THRESH_BINARY)
                if check_word(curr_words) and check_different(pre_word, curr_words):
                    if not save_image:
                        sun_shine_time = time + GRADUAL_TIME
                        continue

                    pre_word = curr_words
                    temp = curr_frame[WORD_RANGE[1]:WORD_RANGE[3], WORD_RANGE[0]:WORD_RANGE[2]]
                    cv2.imshow('image', temp)
                    cv2.waitKey(1)
                    save_image = False
                    cv2.imwrite(dir + time_str + '.jpg', temp)

        cap.release()
