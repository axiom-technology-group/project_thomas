from recognize import *
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import imutils
import time
import cv2

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
lock = threading.Lock()
vs = None
 
# initialize a flask object
app = Flask(__name__)
 
# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()

time.sleep(1.0)


@app.route("/")
def index():
    init()
	# return the rendered template
    return render_template('index.html')

def init():
    global vs

    # start a thread that will perform motion detection
    vs = VideoStream(src=0).start()
    time.sleep(1.0)
    t = threading.Thread(target=recogonize, args=(32,))
    t.daemon = True
    t.start()


def recogonize(frameCount):
    # grab global references to the video stream, output frame, and
    # lock variables
    global vs, outputFrame, lock

    # initialize accumulated weight
    accumWeight = 0.5

    ## region of interest (ROI) coordinates
    top, right, bottom, left = 10, 500, 225, 750

    # initialize num of frames
    num_frames = 0

    # calibration indicator
    calibrated = False

    # keep looping, until interrupted
    while(True):
        # get the current frame
        frame = vs.read()

        # resize the frame
        frame = imutils.resize(frame, width=800)

        # flip the frame so that it is not the mirror view
        frame = cv2.flip(frame, 1)

        # clone the frame
        clone = frame.copy()

        # get the height and width of the frame
        (height, width) = frame.shape[:2]

        # get the ROI
        roi = frame[top:bottom, right:left]

        # convert the roi to grayscale and blur it
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        # to get the background, keep looking till a threshold is reached
        # so that our weighted average model gets calibrated
        if num_frames < frameCount:
            run_avg(gray, accumWeight)
            if num_frames == 1:
                app.logger.info("[STATUS] please wait! calibrating...")
            elif num_frames == 29:
                app.logger.info("[STATUS] calibration successfull...")
        else:
            # segment the hand region
            hand = segment(gray)

            # check whether hand region is segmented
            if hand is not None:
                # if yes, unpack the thresholded image and
                # segmented region
                (thresholded, segmented) = hand

                # draw the segmented region and display the frame
                cv2.drawContours(clone, [segmented + (right, top)], -1, (0, 0, 255))

                # count the number of fingers
                fingers = count(thresholded, segmented)

                cv2.putText(clone, str(fingers), (70, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

                #app.logger.info('The num of finger is: %d', fingers)
                
                # show the thresholded image
                # cv2.imshow("Thesholded", thresholded)

        # draw the segmented hand
        cv2.rectangle(clone, (left, top), (right, bottom), (0,255,0), 2)

        # increment the number of frames
        num_frames += 1
        # observe the keypress by the user
        keypress = cv2.waitKey(1) & 0xFF

        # if the user pressed "q", then stop looping
        if keypress == ord("q"):
            app.logger.info('The num of finger is: %d', fingers)
            break
        # display the frame with segmented hand
        # cv2.imshow("Video Feed", clone)
        with lock:
            outputFrame = clone.copy()



    # free up memory
    camera.release()
    cv2.destroyAllWindows()


def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock

	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue

			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

			# ensure the frame was successfully encoded
			if not flag:
				continue

		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')


@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	t = threading.Thread(target=recogonize, args=(32,))
	t.daemon = True
	t.start()
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

# check to see if this is the main thread of execution
if __name__ == '__main__':

	# start the flask app
	app.run(host='0.0.0.0', port=1234, debug=True, threaded=True,
            use_reloader=False)
 
# release the video stream pointer
vs.stop()
