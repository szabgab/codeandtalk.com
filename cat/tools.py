
def in_sec(length):
    parts = [int(x) for x in length.split(':')]
    sec = 0
    #print(parts)
    while len(parts) > 0:
        sec *= 60
        sec += parts.pop(0)
    return sec

# vim: expandtab
