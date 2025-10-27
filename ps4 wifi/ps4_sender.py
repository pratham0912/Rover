import pygame
import socket
import json

# -------- CONFIG -----------
RECEIVER_IP = "192.168.1.20"  # change to receiver PC IP
RECEIVER_PORT = 5050
# ---------------------------

pygame.init()
pygame.joystick.init()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Connected to controller: {joystick.get_name()}")

while True:
    pygame.event.pump()

    # Left stick (X, Y)
    left_x = int(joystick.get_axis(0) * 127)
    left_y = int(joystick.get_axis(1) * 127)

    # Right stick (X, Y)
    right_x = int(joystick.get_axis(2) * 127)
    right_y = int(joystick.get_axis(3) * 127)

    # L2 and R2 triggers
    l2 = int(joystick.get_axis(4) * 127)
    r2 = int(joystick.get_axis(5) * 127)

    # D-Pad (hat)
    hat_x, hat_y = joystick.get_hat(0)

    # Buttons (PS4 has 14–16 typically)
    buttons = {}
    for i in range(joystick.get_numbuttons()):
        buttons[f"b{i}"] = joystick.get_button(i)

    data = {
        "left_x": left_x,
        "left_y": left_y,
        "right_x": right_x,
        "right_y": right_y,
        "l2": l2,
        "r2": r2,
        "hat_x": hat_x,
        "hat_y": hat_y,
        "buttons": buttons
    }

    sock.sendto(json.dumps(data).encode(), (RECEIVER_IP, RECEIVER_PORT))
