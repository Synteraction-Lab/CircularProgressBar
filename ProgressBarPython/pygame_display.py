# coding=utf-8

import pygame
import cv2

DISPLAY_HEIGHT = 1080
DISPLAY_WIDTH = 1920

DISPLAY_FPS = 25

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)

DISPLAY_FONT = 'arial'
DISPLAY_FONT_SIZE = 100

display_surface = None
display_info = None
display_font = None

face_image = None

# sync time
display_clock = pygame.time.Clock()


# see https://www.pygame.org/docs/ref/display.html#pygame.display.init
def start():
    global display_surface, display_info, display_font, face_image

    pygame.init()
    display_surface = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT),
                                              flags=pygame.FULLSCREEN | pygame.NOFRAME, display=1)
    display_info = pygame.display.Info()
    print(display_info)
    display_font = pygame.font.SysFont(DISPLAY_FONT, DISPLAY_FONT_SIZE)
    # pygame.display.flip()

    face_image = pygame.image.load('img/face_circle.png')
    face_image = pygame.transform.scale(face_image,
                                        (display_info.current_w, display_info.current_h))


def stop():
    pygame.quit()


def reset():
    display_surface.fill(COLOR_BLACK)
    pygame.display.update()
    # pygame.display.flip()


def show_image_file(image_name, full_screen):
    img = pygame.image.load(image_name)
    _show_image(img, full_screen)


# image = pygame image object
def _show_image(image, full_screen):
    img = image
    if full_screen:
        img = pygame.transform.scale(img, (display_info.current_w, display_info.current_h))
    display_surface.blit(img, (0, 0))
    pygame.display.update()


def show_face_image():
    display_surface.blit(face_image, (0, 0))
    pygame.display.update()


video_capture = None


def set_video():
    global video_capture
    video_capture = cv2.VideoCapture('img/video2_2.mp4')


def _show_video_frame(frame, full_screen):
    shape = frame.shape[1::-1]
    img = pygame.image.frombuffer(frame.tobytes(), shape, "BGR")
    _show_image(img, full_screen)


# set_video() before this
def play_video():
    display_clock.tick(DISPLAY_FPS)
    success, frame = video_capture.read()
    if success:
        _show_video_frame(frame, True)
    else:
        set_video()


def reset_video():
    video_capture.release()
    cv2.destroyAllWindows()


def get_center_text_position(text):
    screen_w = display_info.current_w
    screen_h = display_info.current_h
    return (
        int(screen_w / 2 - (len(text) / 2) * (screen_w / 55)),
        int(screen_h / 2 - screen_h * 2 / 32))


def show_text(text):
    text_surface = display_font.render(text, False, COLOR_WHITE)
    display_surface.blit(text_surface, get_center_text_position(text))
    pygame.display.update()
