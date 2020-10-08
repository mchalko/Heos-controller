

def formatstr(string, separator):
    return string.replace("\\", "\\\\").replace(separator, "\\" + separator)


def split(string, separator):
    result = []
    state = 0
    word = ""
    for letter in string :
        if state == 0 : # normal operation
            if letter == separator :
                result.append(word)
                word = ""
            elif letter == "\\" :
                state = 1
            else :
                word += letter
        elif state == 1: # after \
            word += letter
            state = 0
    result.append(word)
    return result


