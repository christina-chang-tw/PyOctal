import yaml

with open('plot_config.yaml', 'r') as file:
    data = yaml.safe_load(file)

print(data["structure"])