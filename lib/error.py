# Error Code Definition

INCOMPATIBLE_OS_ERR = 0x01
PYTHON_VER_ERROR = 0x02
HW_TIMEOUT_ERR = 0x03
PARAM_OUT_OF_RANGE_ERR = 0x04
PARAM_INVALID_ERR = 0x05
UNKNOWN_ADDR_ERR = 0x06
CONNECTION_ERR = 0x07
FOLDER_NOT_EXIST_ERR = 0x08
FILE_NOT_EXIST_ERR = 0x08

error_message = {
    INCOMPATIBLE_OS_ERR: "OS system incompatible. Please use Windows OS.",
    PYTHON_VER_ERROR: "Python Version too old.",
    HW_TIMEOUT_ERR: "Time out while waiting for hardware unit to respond.",
    PARAM_OUT_OF_RANGE_ERR: "Parameter is out of range.",
    PARAM_INVALID_ERR: "Parameter is invalid.",
    UNKNOWN_ADDR_ERR: "Unknown address.",
    CONNECTION_ERR: "Cannot connect to the instrument.",
    FOLDER_NOT_EXIST_ERR: "Folder does not exist.",
    FILE_NOT_EXIST_ERR: "File does not exist."
}


