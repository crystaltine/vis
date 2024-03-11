# all unicode block elements
from utils import fcode, cls

print("▀▁▂▃▄▅▆▇█▉▊▋▌▍▎▏")
print("▐░▒▓▔▕▖▗▘▙▚▛▜▝▞▟")
print("■□▢▣▤▥▦▧▨▩▪▫▬▭▮▯")
print("▰▱▲△▴▵▶▷▸▹►▻▼▽▾▿")
print("◀◁◂◃◄◅◆◇◈◉◊○◌◍◎")
print("●◐◑◒◓◔◕◖◗◘◙◚◛◜◝◞◟")
print("◠◡◢◣◤◥◦◧◨◩◪◫◬◭◮◯")
print("◰◱◲◳◴◵◶◷◸◹◺◻◼◽◾◿")
print("⬒⬓⬔⬕⬖⬗⬘⬙⬚⬛⬜⬝⬞⬟")
print("⬠⬡⬢⬣⬤⬥⬦⬧⬨⬩⬪⬫⬬⬭⬮⬯")
print("⬰⬱⬲⬳⬴⬵⬶⬷⬸⬹⬺⬻⬼⬽⬾⬿")

# edges
print(f"└┘┐────┌┴┬┤├┼")

print("◜──────◝")
print("│      │")
print("│      │")
print("│      │")
print("◟──────◞")
#      R L D U F
print("▐ ▌ ▄ ▀ █")
print("▖▝▗ ▘▙ ▟ ▛ ▜  ▞ ▚  ")

A = [
    "█▀█",
    "█▀█",
    "▀ ▀"
]
B = [
    "█▀▙",
    "█▀▙",
    "▀▀▘"
]
C = [
    "▟▛▀",
    "█▖ ",
    "▝▀▀"
]
    
    
L = [
   "█  ",
   "█  ",
   "▀▀▀" 
]
O = [
    "▟▀▙",
    "█ █",
    "▝▀▘"
]
G = [
    "▟▀▀",
    "█▝█",
    "▝▀▀"
]
I = [
    "▀█▀",
    " █ ",
    "▀▀▀"
]
N = [
    "█▖█",
    "█▜█",
    "▀ ▀"
]

print()

# add up A B C elementwise to do horizontal rendering
login = [L, O, G, I, N]

for i in range(len(login[0])):
    print(" ".join([login[j][i] for j in range(len(login))]))
