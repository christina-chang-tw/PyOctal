from lib.util.util import *

def test_platform():
    platform_check()

def test_version():
    pyversion_check()

def test_get_func():
    def func():
        return get_func_name()
    assert func.__name__ == func()

def test_package_info():
    dictonary = {
        "name": "ORC group",
        "year": "2023",
        "month": "July",
    }
    df_packaged = package_info(dictonary)

    df = pd.DataFrame()
    df["Params"] = ("name", "year", "month")
    df["Value"] = ("ORC group", "2023", "July")

    assert df.equals(df_packaged)

def test_folder_ops():
    path = "./tests/TEST"
    create_folder(path)
    assert os.path.isdir(path)
    delete_folder(path)
    assert not os.path.isdir(path)


if __name__ == "__main__":
    pass