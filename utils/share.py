import random


def get_check_code(num):
    check_code = ''
    for i in range(num):
        index = random.randrange(0, 4)
        if (index != i and index + 1 != i) or index + 1 == i:
            check_code += chr(random.randint(97, 122))
        else:
            check_code += str(random.randint(1, 9))
    return check_code
