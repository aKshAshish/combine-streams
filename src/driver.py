from rtpStream import RTPStream
from videoStream import VideoStream
from datetime import datetime
import time
import cv2

def readAudioStream():
    rawDataStream = RTPStream('127.0.0.1', 6000)

    while True:
        if rawDataStream.stopped:
            rawDataStream.start()
        data = rawDataStream.data

        if data is None:
            print(f'[INFO] -- {datetime.now().strftime('%H:%M:%S')} -- No data avalilable. Sleeping for 5 seconds.')
            time.sleep(5)
            continue

        try:
            print(data)
        except Exception as err:
            print(f'[Error] -- Failed to read the stream data. Unexpected {err=}, {type(err)=}')
            rawDataStream.stop()
            break

def readVideoStream():
    videoStream = VideoStream('rtp://127.0.0.1:6000')

    while True:
        if videoStream.stopped:
            videoStream.start()
        data = videoStream.data

        if data is None:
            print(f'[INFO] -- {datetime.now().strftime('%H:%M:%S')} -- No data avalilable. Sleeping for 5 seconds.')
            time.sleep(5)
            continue

        try:
            # Display or process the frame
            cv2.imshow('Frame', data)
        except Exception as err:
            print(f'[Error] -- Failed to read the stream data. Unexpected {err=}, {type(err)=}')
            videoStream.stop()
            break

        if cv2.waitKey(60) & 0xFF == ord('q'):
            videoStream.stop()
            break

readVideoStream()
cv2.destroyAllWindows()