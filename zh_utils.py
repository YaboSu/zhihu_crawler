def parse_num(text):
    if text[-1] == 'K':
        return int(float(text[:-1])*1000)
    else:
        return int(text)
