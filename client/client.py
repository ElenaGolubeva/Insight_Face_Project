import socket
import json
import pygame
import cv2
import numpy as np
import base64

TCP_IP = '127.0.0.1'
TCP_PORT = 8080

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

while True:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))

        received_data = b''
        while True:
            try:
                data = s.recv(16384)
                if not data:
                    break
                received_data += data
                try:
                    image_data = json.loads(received_data.decode())
                    image_b64 = image_data['image']
                    image_bytes = base64.b64decode(image_b64)
                    print("Received image data")

                    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)

                    image_surface = pygame.image.frombuffer(image.tobytes(), image.shape[1::-1], 'BGR')

                    screen.blit(image_surface, (0, 0))
                    pygame.display.flip()

                    received_data = b''
                except json.JSONDecodeError:
                    pass
            except Exception as e:
                print(f"Error receiving data from TCP server: {e}")
                break

        s.close()
    except Exception as e:
        print(f"Error connecting to TCP server: {e}")
        break

    # Обработка события закрытия окна
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
