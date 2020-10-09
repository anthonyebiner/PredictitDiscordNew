def convert(lst: list) -> str:
    """
    convert list to string
    :param lst: list
    :return: string
    """
    string = ""
    for n in lst:
        string += str(n)
    return string


def opt_shares(cost: float) -> float:
    return 1.0 / (1.0 - (1.0 - float(cost)) * 0.1)
