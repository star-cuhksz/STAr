/**
 * @Author: larryu
 * @Date:   2018-02-26T15:36:16+08:00
 * @Email:  larryu1202@gmail.com
 * @Last modified by:   larryu
 * @Last modified time: 2018-02-26T16:47:03+08:00
 */

#include "opencv2/opencv.hpp"
#include "opencv2/stitching/detail/blenders.hpp"
#include "stdio.h"
#include "time.h"

using namespace cv;
using namespace cv::detail;

Mat readhomography(const char* homo_xml) {
  Mat homo;
  FileStorage fs(homo_xml, cv::FileStorage::READ);
  if (!fs.isOpened()) {
    std::cout << "Save File Failed!" << std::endl;
    std::exit(1);
  } else {
    fs["homography"] >> homo;
    return homo;
  }
}

int main(int argc, char const* argv[]) {
  if (argc != 6) {
    printf(
        "Usage: ./stitching 4to5.xml 6to5.xml LeftToCamera2.xml "
        "LeftToCamera3.xml Camera1ToLeft.xml output.jpg\n");
    return 1;
  }
  clock_t start = clock();
  VideoCapture capture_01(0);
  VideoCapture capture_02(1);
  VideoCapture capture_03(2);
  VideoCapture capture_04(3);
  VideoCapture capture_05(4);
  VideoCapture capture_06(5);
  /*namedWindow("v1");
  namedWindow("v2");
  namedWindow("v3");
  namedWindow("v4");
  namedWindow("v5");
  namedWindow("v6");*/

  Mat camera1, camera2, camera3, camera4, camera5, camera6;
  Mat homo4to5, homo6to5, homoLeftToCamera2, homoLeftToCamera3,
      homoCamera1ToLeft;
  Mat result_s, result_mask;
  Mat leftPanoImg;
  Mat leftPanoImgV2;
  Mat leftPanoImgV3;
  Mat totalPano;

  // measure performance
  clock_t t;

  /*imshow("v1", camera1);
  imshow("v2", camera2);
  imshow("v3", camera3);
  imshow("v4", camera4);
  imshow("v5", camera5);
  imshow("v6", camera6);*/

  t = clock();
  homo4to5 = readhomography(argv[1]);
  homo6to5 = readhomography(argv[2]);
  homoLeftToCamera2 = readhomography(argv[3]);
  homoLeftToCamera3 = readhomography(argv[4]);
  homoCamera1ToLeft = readhomography(argv[5]);
  printf("reading homographies takes %f seconds\n",
         float(clock() - t) / CLOCKS_PER_SEC);

  // ------------------stitch left three cameras--------------------------------
  while (true) {
    t = clock();

    capture_01 >> camera6;
    capture_02 >> camera3;
    capture_03 >> camera1;
    capture_04 >> camera4;
    capture_05 >> camera2;
    capture_06 >> camera5;
    printf("reading cameras takes %f seconds\n",
           float(clock() - t) / CLOCKS_PER_SEC);

    // prepare shift matrix
    // FIXME: adjust the shift matrix
    Mat shf4to5Mat =
        (Mat_<double>(3, 3) << 1.0, 0, 0, 0, 1.0, camera2.rows, 0, 0, 1.0);
    Mat shf6to5Mat =
        (Mat_<double>(3, 3) << 1.0, 0, 0, 0, 1.0, -1 * camera2.rows, 0, 0, 1.0);

    t = clock();
    // prepare masks
    Mat midMask(camera5.size(), CV_8U);
    midMask(Rect(0, 0, midMask.cols, midMask.rows)).setTo(255);

    Mat upMask(camera4.size(), CV_8U);
    upMask(Rect(0, 0, upMask.cols, upMask.rows)).setTo(255);
    warpPerspective(upMask, upMask, shf4to5Mat * homo4to5,
                    Size(camera4.cols, camera4.rows));

    warpPerspective(camera4, camera4, shf4to5Mat * homo4to5,
                    Size(camera4.cols, camera4.rows));

    Mat downMask(camera6.size(), CV_8U);
    downMask(Rect(0, 0, midMask.cols, midMask.rows)).setTo(255);
    warpPerspective(downMask, downMask, shf6to5Mat * homo6to5,
                    Size(camera5.cols, camera5.rows));
    warpPerspective(camera6, camera6, shf6to5Mat * homo6to5,
                    Size(camera5.cols, camera5.rows));

    // ready for blend
    MultiBandBlender blender(false, 5);

    blender.prepare(Rect(0, 0, camera4.cols, camera4.rows * 3));

    blender.feed(camera4, upMask, Point(0, 0));
    blender.feed(camera5, midMask, Point(0, camera4.rows));
    blender.feed(camera6, downMask, Point(0, camera4.rows * 2));

    blender.blend(result_s, result_mask);
    result_s.convertTo(leftPanoImg, CV_8U);

    printf("stitching left three cameras takes %f seconds\n",
           float(clock() - t) / CLOCKS_PER_SEC);

    // sittch leftPanoImg to camera 2
    t = clock();

    // perpare mask
    Mat leftMask(leftPanoImg.size(), CV_8U);
    leftMask(Rect(0, 0, leftMask.cols, leftMask.rows)).setTo(255);

    Mat camera2Mask(camera2.size(), CV_8U);
    camera2Mask(Rect(0, 0, camera2.cols, camera2.rows)).setTo(255);

    // prepare shift matrix
    // FIXME: adjust values of this shift matrix
    Mat shiftLeftToCamera2 =
        (Mat_<double>(3, 3) << 1.0, 0, -1 * leftPanoImg.cols - 15, 0, 1.0, 18,
         0, 0, 1.0);

    warpPerspective(leftMask, leftMask, shiftLeftToCamera2 * homoLeftToCamera2,
                    Size(leftPanoImg.cols, leftPanoImg.rows));

    warpPerspective(leftPanoImg, leftPanoImg,
                    shiftLeftToCamera2 * homoLeftToCamera2,
                    Size(leftPanoImg.cols, leftPanoImg.rows));

    // ready for blend

    blender.prepare(Rect(0, 0, camera2.cols * 2, camera2.rows * 3));

    blender.feed(leftPanoImg, leftMask, Point(0, 0));
    blender.feed(camera2, camera2Mask, Point(camera2.cols, camera2.rows));

    blender.blend(result_s, result_mask);
    result_s.convertTo(leftPanoImgV2, CV_8U);
    // the size of leftPanoImgV2 is Size(2 * camera.cols, 3 * camera.rows) now

    printf("stitching left pano image to camera 2 takes %f seconds\n",
           float(clock() - t) / CLOCKS_PER_SEC);

    // stitch leftPanoImgV2 to camera 3
    t = clock();

    // perpare mask
    Mat leftMaskV2(leftPanoImgV2.size(), CV_8U);
	leftMaskV2(Rect(0, 0, leftMaskV2.cols, leftMaskV2.rows)).setTo(255);

    Mat camera3Mask(camera3.size(), CV_8U);
    camera3Mask(Rect(0, 0, camera3.cols, camera3.rows)).setTo(255);

    // prepare shift matrix
    // FIXME: adjust values of this shift matrix
    Mat shiftLeftToCamera3 =
        (Mat_<double>(3, 3) << 1.0, 0, -1 * leftPanoImg.cols - 15, 0, 1.0, 18,
         0, 0, 1.0);

    warpPerspective(leftMaskV2, leftMaskV2, shiftLeftToCamera3 * homoLeftToCamera3,
                    Size(leftPanoImgV2.cols, leftPanoImgV2.rows));

    warpPerspective(leftPanoImgV2, leftPanoImgV2,
                    shiftLeftToCamera3 * homoLeftToCamera3,
                    Size(leftPanoImgV2.cols, leftPanoImgV2.rows));

    // ready for blend

    blender.prepare(Rect(0, 0, camera3.cols * 2, camera3.rows * 3));

    blender.feed(leftPanoImgV2, leftMaskV2, Point(0, 0));
    blender.feed(camera3, camera3Mask, Point(camera3.cols, camera3.rows * 2));

    blender.blend(result_s, result_mask);
    result_s.convertTo(leftPanoImgV3, CV_8U);

    printf("stitching left pano image v2 to camera 3 takes %f seconds\n",
           float(clock() - t) / CLOCKS_PER_SEC);

    // stitch camera 1 to leftPanoImgV3
    t = clock();

    // perpare mask
    Mat leftMaskV3(leftPanoImgV3.size(), CV_8U);
	leftMaskV3(Rect(0, 0, leftMaskV3.cols, leftMaskV3.rows)).setTo(255);

    Mat camera1Mask(camera1.size(), CV_8U);
    camera3Mask(Rect(0, 0, camera1.cols, camera1.rows)).setTo(255);

    // prepare shift matrix
    // FIXME: adjust values of this shift matrix
    Mat shiftCamera1ToLeft =
        (Mat_<double>(3, 3) << 1.0, 0, -1 * leftPanoImg.cols - 15, 0, 1.0, 18,
         0, 0, 1.0);

    warpPerspective(camera1Mask, camera1Mask,
                    shiftCamera1ToLeft * homoCamera1ToLeft,
                    Size(camera1.cols, camera1.rows));

    warpPerspective(camera1, camera1, shiftCamera1ToLeft * homoCamera1ToLeft,
                    Size(camera1.cols, camera1.rows));

    // ready for blend

    blender.prepare(Rect(0, 0, camera1.cols * 2, camera1.rows * 3));

    blender.feed(leftPanoImgV3, leftMaskV3, Point(0, 0));
    blender.feed(camera1, camera1Mask, Point(camera1.cols, 0));

    blender.blend(result_s, result_mask);
    result_s.convertTo(totalPano, CV_8U);

    printf("stitching camera 1 to left pano image v3 takes %f seconds\n",
           float(clock() - t) / CLOCKS_PER_SEC);

    namedWindow("result", CV_WINDOW_NORMAL);

    imshow("result", totalPano);

    imwrite("result.jpg", totalPano);

    waitKey(30);
  }

  return 0;
}
