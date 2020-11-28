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


def space(start: str, shrink: str, middle: str, end: str, max_len: int):
    start_len = len(start) + len(middle)
    end_len = len(end)
    free_len = max_len - start_len - end_len
    if len(shrink) > free_len:
        shrink = shrink[0:free_len-3] + "..."
    padding = " " * (free_len - len(shrink))
    return start + shrink + middle + padding + end
