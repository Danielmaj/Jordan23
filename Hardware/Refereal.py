from mainboard import ComportMainboard
try:
    com = ComportMainboard()
    com.open()
    while True:
        com.Readmsgs(verbos=True)
finally:
    com.close()
