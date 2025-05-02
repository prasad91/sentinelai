import xml.etree.ElementTree as ET

def parse_pom(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
    
    app_group_id = root.find("mvn:groupId", ns)
    app_artifact_id = root.find("mvn:artifactId", ns)
    app_version = root.find("mvn:version", ns)
    app_name = f"{app_group_id.text}:{app_artifact_id.text}:{app_version.text}" if app_artifact_id is not None and app_group_id is not None and app_version is not None else "Unnamed Maven App"

    dependencies = []

    for dep in root.findall(".//mvn:dependency", ns):
        group_id = dep.find("mvn:groupId", ns).text
        artifact_id = dep.find("mvn:artifactId", ns).text
        version = dep.find("mvn:version", ns)
        version_text = version.text if version is not None else None

        dependencies.append({
            "app": app_name,
            "package": f"{group_id}:{artifact_id}",
            "version": version_text,
            "ecosystem": "Maven"
        })

    return dependencies
