def update_requirements_txt(file_path, package_name, new_version):
    lines = []
    found = False

    with open(file_path, "r") as f:
        for line in f:
            if line.startswith(f"{package_name}=="):
                lines.append(f"{package_name}=={new_version}\n")
                found = True
            else:
                lines.append(line)

    if found:
        with open(file_path, "w") as f:
            f.writelines(lines)
    else:
        raise ValueError(f"{package_name} not found in {file_path}")
