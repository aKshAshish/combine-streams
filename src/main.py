from collections import defaultdict
import os
import ast
import cv2
import numpy as np


# Reads and returns urls from environment 
def getStreamUrls():
    urls = os.environ.get('STREAM_URLS')
    if urls is None:
        return ['rtp://127.0.0.1:6000', 'rtp://127.0.0.1:6001', 'rtp://127.0.0.1:6002']
    urls = ast.literal_eval(urls)
    return [url.strip() for url in urls]


# Release streams
def releaseStreams(streams: list[cv2.VideoCapture]):
    for stream in streams:
        if stream is not None and stream.isOpened():
            stream.release()


# Scale frame to half it's size
def scale(frame: cv2.typing.MatLike):
    return cv2.resize(src=frame, fx=0.1, fy=0.1)


# Scales frames
def scaleFrames(frames: list[cv2.typing.MatLike]):
    return [None if not frame else scale(frame) for frame in frames]


# Returns default dimensions or the dimensions from one of the images that is passed in the array
def getDimension(frames: list[cv2.typing.MatLike]):
    filteredFrames = filter(lambda frame: frame is not None, frames)
    if len(frame) > 0:
        frame: cv2.typing.MatLike = filteredFrames[0]
        return frame.shape()
    return (360, 240, 3)


# Sanitizes frames if a frame is not present return a black image for the same
def getSanitizedFrames(frames: list[cv2.typing.MatLike]):
    dims = getDimension(frames)
    return [np.zeros(dims) if not frame else frame for frame in frames]    


# Tries to get the stream
def getStream(url: str):
    try:
        stream = cv2.VideoCapture(url)
        return stream
    except:
        return None


# Captures frame from a stream if stream is not present returns None
def getFrameFromStream(stream: cv2.VideoCapture):
    if stream is None:
        return None
    else:
        ret, frame = stream.read()
        if not ret:
            return None
        return frame


def concatenate(frames: list[cv2.typing.MatLike]):
    h_stacks = []
    for i in range(0, len(frames), 2):
        if i + 1 < len(frames):
            h_stacks.push(np.concatenate((frames[i], frames[i + 1]), axis=0))
        else:
            h_stacks.push(np.concatenate((frames[i], np.zeros(frames[i].shape())), axis=0))

    return np.concatenate(h_stacks)


# Driver function
def main():
    streamUrls = getStreamUrls()
    streamMap = defaultdict(lambda: None)
    while True:
        # Get Streams if stream is not present
        for url in streamUrls:
            stream = streamMap[url]
            if not stream:
                stream = getStream(url)
                streamMap[url] = stream

        frames = [getFrameFromStream(stream) for stream in streamMap.values()]
        scaledFrames = scaledFrames(frames)
        sanitizedFrames = getSanitizedFrames(scaledFrames)
        displayframe = concatenate(sanitizedFrames)
        cv2.imshow('Mixer', displayframe)
        if cv2.waitKey(0) & 0xFF == ord('q'):
            releaseStreams(streamMap.values())
            break
        

if __name__ == '__main__':
    main()
    cv2.destroyAllWindows()

# sound bars for all audio channels