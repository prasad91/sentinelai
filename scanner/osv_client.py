import requests
from packaging.version import Version, InvalidVersion

def query_osv(package, version, ecosystem):
    print("🔍 Querying OSV for", f"{package}:{version}")
    payload = {
        "version": version,
        "package": {
            "name": f"{package}",
            "ecosystem": ecosystem
        }
    }
    res = requests.post("https://api.osv.dev/v1/query", json=payload)
    if res.status_code != 200:
        return []
    
    vulns = res.json().get("vulns", [])
    return parsed_vulnerabilities(vulns, package, version)

def extract_fix_version(affected):
    for r in affected.get("ranges", []):
        for event in r.get("events", []):
            if "fixed" in event:
                return event["fixed"]
    return None

def is_version_in_range(version: Version, introduced: Version, fixed: Version) -> bool:
    return (not introduced or version >= introduced) and (not fixed or version < fixed)


def is_version_vulnerable(current_version: str, affected_ranges: list) -> bool:
    try:
        current = Version(current_version)
    except InvalidVersion:
        return True  # If version can't be parsed, better to include it

    for affected in affected_ranges:
        if affected.get("type") != "ECOSYSTEM":
            continue

        introduced = next((Version(event["introduced"]) for event in affected.get("events", []) if "introduced" in event), None)
        fixed = next((Version(event["fixed"]) for event in affected.get("events", []) if "fixed" in event), None)

        if is_version_in_range(current, introduced, fixed):
            return True

    return False

def parsed_vulnerabilities(vulns, package, version):
    parsed = []
    for vuln in vulns:
        fix_version = next((extract_fix_version(affected) for affected in vuln.get("affected", [])), None)

        if is_version_vulnerable(version, vuln.get("affected", [])[0].get("ranges", [])):
            parsed.append({
                "id": vuln.get("id"),
                "summary": vuln.get("summary", "No summary"),
                "severity": vuln.get("severity", []),
                "package": package or "Unknown Package",
                "version": version or "Unknown Version",
                "fix_version": fix_version
            })
    
    return parsed
