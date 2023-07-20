import yaml

with open('./config/test.yaml', 'r') as file:
    data = yaml.safe_load(file)

print(data["orc_groups"]["laser_groups"])