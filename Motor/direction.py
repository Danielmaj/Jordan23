def forward(power):
    vel = [0,0,-power,power]
    return vel

def backward(power):
    vel = [0,0,power,-power]
    return vel

def right(power):
    vel = [0,0,power,power]
    return vel

def left(power):
    vel = [0,0,-power,-power]
    return vel
def stop():

    vel = [0,0,0,0]
    return vel

def test_all_wheels(power):

    vel = [0,power,power,power]
    return vel

def test_thrower():

    vel = [power,0,0,0]
    return vel
