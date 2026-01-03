import time
import threading
from picamera2 import Picamera2
import BlynkLib, os
from stream_server import run_server # Import your engine

# 1. SETUP BLYNK
BLYNK_AUTH = 'rlae8SVJlydLMI-Y41NYARtBRA2Exvpy'
blynk = BlynkLib.Blynk(BLYNK_AUTH)

# 2. INITIALIZE HARDWARE
print("Starting Camera Module 3...")
picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

# 3. START STREAM SERVER IN BACKGROUND
# We pass the 'picam2' object to the server so it can use it
server_thread = threading.Thread(target=run_server, args=(picam2,))
server_thread.daemon = True
server_thread.start()

print("Server is live at: http://192.168.224.115:5000/video_feed")

# 4. BLYNK ACTION
@blynk.on("V2")
def handle_v2_write(value):
    if int(value[0]) == 1:
        print("Blynk Trigger: Capturing Still Image...")
        # use_video_port=True allows capturing while the stream is running!
        picam2.capture_file("blynk_capture.jpg")
        print("Image saved.")

# 5. MAIN LOOP
try:
    while True:
        blynk.run()
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Shutting down...")
finally:
    picam2.stop()

