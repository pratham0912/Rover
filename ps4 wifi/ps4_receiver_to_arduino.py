import socket
import json
import serial
import time

# -------- CONFIG ----------
UDP_IP = "0.0.0.0"
UDP_PORT = 5050
SERIAL_PORT = "COM5"  # change to your Arduino COM
BAUD_RATE = 115200
# --------------------------

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
print(f"Receiver started on UDP {UDP_IP}:{UDP_PORT}")

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)
print(f"Connected to Arduino on {SERIAL_PORT}")

while True:
    data, addr = sock.recvfrom(4096)
    try:
        controller = json.loads(data.decode())

        # Compact message (fits into Serial line easily)
        msg = f"LX:{controller['left_x']} LY:{controller['left_y']} RX:{controller['right_x']} RY:{controller['right_y']} L2:{controller['l2']} R2:{controller['r2']} "
        msg += f"HX:{controller['hat_x']} HY:{controller['hat_y']} "

        # Add all buttons
        for btn, state in controller["buttons"].items():
            msg += f"{btn}:{state} "

        msg += "\n"
        ser.write(msg.encode())

        # Read echo from Arduino
        if ser.in_waiting:
            echo = ser.readline().decode().strip()
            print("From Arduino:", echo)

    except Exception as e:
        print("Error:", e)

# void setup() {
#   Serial.begin(115200);
#   while (!Serial) {;}
# }

# void loop() {
#   if (Serial.available()) {
#     String data = Serial.readStringUntil('\n');
#     Serial.println("ECHO:" + data);
#   }
# }
