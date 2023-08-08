# Error Code Definition

INCOMPATIBLE_OS_ERR = 0x01
PYTHON_VER_ERROR = 0x02
RESOURCE_ADDR_UNKNOWN_ERR = 0x03
RESOURCE_CLASS_UNKNOWN_ERR = 0x04
HW_TIMEOUT_ERR = 0x05
PARAM_OUT_OF_RANGE_ERR = 0x06
PARAM_INVALID_ERR = 0x07
COND_INVALID_ERR = 0x08
UNKNOWN_ADDR_ERR = 0x09
CONNECTION_ERR = 0x10
FOLDER_NOT_EXIST_ERR = 0x1A
FILE_NOT_EXIST_ERR = 0x1B
FILE_EMPTY_ERR = 0x1C
INSTR_NOT_EXIST = 0x1D
INSTR_MATCH_STRING_INCOR = 0x1E

error_message = {
    INCOMPATIBLE_OS_ERR: "OS system incompatible. Please use Windows OS.",
    PYTHON_VER_ERROR: "Python Version too old.",
    RESOURCE_ADDR_UNKNOWN_ERR: "Resource not know, check your address on NI MAX or Connection Expert",
    RESOURCE_CLASS_UNKNOWN_ERR: "'Resource class not contemplated. Please add this class to the system.",
    PYTHON_VER_ERROR: "Python Version too old.",
    HW_TIMEOUT_ERR: "Time out while waiting for hardware unit to respond.",
    PARAM_OUT_OF_RANGE_ERR: "Parameter is out of range.",
    PARAM_INVALID_ERR: "Parameter is invalid.",
    COND_INVALID_ERR: "Condition is invalid.",
    UNKNOWN_ADDR_ERR: "Unknown address.",
    CONNECTION_ERR: "Cannot connect to the instrument.",
    FOLDER_NOT_EXIST_ERR: "Folder does not exist.",
    FILE_NOT_EXIST_ERR: "File does not exist.",
    FILE_EMPTY_ERR: "File is empty.",
    INSTR_NOT_EXIST: "Required instruments for this sweep do not exist. Check YAML file instrument address parameter correspond to the device.",
    INSTR_MATCH_STRING_INCOR: "Match strings for instruments is incorrect.",
}


