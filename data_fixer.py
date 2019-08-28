

def passport_fixer(data):
    try:
        # first letter is not number
        if data[0:1] == "6":
            data = data.replace("6", "G")
    except Exception as identifier:
        pass
    return data