from random import randint

def calc_time(time):
    minutes = time // 6000
    seconds = (time % 6000) // 100
    milisec = (time % 6000) % 100 // 1

    return minutes, seconds, milisec

def time_string(time):
    if time == -1:
        return "-"

    if time == 0:
        return "DNF"

    minutes = time // 6000
    seconds = (time % 6000) // 100
    milisec = (time % 6000) % 100 // 1

    time_str = "{minutes:02d}:{seconds:02d}.{milisec:02d}".format(minutes=minutes, seconds=seconds, milisec=milisec)

    return time_str


moves = ['U', 'D', 'R', 'L', 'F', 'B']
direction = ['', "'", "2"]

def scramble_gen(scramble_length):
    arr = [[0, 0] for _ in range(scramble_length)]
    arr[0][0] = moves[randint(0, 5)]
    arr[0][1] = direction[randint(0, 2)]
    i = 1
    while(i < scramble_length):
        arr[i][0] = moves[randint(0, 5)]
        arr[i][1] = direction[randint(0, 2)]
        if arr[i-1][0] == arr[i][0]:
            continue
        i += 1
    scramble = "  ".join([a[0]+a[1] for a in arr])
    return scramble
