#!/usr/bin/env python

'''
Lucas-Kanade tracker
====================

Lucas-Kanade sparse optical flow demo. Uses goodFeaturesToTrack
for track initialization and back-tracking for match verification
between frames.

Usage
-----
lk_track.py [<video_source>]


Keys
----
ESC - exit
'''

# Python 2/3 compatibility
from __future__ import print_function

import numpy as np
import cv2 as cv
import video
from common import anorm2, draw_str
from time import clock

# Parameters for lucas kanade optical flow
lk_params = dict( winSize  = (15, 15),
                  maxLevel = 2,
                  criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))

# Parameters for corner detection
feature_params = dict( maxCorners = 500,
                       qualityLevel = 0.3,
                       minDistance = 7,
                       blockSize = 7 )

class App:
    def __init__(self, video_src):
        """
        Optical flow initiation
        :param  video_src: the path of video source
        :datafield  self.track_len:
                    self.detect_interval: frequency of finding feature points
                    self.tracks: tracking points
                    self.cam: video instance obtained from video_src
                    self.frame_idx:
                    self.trace_color: color of the trace, BGR pattern
        """
        self.track_len = 10
        self.detect_interval = 5
        self.tracks = []
        self.cam = video.create_capture(video_src)
        self.frame_idx = 0
        self.trace_color = (0, 0, 255)

    # def get_velocity(self, point_prev, point_curr):
    #     """
    #     Calculate the velocity of the interested feature points.
    #     :param point_prev: previous point in type numpy.array
    #     :param point_curr: current point in type numpy.array
    #     :return: the velocity of this point in unit 'pixel/frame'
    #     """
    #     distance = np.linalg.norm(point_prev - point_curr)
    #     velocity = float(distance / self.detect_interval)
    #     return velocity

    def run(self):
        while True:
            _ret, frame = self.cam.read()

            # avoid crashing if frame not found
            if _ret:
                frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            else:
                continue
            vis = frame.copy()

            if len(self.tracks) > 0:
                img0, img1 = self.prev_gray, frame_gray
                p0 = np.float32([tr[-1] for tr in self.tracks]).reshape(-1, 1, 2)
                p1, _st, _err = cv.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params)
                p0r, _st, _err = cv.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)
                d = abs(p0-p0r).reshape(-1, 2).max(-1)
                good = d < 1
                new_tracks = []
                for tr, (x, y), good_flag in zip(self.tracks, p1.reshape(-1, 2), good):
                    if not good_flag:
                        continue
                    tr.append((x, y))
                    if len(tr) > self.track_len:
                        del tr[0]
                    new_tracks.append(tr)
                    cv.circle(img=vis, center=(x, y), radius=2, color=self.trace_color, thickness=-1)
                self.tracks = new_tracks
                cv.polylines(vis, [np.int32(tr) for tr in self.tracks], False, (0, 255, 0))
                draw_str(vis, (20, 20), 'track count: %d' % len(self.tracks))

            # detect feature points every detect_interval frames
            if self.frame_idx % self.detect_interval == 0:
                # initiate the mask
                mask = np.zeros_like(frame_gray)
                mask[:] = 255
                for x, y in [np.int32(tr[-1]) for tr in self.tracks]:
                    cv.circle(img=mask, center=(x, y), radius=5, color=0, thickness=-1)
                p = cv.goodFeaturesToTrack(frame_gray, mask=mask, **feature_params)
                if p is not None:
                    for x, y in np.float32(p).reshape(-1, 2):
                        self.tracks.append([(x, y)])

            # update previous frame
            self.frame_idx += 1
            self.prev_gray = frame_gray
            cv.imshow('lk_track', vis)

            # press ESC to quit
            ch = cv.waitKey(1)
            if ch == 27:
                break

        # release the camera if used
        self.cam.release()

def main():
    import sys
    try:
        video_src = sys.argv[1]
    except:
        video_src = 0

    print(__doc__)
    App(video_src).run()
    cv.destroyAllWindows()

if __name__ == '__main__':
    main()
