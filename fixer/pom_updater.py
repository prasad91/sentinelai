import xml.etree.ElementTree as ET

def update_pom(pom_path, group_id, artifact_id, new_version):
    tree = ET.parse(pom_path)
    root = tree.getroot()
    ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}

    found = False

    for dep in root.findall(".//mvn:dependency", ns):
        gid = dep.find("mvn:groupId", ns)
        aid = dep.find("mvn:artifactId", ns)
        ver = dep.find("mvn:version", ns)

        if gid is not None and aid is not None and ver is not None:
            if gid.text == group_id and aid.text == artifact_id:
                ver.text = new_version
                found = True
                print(f"✅ Updated {group_id}:{artifact_id} to version {new_version}")

    if found:
        tree.write(pom_path)
    else:
        print(f"⚠️ Dependency {group_id}:{artifact_id} not found in {pom_path}")
