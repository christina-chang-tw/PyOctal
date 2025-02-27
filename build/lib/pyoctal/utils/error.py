# Error Code Definition
# pylint: disable=C0301
INCOMPATIBLE_OS_ERR = 100
PYTHON_VER_ERROR = 101
RESOURCE_ADDR_UNKNOWN_ERR = 102
RESOURCE_CLASS_UNKNOWN_ERR = 103
HW_TIMEOUT_ERR = 105

PARAM_OUT_OF_RANGE_ERR = 200
PARAM_INVALID_ERR = 201
COND_INVALID_ERR = 202

FOLDER_NOT_EXIST_ERR = 300
FILE_NOT_EXIST_ERR = 301
FILE_EMPTY_ERR = 302

INSTR_NOT_EXIST = 400
INSTR_MATCH_STRING_INCOR = 401

error_message = {
    INCOMPATIBLE_OS_ERR: "OS system incompatible. Please use Windows OS.",
    PYTHON_VER_ERROR: "Python version incompatible. Please use python version >= Python 3.6.",
    RESOURCE_ADDR_UNKNOWN_ERR: "Resource not found. Check your address on NI MAX or Connection Expert",
    RESOURCE_CLASS_UNKNOWN_ERR: "'Resource class not contemplated. Please add this class to the system.",
    HW_TIMEOUT_ERR: "Time out while waiting for hardware unit to respond.",

    PARAM_OUT_OF_RANGE_ERR: "Parameter is out of range.",
    PARAM_INVALID_ERR: "Parameter is invalid.",
    COND_INVALID_ERR: "Condition is invalid.",

    FOLDER_NOT_EXIST_ERR: "Folder does not exist. Please make sure the folder path is valid.",
    FILE_NOT_EXIST_ERR: "File does not exist. Please make sure the file path if valid.",
    FILE_EMPTY_ERR: "File is empty. Nothing can be read from the file.",

    INSTR_NOT_EXIST: "Required instruments for this sweep do not exist. Check instrument address in YAML file.",
    INSTR_MATCH_STRING_INCOR: "Match strings for instruments is incorrect.",
}
