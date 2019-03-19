def GetCorrectAnswer(counter):
    if int(counter)%3 == 0:
        return "pass"
    elif '3' in str(counter):
        return "pass"
    else:
        return counter