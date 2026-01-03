## This script will transform teh data received from Raspberry Pi camera, transform in a video and 
## send the to be streamed in the web link.

import time
import numpy as np #  organize the sequence of data, pixels, (that will become images later), in a grid.
import cv2 # OpenCV --> most popular computer vision library, will transform the data in JPEG image
import io # Stores the jpeg images temporary in the RAM memory
from flask import Flask, Response # It creates a web address (/video_feed) that stays open and keeps "serving" data.

app = Flask(__name__)

# We create a placeholder. The 'mycamera.py' will give us the actual camera later. otherwise I would need to import Picamera2 library to control  the camera.
shared_camera = None

def generate_frames():
    global shared_camera
    while True:
        # Wait if the camera isn't ready yet, give little bit of time.
        if shared_camera is None:
            time.sleep(0.1)
            continue
            
        try:
            # 1. Using Numpy to capture data to organize in a grid, we are using shared_camera instead of a local picam2
            frame_data = shared_camera.capture_array()
            
            # 2. Process with OpenCV
            frame_bgr = cv2.cvtColor(frame_data, cv2.COLOR_RGB2BGR)# Color translator, it converts data into the way the OpenCV library understands them.
            frame_bgr = cv2.flip(frame_bgr, 0) # flipping the camera, (because my physical camera is upside down).
            
            # 3. Encode, 
            # reference: https://www.geeksforgeeks.org/python/python-opencv-imencode-function/
            # later I figure it out you need 2 variables once using cv2.imencode (because this will return Tuple (a fixed list of two items --> Status, Encoded_Data) ).
            ### 1st ret will return a boolen, if Open CV suscceed or not  
            ### 2nd data_encode, will return the jpg (this code transform the data into the img format, at this case jpg)
            ret, data_encode  = cv2.imencode('.jpg', frame_bgr)
            if not ret:
                continue

            # Converting the array to bytes. 
            frame = data_encode .tobytes()

            #this part of the code is responsable for the contibue streaming (sending img to the internet)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            # yield: continous streaming,Unlike return, which sends data and then ends the function, yield sends data and pauses the function. 
            #           yield allows the code to stay inside the while True loop, sending frame after frame without ever closing the connection to the browser.
            # --frame: "Get ready, here comes a new page!"
            # Content-Type: "It’s a picture!"
            # frame: (The actual JPEG image data).
            # \r\n: "End of this page."

            time.sleep(0.01) 
        except Exception as e:
            print(f"Streaming Error: {e}")
            break

## Local server to visualize the video. (I was using for test).
@app.route('/')
def index():
    return """
    <html>
        <body style="background: #111; color: white; text-align: center; font-family: sans-serif;">
            <h1>SensePi Live Stream</h1>
            <img src="/video_feed" width="640" height="480" style="border: 5px solid #444;">
        </body>
    </html>
    """

# This funciton is using Flask to create a web 
# reference: https://blog.miguelgrinberg.com/post/video-streaming-with-flask
@app.route('/video_feed') #tells Flask which URL triggers this specific function.
def video_feed():
    # return Response: It "wraps" your camera data in a way that the browser understands it is a continuous stream.
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')
    # mimetype='multipart/x-mixed-replace;...' : It tells the browser what kind of "file" it is receiving.


# This is the function your 'mycamera.py' will call
def run_server(camera_obj):
    global shared_camera
    shared_camera = camera_obj

    # using Flask, that creats a "Ignition Switch" that starts your web server.
    # host='0.0.0.0' (Public Access).This is what allows you to open the video stream from your phone or another laptop on the same Wi-Fi
    # port=5000 (The "Door" Number)
    # threaded=True (Handling Multiple Visitors)
    app.run(host='0.0.0.0', port=5000, threaded=True, use_reloader=False)