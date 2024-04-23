from collections import defaultdict
import os
import ast
import cv2
import numpy as np


# Reads and returns urls from environment 
def getStreamUrls():
    urls = os.environ.get('STREAM_URLS')
    if urls is None:
        return ['rtp://127.0.0.1:6000', 'rtp://127.0.0.1:6002', 'rtp://127.0.0.1:6004']
    urls = ast.literal_eval(urls)
    return [url.strip() for url in urls]


# Release streams
def releaseStreams(streams: list[cv2.VideoCapture]):
    for stream in streams:
        if stream is not None and stream.isOpened():
            stream.release()


# Scale frame to half it's size
def scale(frame: cv2.typing.MatLike):
    return cv2.resize(src=frame, dsize=None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)


# Scales frames
def scaleFrames(frames: list[cv2.typing.MatLike]):
    return [frame if frame is None else scale(frame) for frame in frames]


# Returns default dimensions or the dimensions from one of the images that is passed in the array
def getDimension(frames: list[cv2.typing.MatLike]):
    filteredFrames = list(filter(lambda frame: frame is not None, frames))
    if len(filteredFrames) > 0:
        frame: cv2.typing.MatLike = filteredFrames[0]
        return frame.shape
    return (360, 240, 3)


# Sanitizes frames if a frame is not present return a black image for the same
def getSanitizedFrames(frames: list[cv2.typing.MatLike]):
    dims = getDimension(frames)
    return [np.zeros(dims, dtype=np.uint8) if frame is None else frame for frame in frames]    


# Tries to get the stream
def getStream(url: str):
    print(f'[Info] -- Getting stream: {url}')
    try:
        stream = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        totalChannels = int(stream.get(cv2.CAP_PROP_AUDIO_TOTAL_CHANNELS))
        baseIndex = int(stream.get(cv2.CAP_PROP_AUDIO_BASE_INDEX))
        totalStreams = int(stream.get(cv2.CAP_PROP_AUDIO_TOTAL_STREAMS))
        print(f'[INFO] -- Audio Streams -> {totalStreams} Audio Channels -> {totalChannels}, Base Index -> {baseIndex}')
        return stream if stream.isOpened() else None
    except:
        return None

def getAudioChannels(stream: cv2.VideoCapture):
    totalChannels = int(stream.get(cv2.CAP_PROP_AUDIO_TOTAL_CHANNELS))
    baseIndex = int(stream.get(cv2.CAP_PROP_AUDIO_BASE_INDEX))
    audioData: list[cv2.typing.MatLike] = []
    for i in range(0, totalChannels):
        audionChannel: cv2.typing.MatLike = []
        stream.retrieve(audionChannel, baseIndex + i)
        print(audionChannel)
        audioData.append(audionChannel)

# Captures frame from a stream if stream is not present returns None
def getFrameFromStream(stream: cv2.VideoCapture):
    if stream is None :
        return None
    elif stream.isOpened():
        ret, frame = stream.read()
        if not ret:
            return None
        return frame
    return None

def stackVertically(frameA: cv2.typing.MatLike, frameB=None):
    if frameB is None:
        return frameA
    return np.row_stack((frameB, frameA))

def concatenate(frames: list[cv2.typing.MatLike]):
    h_stacks = None
    for i in range(0, len(frames), 2):
        if i + 1 < len(frames):
            h_stacks = stackVertically(
                np.column_stack((frames[i], frames[i + 1])),
                h_stacks
            )
        else:
            h_stacks = stackVertically(
                np.column_stack((frames[i], 255 * np.ones(frames[i].shape, dtype=np.uint8))),
                h_stacks
            )

    return h_stacks


# Driver function
def main():
    streamUrls = getStreamUrls()
    streamMap = defaultdict(lambda: None)
    while True:
        # Get Streams if stream is not present
        for url in streamUrls:
            stream = streamMap[url]
            if stream is None:
                stream = getStream(url)
                streamMap[url] = stream

        # [getAudioChannels(stream) for stream in streamMap.values()]
        frames = [getFrameFromStream(stream) for stream in streamMap.values()]
        scaledFrames = scaleFrames(frames)
        sanitizedFrames = getSanitizedFrames(scaledFrames)
        displayframe = concatenate(sanitizedFrames)
        cv2.imshow('Mixer', displayframe)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            releaseStreams(streamMap.values())
            break
        

if __name__ == '__main__':
    main()
    cv2.destroyAllWindows()

# sound bars for all audio channels