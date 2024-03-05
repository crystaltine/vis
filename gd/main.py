from render.camera import Camera
from engine.level import Level
from time import sleep

thing = Level()
camera = Camera(thing)

camera.render_init()

for i in range(200):
    camera.left += 0.25
    camera.render()
    sleep(1/30)