def validatesInt(s):
    try:
        int(s)
        return True
    except ValueError:
        print("Invalid Selection: due to invalid characters, use one digit only.")
        return False
