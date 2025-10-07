from flask import Flask, Response, render_template_string, jsonify, request
import cv2
import serial
import threading
import time
import os
from datetime import datetime

class Rover:
    def __init__(self, droidcams=None):
        """
        droidcams: list of (ip, port) tuples for DroidCam / IP camera feeds.
        """
        self.app = Flask(__name__)
        self.droidcams = droidcams if droidcams is not None else [("10.34.152.48", 4747)]

        # Capture directory for saved images
        self.save_path = r"C:\Users\WinMin\Desktop\CV\Captured Images"
        os.makedirs(self.save_path, exist_ok=True)

        # Detect cameras
        self.camera_indexes = self.detect_cameras(self.droidcams)
        print("Final camera list:", self.camera_indexes)

        # Frames and locks
        self.frames = [None] * len(self.camera_indexes)
        self.locks = [threading.Lock() for _ in self.camera_indexes]

        # GPS / Arduino data
        self.latest_data = {"latitude": "N/A", "longitude": "N/A"}
        self.arduino = None

        # Serial connection
        try:
            self.arduino = serial.Serial(port='COM6', baudrate=9600, timeout=1)
            print("Serial connection established.")
        except Exception as e:
            print(f"Serial init error (ignored): {e}")

        # Start camera threads
        for i, camera_index in enumerate(self.camera_indexes):
            t = threading.Thread(target=self.capture_frames, args=(camera_index, i), daemon=True)
            t.start()

        # Start GPS thread
        gps_thread = threading.Thread(target=self.gps_communication, daemon=True)
        gps_thread.start()

        # Add Flask routes
        self.add_routes()

    def detect_cameras(self, droidcam_list=None):
        camera_indexes = []

        # Detect local cameras (0..7)
        for i in range(8):
            try:
                cam = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if cam.isOpened():
                    success, _ = cam.read()
                    if success:
                        camera_indexes.append(i)
                        print(f"Local camera detected: index {i}")
                    cam.release()
            except Exception as e:
                print(f"Error detecting local camera {i}: {e}")

        # Add IP/DroidCam feeds
        if droidcam_list:
            for ip, port in droidcam_list:
                url = f"http://{ip}:{port}/video"
                camera_indexes.append(url)
                print(f"Added IP feed: {url}")

        if not camera_indexes:
            print("No cameras detected at startup.")
        return camera_indexes

    def capture_frames(self, camera_index, index):
        friendly = str(camera_index)
        while True:
            cap = None
            try:
                if isinstance(camera_index, int):
                    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
                else:
                    cap = cv2.VideoCapture(camera_index)
                if not cap or not cap.isOpened():
                    print(f"[{friendly}] Cannot open capture. Retrying in 2s...")
                    if cap: cap.release()
                    time.sleep(2)
                    continue

                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
                print(f"[{friendly}] Capture opened.")

                while True:
                    success, frame = cap.read()
                    if not success or frame is None:
                        print(f"[{friendly}] Read failed. Reconnecting in 2s...")
                        break
                    with self.locks[index]:
                        self.frames[index] = frame
                    time.sleep(0.03)
            except Exception as e:
                print(f"[{friendly}] Exception: {e}")
            finally:
                if cap:
                    cap.release()
                time.sleep(2)

    def gps_communication(self):
        while True:
            try:
                if self.arduino and self.arduino.in_waiting > 0:
                    line = self.arduino.readline().decode('utf-8', errors='ignore').strip()
                    if "Latitude" in line and "Longitude" in line:
                        parts = line.split(",")
                        lat = parts[0].split(":")[-1].strip()
                        lon = parts[1].split(":")[-1].strip()
                        self.latest_data = {"latitude": lat, "longitude": lon}
                        print(f"GPS updated: lat={lat}, lon={lon}")
            except Exception as e:
                print(f"GPS read error: {e}")
            time.sleep(0.5)

    def generate_frames(self, camera_id):
        while True:
            try:
                with self.locks[camera_id]:
                    frame = self.frames[camera_id]
                if frame is not None:
                    ok, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                    if not ok:
                        time.sleep(0.05)
                        continue
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                else:
                    time.sleep(0.1)
            except GeneratorExit:
                break
            except Exception as e:
                print(f"[generate_frames:{camera_id}] Error: {e}")
                time.sleep(0.5)

    def add_routes(self):
        @self.app.route('/')
        def index():
            if not self.camera_indexes:
                return "<h1>No cameras available</h1>"

            camera_feeds = []
            for i, cam in enumerate(self.camera_indexes):
                label = f"Local {cam}" if isinstance(cam, int) else f"DroidCam {cam.split('://')[-1].split('/')[0]}"
                camera_feeds.append(f"""
                    <div style="display:inline-block; text-align:center; margin:10px;">
                        <h4 style="color:white;">{label}</h4>
                        <img id="cam-{i}" src="/camera/{i}" 
                             style="border:1px solid white; width:320px; height:240px; border-radius:8px;" />
                        <br>
                        <button onclick="capture({i})">Capture</button>
                    </div>
                """)

            feeds_html = "\n".join(camera_feeds)

            return render_template_string(f"""
                <html>
                    <head>
                        <title>TEAM AUTOMATONS</title>
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <style>
                            body {{
                                background-color: black;
                                text-align: center;
                                font-family: Arial, sans-serif;
                                color: white;
                            }}
                            button {{
                                margin-top: 5px;
                                padding: 5px 10px;
                                font-size: 14px;
                                cursor: pointer;
                            }}
                            table {{
                                margin:20px auto;
                                border-collapse: collapse;
                                border:2px solid white;
                                width:60%;
                                font-size:20px;
                                text-align:center;
                            }}
                            th, td {{
                                padding:15px;
                                border:1px solid white;
                            }}
                            th {{
                                background-color:#222;
                            }}
                        </style>
                    </head>
                    <body>
                        <h1>TEAM AUTOMATONS</h1>
                        <div class="feeds">
                            {feeds_html}
                        </div>
                        <h2>Real-Time Arduino / GPS Data</h2>
                        <table>
                            <tr>
                                <th>Latitude</th>
                                <th>Longitude</th>
                            </tr>
                            <tr>
                                <td id="latitude">Loading...</td>
                                <td id="longitude">Loading...</td>
                            </tr>
                        </table>

                        <script>
                            async function fetchData() {{
                                try {{
                                    const r = await fetch('/data');
                                    const d = await r.json();
                                    document.getElementById('latitude').innerText = d.latitude || "N/A";
                                    document.getElementById('longitude').innerText = d.longitude || "N/A";
                                }} catch(e) {{ console.log(e); }}
                            }}
                            setInterval(fetchData, 2000);
                            fetchData();

                            function capture(camera_id) {{
                                fetch(`/capture/${{camera_id}}`, {{method:'POST'}})
                                .then(r => r.text())
                                .then(msg => alert(msg))
                                .catch(e => alert("Capture failed: " + e));
                            }}
                        </script>
                    </body>
                </html>
            """)

        @self.app.route('/camera/<int:camera_id>')
        def camera_feed(camera_id):
            if 0 <= camera_id < len(self.camera_indexes):
                return Response(self.generate_frames(camera_id),
                                mimetype='multipart/x-mixed-replace; boundary=frame')
            return "<h1>Camera not available</h1>", 404

        @self.app.route('/data')
        def data():
            return jsonify(self.latest_data)

        @self.app.route('/capture/<int:camera_id>', methods=['POST'])
        def capture(camera_id):
            if 0 <= camera_id < len(self.frames):
                frame = None
                with self.locks[camera_id]:
                    if self.frames[camera_id] is not None:
                        frame = self.frames[camera_id].copy()
                if frame is not None:
                    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    filename = os.path.join(self.save_path, f"camera{camera_id}_{ts}.jpg")

                    # --- Overlay GPS coordinates only ---
                    lat = self.latest_data.get("latitude", "N/A")
                    lon = self.latest_data.get("longitude", "N/A")
                    overlay_text = f"Lat: {lat}, Lon: {lon}"

                    # Black outline
                    cv2.putText(frame, overlay_text, (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                                (0, 0, 0), 4, cv2.LINE_AA)
                    # Yellow text
                    cv2.putText(frame, overlay_text, (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                                (0, 255, 255), 2, cv2.LINE_AA)

                    cv2.imwrite(filename, frame)
                    return f"Saved {filename} with GPS overlay", 200
                else:
                    return "No frame available yet", 400
            return "Invalid camera ID", 404

    def run(self):
        self.app.run(host="0.0.0.0", port=5000, threaded=True)

if __name__ == "__main__":
    droidcams = [
        ("192.168.0.108", 4747)\
        # ("10.34.152.252", 4747)
        # ("192.168.0.133", 4747),
    ]
    rover = Rover(droidcams=droidcams)
    rover.run()
