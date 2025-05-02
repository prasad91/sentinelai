import re

def parse_requirements(file_path):
    dependencies = []
    app_name = "vuln-python-app"
    app_version = "0.0.1"

    try:
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue  # Skip comments and empty lines

                match = re.match(r'^([\w\-.]+)==([\w\-.]+)', line)
                if match:
                    name, version = match.groups()
                    dependencies.append({
                        "app": f"{app_name}:{app_version}",
                        "package": name,
                        "version": version,
                        "ecosystem": "PyPI"
                    })

    except Exception as e:
        print(f"❌ Error parsing requirements.txt: {e}")

    return dependencies
