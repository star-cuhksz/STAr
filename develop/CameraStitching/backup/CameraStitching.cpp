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
	}
	else {
		fs["homography"] >> homo;
		return homo;
	}
}

int main(int argc, char const* argv[]) {
	if (argc != 6) {
		printf(
			"Usage: ./stitching  "
			"1to2.xml 3to2.xml 4to5.xml 6to5.xml 2to5.xml output.jpg\n");
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
	Mat homo1to2, homo3to2, homo4to5, homo6to5, homo2to5;
	Mat result_s, result_mask;
	Mat leftPanoImg;
	Mat righPanoImg;
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
	homo1to2 = readhomography(argv[1]);
	homo3to2 = readhomography(argv[2]);
	homo4to5 = readhomography(argv[3]);
	homo6to5 = readhomography(argv[4]);
	homo2to5 = readhomography(argv[5]);
	printf("reading homographies takes %f seconds\n",
		float(clock() - t) / CLOCKS_PER_SEC);

	// ------------------stitch left three cameras--------------------------------
	while (true)
	{
		t = clock();

		capture_01 >> camera6;
		capture_02 >> camera3;
		capture_03 >> camera1;
		capture_04 >> camera4;
		capture_05 >> camera2;
		capture_06 >> camera5;
		printf("reading images takes %f seconds\n",
			float(clock() - t) / CLOCKS_PER_SEC);
		// prepare shift matrix
		Mat shf1to2Mat =
			(Mat_<double>(3, 3) << 1.0, 0, 0, 0, 1.0, camera2.rows, 0, 0, 1.0);
		Mat shf3to2Mat =
			(Mat_<double>(3, 3) << 1.0, 0, 0, 0, 1.0, -1 * camera2.rows, 0, 0, 1.0);


		t = clock();
		// prepare masks
		Mat midMask(camera5.size(), CV_8U);
		midMask(Rect(0, 0, midMask.cols, midMask.rows)).setTo(255);

		Mat upMask(camera4.size(), CV_8U);
		upMask(Rect(0, 0, upMask.cols, upMask.rows)).setTo(255);
		warpPerspective(upMask, upMask, homo4to5 * shf1to2Mat,
			Size(camera4.cols, camera4.rows));

		warpPerspective(camera4, camera4, homo4to5 * shf1to2Mat,
			Size(camera4.cols, camera4.rows));

		Mat downMask(camera6.size(), CV_8U);
		downMask(Rect(0, 0, midMask.cols, midMask.rows)).setTo(255);
		warpPerspective(downMask, downMask, shf3to2Mat * homo6to5,
			Size(camera5.cols, camera5.rows));
		warpPerspective(camera6, camera6, shf3to2Mat * homo6to5,
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

		// ------------------stitch right three cameras-------------------------------
		t = clock();
		midMask(Rect(0, 0, midMask.cols, midMask.rows)).setTo(255);

		// Mat upMask(camera1.size(), CV_8U);
		upMask(Rect(0, 0, midMask.cols, midMask.rows)).setTo(255);
		warpPerspective(upMask, upMask, homo1to2 * shf1to2Mat,
			Size(camera2.cols, camera2.rows));
		warpPerspective(camera1, camera1, homo1to2 * shf1to2Mat,
			Size(camera2.cols, camera2.rows));

		// Mat downMask(camera3.size(), CV_8U);
		downMask(Rect(0, 0, midMask.cols, midMask.rows)).setTo(255);
		warpPerspective(downMask, downMask, shf3to2Mat * homo3to2,
			Size(camera2.cols, camera2.rows));
		warpPerspective(camera3, camera3, shf3to2Mat * homo3to2,
			Size(camera2.cols, camera2.rows));

		// ready for blend
		// MultiBandBlender blender(false, 5);

		blender.prepare(Rect(0, 0, camera1.cols, camera1.rows * 3));

		blender.feed(camera1, upMask, Point(0, 0));
		blender.feed(camera2, midMask, Point(0, camera1.rows));
		blender.feed(camera3, downMask, Point(0, camera1.rows * 2));

		// Mat result_s, result_mask;
		blender.blend(result_s, result_mask);
		result_s.convertTo(righPanoImg, CV_8U);

		printf("stitching right three cameras takes %f seconds\n",
			float(clock() - t) / CLOCKS_PER_SEC);

		// ------------------stitch total panorama------------------------------------
		t = clock();

		Mat shftMat = (Mat_<double>(3, 3) << 1.0, 0, -1 * leftPanoImg.cols - 15, 0,
			1.0, 18, 0, 0, 1.0);

		leftPanoImg = Mat(leftPanoImg, Rect(100, 265, leftPanoImg.cols - 100,
			leftPanoImg.rows - 450));
		righPanoImg = Mat(righPanoImg, Rect(100, 265, righPanoImg.cols - 100,
			righPanoImg.rows - 450));

		Mat rightMask(righPanoImg.size(), CV_8U, Scalar(255));
		Mat leftMask(leftPanoImg.size(), CV_8U, Scalar(255));

		warpPerspective(righPanoImg, righPanoImg, shftMat * homo2to5,
			Size(righPanoImg.cols, righPanoImg.rows));
		warpPerspective(rightMask, rightMask, shftMat * homo2to5,
			Size(rightMask.cols, rightMask.rows));

		// MultiBandBlender blender(false, 5);

		blender.prepare(Rect(0, 0, righPanoImg.cols * 2, righPanoImg.rows));

		blender.feed(leftPanoImg, leftMask, Point(0, 0));
		blender.feed(righPanoImg, rightMask, Point(righPanoImg.cols, 0));

		blender.blend(result_s, result_mask);
		result_s.convertTo(totalPano, CV_8U);

		printf("stitching left and right takes %f seconds\n",
			float(clock() - t) / CLOCKS_PER_SEC);

		printf("stitching six cameras takes %f seconds\n",
			float(clock() - start) / CLOCKS_PER_SEC);

		namedWindow("result", CV_WINDOW_NORMAL);

		imshow("result", totalPano);

		imwrite("result.jpg", totalPano);

		waitKey(30);
	}


	return 0;
}
