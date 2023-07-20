# Configurations

This folder is used for setting up parameters for different testings and graph plotting. YAML file format is used for creating all configuration files and they will be appropriately loaded to the program when a corresponding function is called.

If you are a user, please do not add or remove any parameter! Leave it blank if the variable is not used.

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

Loading above YAML example into python
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