import json

def parse_package_json(file_path):
    dependencies = []

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            app_name = data.get("name", "Unnamed npm App")
            app_version = data.get("version", "Unnamed npm App")

            all_deps = {}

            if "dependencies" in data:
                all_deps.update(data["dependencies"])
            if "devDependencies" in data:
                all_deps.update(data["devDependencies"])

            for name, version in all_deps.items():
                cleaned_version = version.lstrip("^~>=< ")
                dependencies.append({
                    "app": f"{app_name}:{app_version}",
                    "package": name,
                    "version": cleaned_version,
                    "ecosystem": "npm"
                })

    except Exception as e:
        print(f"❌ Error parsing package.json: {e}")

    return dependencies
