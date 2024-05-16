from interpreter import read_styles, read_vis
from globalvars import Globals
from cursor import hide

hide()

read_styles("test_style.tss")
read_vis("test.vis")

doc = Globals.__vis_document__

doc.mount()
