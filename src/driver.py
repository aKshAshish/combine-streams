from rtpStream import RTPStream
from videoStream import VideoStream
from datetime import datetime
import av
import time
import cv2
import io

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

# readVideoStream()
# cv2.destroyAllWindows()

def display_frame(frame, start_time, pts_offset, frame_rate):
    if frame.pts is not None:
        play_time = (frame.pts - pts_offset) * frame.time_base.numerator / frame.time_base.denominator
        if start_time is not None:
            current_time = time.time() - start_time
            time_diff = play_time - current_time
            if time_diff > 1 / frame_rate:
                return False
            if time_diff > 0:
                time.sleep(time_diff)
    img = frame.to_ndarray(format='bgr24')
    cv2.imshow('Video', img)
    return True

def get_pts(frame):
    return frame.pts

def render(stream: RTPStream):
    rawData = io.BytesIO()
    cur_pos = 0
    frames_buffer = []
    start_time = None
    pts_offset = None
    got_key_frame = False
    while True:
        try:
            data = stream.data.get_nowait()
        except:
            time.sleep(5)
            continue
        rawData.write(data)
        rawData.seek(cur_pos)
        if cur_pos == 0:
            container = av.open(rawData, mode='r')
            print(container.streams)
            original_codec_ctx = container.streams.video[0].codec_context
            codec = av.codec.CodecContext.create(original_codec_ctx.name, 'r')
        cur_pos += len(data)
        dts = None
        for packet in container.demux():
            if packet.size == 0:
                continue
            dts = packet.dts
            if pts_offset is None:
                pts_offset = packet.pts
            if not got_key_frame and packet.is_keyframe:
                got_key_frame = True
            if stream.data.qsize() > 8 and not packet.is_keyframe:
                got_key_frame = False
                continue
            if not got_key_frame:
                continue
            frames = codec.decode(packet)
            if start_time is None:
                start_time = time.time()
            frames_buffer += frames
            frames_buffer.sort(key=get_pts)
            for frame in frames_buffer:
                if display_frame(frame, start_time, pts_offset, codec.framerate):
                    frames_buffer.remove(frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        if dts is not None:
            container.seek(25000)
        rawData.seek(cur_pos)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    stream.stop()
    cv2.destroyAllWindows()

def driver():
    rawDataStream = RTPStream('127.0.0.1', 6000)
    rawDataStream.start()
    render(rawDataStream)

driver()