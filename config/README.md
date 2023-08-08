# Configurations

This folder is used for setting up parameters for different testings and graph plotting. YAML file format is used for creating all configuration files and they will be appropriately loaded to the program when a corresponding function is called.

If you are a user, please do not add or remove any base parameter! Leave it blank if the variable is not used.

### Instrument address format

Follow this parameter definitions carefully! If you get an error code of `0x1D`, the parameter which you specify for storing the address of your device is incorrect.

| Parameters  | Device type         | Instruments       |
| ----------- | ------------------- | ----------------- |
| siggen | Signal Generator         | E8257D
| osc    | Oscilloscope             | DSO8000, 86100D
| amp    | Amplifier                | DSP7230, DSP7265
| mm     | Multimeter               | 8163B
| pm     | Power Meter              | E3640A, PM100
| cs     | ComboSource              | 6301
| smu    | Source Measure Unit      | 2400
| vs     | Voltage Source           | 6487
| ld     | Laser Diode              | ITC4002QCL
| dfg    | Dual Function Generator  | TGF3162

Example
```yaml
# In the corresponding YAML file
# one device
instr_addrs:
  vs: "GPIB0::25::INSTR"
  osc: "GPIB0::20::INSTR"

# Two devices of same type
instr_addrs:
  smu: 
    - "GPIB0::25::INSTR"
    - "GPIB0::24::INSTR"
  dfg: "GPIB0::20::INSTR"
```
### Available functions

This table provides information about all callable functions for each type of sweeps. The function that you wish to call can be specified by `func` in a YMAL config file.

| Sweeps      | Functions      | Instruments | Description |
| ----------- | -------------- | ----------- | ----------- |
| passive     | run_ilme       | Agilent8163B, KeysightILME | Use ILME Engine to control the multimeter |
| dc          | run_ilme       | AgilentE3640A, KeysightILME | Use ILME Engine to sweep through the wavelengths and a voltage source to perform dc sweeps|
|             | run_one_source | AgilentE3640A, Agilent8163B | Perform direct loss-wavelength measurement with the multimeter at different voltages |
| iv          | run_7487       | Keithley6487 | Run with Keithley 6487 voltage source |
|             | run_DSP7265    | AgilentE3640A, AmetekDSP7265 | Run with a power meter and a lock-in amplifier |
|             | run_dual_DSP7265 | AgilentE3640Ax2, AmetekDSP7265 | Run with two power meters and a lock-in amplifier
|             | run_E3640A | AgilentE3640A | Run with only the power meter |
|             | run_2400   | Keithley2400  | Run with only the SMU


### How to write a YAML configuration file
**IMPORTANT:** YAML best practice is to use two spaces rather than tab for indentation as using tab may cause parsing errors.

YAML stores objects as a collection of key and value pairs. In YAML, strings do not need the quotation mark unless representing numbers in string. However, for the users' easiness of understanding the code, it should be standardised to always use quotation mark for strings on the right-hand side.

YAML example:
```yaml
--- # document starts
# assign a value to a variable 
name: "ORC"
year: "2023"

# creating a list
siph_groups:
  - "mid_infrared"
  - "modulators"
  - "sensors"

# creating a dictionary
orc_groups:
  siph_groups: 
    - "mid_infrared"
    - "modulators"
    - "sensors"
  fibre_groups:
    - "non_linear"
    - "high_power"
    - "communication"
  laser_groups:
    - "high_power"
    - "pulsed"
    - "planar"
... # document ends
```

Python equivalent:
```python
# assign a value to a variable 
name = "ORC"
year = "2023"

# creating a list
siph_groups = ["mid_infrared", "modulators", "sensors"]

# creating a dictionary of lists
orc_groups = {
    "siph_groups" : ["mid_infrared", "modulators", "sensors"],
    "fibre_groups" : ["non_linear", "high_power", "communication"]
    "laser_groups" : ["high_power", "pulsed", "planar"]
}
```

The output of the above YAML example after loaded into Python. You may be able to recognise that the Python output is syntatically identical to JSON format.
```python
# Everything becomes a dictionary simply a key-value pair. To access a value, simply types in the correct key.
{
    # variables
    'name': 'ORC', 
    'year': '2023', 

    # list
    'siph_groups': ['mid_infrared', 'modulators', 'sensors'], 

    # dictionary
    'orc_groups': 
    {
        'siph_groups': ['mid_infrared', 'modulators', 'sensors'], 
        'fibre_groups': ['non_linear','high_power', 'communication'], 
        'laser_groups': ['high_power', 'pulsed', 'planar']
    }
}
```

How to load and access data?
```python
import yaml # import yaml python module

with open("path/to/yaml/file", 'r') as file:
    data = yaml.safe_load(file)

# access "name" variable
name = data["name"]

# access "laser_groups" array under "orc_groups"
laser_groups = data["orc_groups"]["laser_groups"]
```