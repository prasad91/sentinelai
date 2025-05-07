import os
import xml.etree.ElementTree as ET
import requests
from typing import List, Dict, Optional
from lxml import etree

def get_bom_version(group_id: str, artifact_id: str, parent_version: str) -> Optional[str]:
    url = f"https://repo1.maven.org/maven2/org/springframework/boot/spring-boot-dependencies/{parent_version}/spring-boot-dependencies-{parent_version}.pom"
    response = requests.get(url)
    if response.status_code != 200:
        return None

    root = etree.fromstring(response.content)
    ns = {'m': 'http://maven.apache.org/POM/4.0.0'}

    for dep in root.xpath('.//m:dependencyManagement/m:dependencies/m:dependency', namespaces=ns):
        g = dep.find('m:groupId', namespaces=ns)
        a = dep.find('m:artifactId', namespaces=ns)
        v = dep.find('m:version', namespaces=ns)
        if g is not None and a is not None and v is not None:
            if g.text == group_id and a.text == artifact_id:
                return v.text
    return None

def extract_dependency_info(dep, parent_version, ns, root):
    group_id_el = dep.find('mvn:groupId', ns)
    artifact_id_el = dep.find('mvn:artifactId', ns)
    version_el = dep.find('mvn:version', ns)

    app_group_id = root.find("mvn:groupId", ns)
    app_artifact_id = root.find("mvn:artifactId", ns)
    app_version = root.find("mvn:version", ns)
    app_name = f"{app_group_id.text}:{app_artifact_id.text}:{app_version.text}" if app_artifact_id is not None and app_group_id is not None and app_version is not None else "Unnamed Maven App"

    if group_id_el is not None and artifact_id_el is not None:
        group_id = group_id_el.text.strip()
        artifact_id = artifact_id_el.text.strip()
        version = version_el.text.strip() if version_el is not None else get_bom_version(group_id, artifact_id, parent_version) or "UNKNOWN"

        return {
            'app': app_name,
            'group': group_id,
            'package': artifact_id,
            'version': version,
            'ecosystem': 'maven'
        }
    return None

def get_parent_version(root, ns):
    parent = root.find('mvn:parent', ns)
    if parent is not None:
        group = parent.find('mvn:groupId', ns)
        artifact = parent.find('mvn:artifactId', ns)
        version = parent.find('mvn:version', ns)
        if group is not None and artifact is not None and version is not None:
            if group.text.strip() == "org.springframework.boot" and artifact.text.strip() == "spring-boot-starter-parent":
                return version.text.strip()
    return None

def parse_pom(pom_path: str) -> List[Dict[str, str]]:
    tree = ET.parse(pom_path)
    root = tree.getroot()
    ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
    parent_version = get_parent_version(root, ns)

    dependencies = []
    for dep in root.findall('.//mvn:dependencies/mvn:dependency', ns):
        dependency_info = extract_dependency_info(dep, parent_version, ns, root)
        if dependency_info:
            dependencies.append(dependency_info)

    return dependencies
