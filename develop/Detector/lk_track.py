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
import log_helper
from common import anorm2, draw_str, get_velocity, draw_velocity_arrowedline
from time import clock
from datetime import datetime

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
        :datafield  self.track_len: \n
                    self.detect_interval: frequency of finding feature points \n
                    self.tracks: tracking points \n
                    self.cam: video instance obtained from video_src \n
                    self.frame_idx: \n
                    self.log_velocity: log_helper.Log instance that records velocity \n
                    self.log_feature_points: log_helper.Log instance that records feature points \n
                    self.point_color: color of the feature point, BGR pattern \n
                    self.trace_color: color of the trace, BGR pattern \n
                    self.velocity_params: the parameters of velocity lines
                                            color: the color of velocity lines
                                            scale: the ratio of arrowed line and displacement
                                            thickness: the thickness of velocity lines
                                            line_type: determine how the line will be drawn on the image
        """
        self.track_len = 10
        self.detect_interval = 5
        self.tracks = []
        self.cam = video.create_capture(video_src)
        self.frame_idx = 0
        self.log_velocity = log_helper.Log(".velocity_log")
        self.log_feature_points = log_helper.Log(".points_log")
        self.point_color = (0, 255, 0)
        self.trace_color = (0, 255, 0)
        self.velocity_params = dict(color=(0, 0, 255),
                                    scale=10,
                                    thickness=1,
                                    line_type=cv.LINE_AA)

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
                # p1 is the list of 2D points containing the calculated new positions of input
                # features in the nextImg
                p1, _status, _err = cv.calcOpticalFlowPyrLK(prevImg=img0, nextImg=img1, prevPts=p0,
                                                            nextPts=None, **lk_params)
                p0r, _status, _err = cv.calcOpticalFlowPyrLK(prevImg=img1, nextImg=img0, prevPts=p1,
                                                            nextPts=None, **lk_params)
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
                    cv.circle(img=vis, center=(x, y), radius=2, color=self.point_color, thickness=-1)
                self.tracks = new_tracks

                # draw trace
                cv.polylines(img=vis, pts=[np.int32(tr) for tr in self.tracks], isClosed=False, color=self.trace_color)

                # draw velocity arrowed line
                for (x1, y1), (x2, y2), good_flag in zip(p0.reshape(-1, 2), p1.reshape(-1, 2), good):
                    if not good_flag:
                        continue
                    self.log_feature_points.log_buffer.append((x2, y2))
                    self.log_velocity.log_buffer.append(get_velocity(point_prev=(x1, y1), point_curr=(x2, y2),
                                                      time_interval=self.detect_interval))
                    draw_velocity_arrowedline(output_img=vis, point_prev=(x1, y1), point_curr=(x2, y2),
                                              **self.velocity_params)

                # export feature points per frame
                self.log_feature_points.log_add(self.log_feature_points.log_buffer)
                # export velocity data per frame
                self.log_velocity.log_add(self.log_velocity.log_buffer)

                # show information
                draw_str(vis, (20, 20), 'track count: %d' % len(self.tracks))

            # detect feature points every detect_interval frames
            if self.frame_idx % self.detect_interval == 0:
                # initiate the mask
                mask = np.zeros_like(frame_gray)
                mask[:] = 255
                for x, y in [np.int32(tr[-1]) for tr in self.tracks]:
                    cv.circle(img=mask, center=(x, y), radius=5, color=0, thickness=-1)
                # detect new feature points
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
