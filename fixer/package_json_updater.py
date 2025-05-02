import json

def update_package_json(file_path, package_name, new_version):
    with open(file_path, "r") as f:
        data = json.load(f)

    for section in ["dependencies", "devDependencies"]:
        if section in data and package_name in data[section]:
            data[section][package_name] = new_version

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
