from render.camera import Camera
from engine.objects import OBJECTS
from time import sleep

leveldata = [
    [],
    [],
    [],
    [],
    [OBJECTS.block, OBJECTS.block],
    [OBJECTS.spike],
    [OBJECTS.spike],
    [OBJECTS.spike],
    [],
    [],
    [],
    [],
    [OBJECTS.spike],
]
camera = Camera(leveldata)

camera.render_init()

for i in range(200):
    camera.left += 0.25
    camera.render()
    sleep(1/30)