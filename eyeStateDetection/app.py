# from flask import Flask, send_from_directory
#
# app= Flask(__name__)
# from subprocess import check_output
# check_output("jupyter nbconvert --to html --execute --ExecutePreprocessor.timeout=9999999 eye-state-detection-drowsiness-detection.ipynb" , shell=True).decode()


from keras.models import model_from_json
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import os
from datetime import datetime
from datetime import timedelta

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'


class FacialExpressionModel(object):
    EMOTIONS_LIST = ["Closed", "Open"]

    def __init__(self, model_json_file, model_weights_file):
        # load model from JSON file
        self.loaded_model = tf.keras.models.load_model('my_new_model.h5')
        self.first = True

    def predict_emotion(self, img):
        final_img = cv2.resize(img, (224, 224))
        final_img = np.expand_dims(final_img, axis=0)
        final_img = final_img / 255.0

        self.preds = self.loaded_model.predict(final_img)
        if self.first:
            plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            classification = "Closed" if self.preds[0][0] < 0.25 and self.preds[0][0] > 0.00 else "Open" if \
                1.01 > self.preds[0][0] > 0.75 else "Inconclusive"
            plt.title(classification + "-" + str(self.preds[0][0]))
            plt.show()
            self.first = False
        classification = "Closed" if self.preds[0][0] < 0.25 and self.preds[0][0] > 0.00 else "Open" if 1.01 > \
                                                                                                        self.preds[0][
                                                                                                            0] > 0.75 else "Inconclusive"
        #print(classification + "-" + str(self.preds[0][0]))
        return classification


import cv2
import numpy as np

facec = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
model = FacialExpressionModel("model.json", "model_weights.h5")
font = cv2.FONT_HERSHEY_SIMPLEX


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.history = []

    def __del__(self):
        self.video.release()

    def treat_list(self, list):
        fiveMinutesAgo = datetime.now() - timedelta(minutes=1)
        result = []
        closed = 0
        open = 0
        for idx, val in enumerate(list):
            if val[0] > fiveMinutesAgo:
                print(val)
                result.append(val)
                if val[1] == "Open":
                    open = open + 1
                if val[1] == "Closed":
                    closed = closed + 1
        return result, closed / (len(result) if len(result) > 0 else 1)

    # returns camera frames along with bounding boxes and predictions
    def get_frame(self):
        _, fr = self.video.read()
        gray_fr = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
        eyeCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

        eyes = eyeCascade.detectMultiScale(gray_fr, 1.1, 4)
        preds = []
        for (x, y, w, h) in eyes:
            cv2.rectangle(fr, (x, y), (x + w, y + h), (0, 255, 0), 1)
            roi = fr[y:y + h, x:x + w]
            pred = model.predict_emotion(roi)
            preds.append(pred)
            cv2.putText(fr, pred, (x, y), font, 1, (255, 255, 0), 2)

        result = ""

        if len(preds) == 0:
            _, jpeg = cv2.imencode('.jpg', fr)
            return jpeg.tobytes()
        if preds.count(preds[0]) == len(preds):
            result = preds[0]
        else:
            result = "Closed"
        self.history.append((datetime.now(), result))
        self.history, perclos = self.treat_list(self.history)

        cv2.putText(fr, str(perclos), (30, 30), font, 1, (255, 255, 0), 2)
        _, jpeg = cv2.imencode('.jpg', fr)
        return jpeg.tobytes()


from flask import Flask, render_template, Response, send_from_directory

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


from os.path import exists


@app.route('/nb')
def hello():
    file_exists = exists('eye-state-detection-drowsiness-detection.html')
    if file_exists:
        return send_from_directory("", "eye-state-detection-drowsiness-detection.html")
    else:
        return "Não acabou"


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
