from interpreter import read_styles, read_vis

read_styles("main_menu.tss")


from globalvars import Globals

read_vis("main_menu.vis")

document = Globals.__vis_document__

document.mount()