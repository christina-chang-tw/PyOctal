from typing import Union

def func(cond: Union[tuple, list] = None):
    try:
        name = "Christina"
        name_list = None

        if isinstance(cond, None):
            return

        if name not in name_list:
            raise ValueError("bad bad")

    except Exception as e:
        print(e)

func()