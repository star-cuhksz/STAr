#!/usr/bin/env python

'''
Camshift tracker
================

This is a demo that shows mean-shift based tracking
You select a color objects such as your face and it tracks it.
This reads from video camera (0 by default, or the camera number the user enters)

http://www.robinhewitt.com/research/track/camshift.html

Usage:
------
    camshift.py [<video source>]

    To initialize tracking, select the object with mouse

Keys:
-----
    ESC   - exit
    b     - toggle back-projected probability visualization
'''

# Python 2/3 compatibility
from __future__ import print_function
import sys
PY3 = sys.version_info[0] == 3

if PY3:
    xrange = range

import numpy as np
import cv2 as cv

# local module
import video
from video import presets
from utils.draw import rand_color


class App(object):
    def __init__(self, video_src):
        self.cam = video.create_capture(video_src, presets['cube'])
        _ret, self.frame = self.cam.read()
        cv.namedWindow('camshift')
        cv.setMouseCallback('camshift', self.onmouse)

        self.selection = None
        self.drag_start = None
        self.show_backproj = False
        self.track_window = None

        self.selections = []
        self.hist_list = []
        self.track_windows = []
        self.track_box_colors = []  # colors of tracking boxes: [(Blue:int, Green:int, Red:int), ...]

    def onmouse(self, event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            self.drag_start = (x, y)
            self.track_window = None
        if self.drag_start:
            xmin = min(x, self.drag_start[0])
            ymin = min(y, self.drag_start[1])
            xmax = max(x, self.drag_start[0])
            ymax = max(y, self.drag_start[1])
            # self.selection = (xmin, ymin, xmax, ymax)
        if event == cv.EVENT_LBUTTONUP:
            self.drag_start = None
            self.selections.append((xmin, ymin, xmax, ymax))
            self.track_window = (xmin, ymin, xmax - xmin, ymax - ymin)
            self.track_windows.append((xmin, ymin, xmax - xmin, ymax - ymin))
            self.track_box_colors = rand_color(exist_color_list=self.track_box_colors)[1]  # pick a new color for tracking box

    def show_hist(self, idx):
        bin_count = self.hist_list[idx].shape[0]
        bin_w = 24
        img = np.zeros((256, bin_count*bin_w, 3), np.uint8)
        for i in xrange(bin_count):
            # h = int(self.hist[i])
            h = int(self.hist_list[idx][i])
            cv.rectangle(img=img, pt1=(i*bin_w+2, 255), pt2=((i+1)*bin_w-2, 255-h),
                         color=(int(180.0*i/bin_count), 255, 255), thickness=-1)
        img = cv.cvtColor(src=img, code=cv.COLOR_HSV2BGR)
        cv.imshow('hist-{}'.format(idx), img)

    def run(self):
        while True:
            _ret, self.frame = self.cam.read()
            vis = self.frame.copy()
            hsv = cv.cvtColor(src=self.frame, code=cv.COLOR_BGR2HSV)  # convert to HSV to reduce the influence of lightness
            mask = cv.inRange(src=hsv, lowerb=np.array((0., 60., 32.)), upperb=np.array((180., 255., 255.)))

            # if self.selection:
            #     x0, y0, x1, y1 = self.selection
            #     hsv_roi = hsv[y0:y1, x0:x1]
            #     mask_roi = mask[y0:y1, x0:x1]
            #     hist = cv.calcHist([hsv_roi], [0], mask_roi, [16], [0, 180] )
            #     cv.normalize(hist, hist, 0, 255, cv.NORM_MINMAX)
            #     self.hist = hist.reshape(-1)
            #     self.show_hist()
            #
            #     vis_roi = vis[y0:y1, x0:x1]
            #     cv.bitwise_not(vis_roi, vis_roi)
            #     vis[mask == 0] = 0
            if self.selections:
                for idx, selection in enumerate(self.selections):
                    if selection:
                        x0, y0, x1, y1 = selection
                        hsv_roi = hsv[y0:y1, x0:x1]
                        mask_roi = mask[y0:y1, x0:x1]
                        hist = cv.calcHist(images=[hsv_roi], channels=[0], mask=mask_roi, histSize=[16], ranges=[0, 180])
                        cv.normalize(src=hist, dst=hist, alpha=0, beta=255, norm_type=cv.NORM_MINMAX)
                        # self.hist = hist.reshape(-1)
                        try:
                            self.hist_list[idx] = hist.reshape(-1)  # update hist
                        except:
                            self.hist_list.append(hist.reshape(-1))  # add hist if select new
                        # self.show_hist(idx)

                        vis_roi = vis[y0:y1, x0:x1]
                        cv.bitwise_not(vis_roi, vis_roi)
                        vis[mask == 0] = 0
                    self.show_hist(idx)

            # if self.track_window and self.track_window[2] > 0 and self.track_window[3] > 0:
            #     self.selection = None
            #     prob = cv.calcBackProject([hsv], [0], self.hist, [0, 180], 1)
            #     prob &= mask
            #     term_crit = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 1)
            #     track_box, self.track_window = cv.CamShift(prob, self.track_window, term_crit)
            #
            #     if self.show_backproj:
            #         vis[:] = prob[...,np.newaxis]
            #     try:
            #         cv.ellipse(vis, track_box, (0, 0, 255), 2)
            #     except:
            #         print(track_box)
            if self.track_windows:
                for idx, track_window in enumerate(self.track_windows):
                    if track_window and track_window[2] > 0 and track_window[3] > 0:
                        self.selections[idx] = None  # FIXME: comment this line for refresh hist, however, that will lead to bad display
                        prob = cv.calcBackProject(images=[hsv], channels=[0], hist=self.hist_list[idx],
                                                  ranges=[0, 180], scale=1)
                        prob &= mask
                        term_crit = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 1)
                        track_box, track_window = cv.CamShift(probImage=prob, window=track_window, criteria=term_crit)

                        if self.show_backproj:
                            vis[:] = prob[..., np.newaxis]
                        try:
                            cv.ellipse(img=vis, center=track_box, axes=self.track_box_colors[idx], angle=2)
                        except:
                            print(track_box)

            cv.imshow('camshift', vis)

            ch = cv.waitKey(5)
            if ch == 27:
                break
            if ch == ord('b'):
                self.show_backproj = not self.show_backproj
        cv.destroyAllWindows()


if __name__ == '__main__':
    import sys
    try:
        video_src = sys.argv[1]
    except:
        video_src = 0
    print(__doc__)
    App(video_src).run()
