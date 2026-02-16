# run.py - Backend Factory V1 Test Runner & Generator

import json
import os
import hashlib
import argparse
import subprocess
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).parent
SPEC_DIR = BASE_DIR / "specs"
TEMPLATE_DIR = BASE_DIR / "templates"
GENERATED_DIR = BASE_DIR / "generated"

# -----------------------------
# Example Specs (JSON)
# -----------------------------
VALID_SPEC = {
    "specVersion": "1.0",
    "entities": [
        {
            "name": "User",
            "fields": [
                {"name": "id", "type": "uuid", "primaryKey": True},
                {"name": "email", "type": "string"},
                {"name": "created_at", "type": "datetime"}
            ]
        },
        {
            "name": "Post",
            "fields": [
                {"name": "id", "type": "uuid", "primaryKey": True},
                {"name": "title", "type": "string"},
                {"name": "author_id", "type": "uuid"}
            ]
        }
    ]
}

INVALID_SPEC = {
    "specVersion": "0.9",  # invalid version
    "entities": [
        {"name": "User", "fields": [{"name": "id", "type": "uuid"}]},
        {"name": "User", "fields": [{"name": "email", "type": "string"}]}
    ]
}

# -----------------------------
# Validator
# -----------------------------
def validate_spec(spec):
    errors = []
    if spec.get("specVersion") != "1.0":
        errors.append("Invalid specVersion")
    names = set()
    for entity in spec.get("entities", []):
        if "primaryKey" not in [f.get("primaryKey", False) for f in entity.get("fields", [])]:
            errors.append(f"Entity {entity['name']} missing primary key")
        if entity["name"] in names:
            errors.append(f"Duplicate entity name: {entity['name']}")
        names.add(entity["name"])
        if len(entity.get("fields", [])) > 4:
            errors.append(f"Warning: entity {entity['name']} has >4 fields")
    return errors

# -----------------------------
# Code Generator
# -----------------------------
def generate_code(spec, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape()
    )
    for entity in spec.get("entities", []):
        # Python model
        template_py = env.get_template("python/model.py.j2")
        code_py = template_py.render(entity=entity)
        with open(output_dir / f"{entity['name']}.py", "w") as f:
            f.write(code_py)
        # Java model
        template_java = env.get_template("java/Model.java.j2")
        code_java = template_java.render(entity=entity)
        with open(output_dir / f"{entity['name']}.java", "w") as f:
            f.write(code_java)

# -----------------------------
# Deterministic Hash Check
# -----------------------------
def deterministic_hash(output_dir):
    hashes = {}
    for file in sorted(output_dir.glob("**/*")):
        if file.is_file():
            with open(file, "rb") as f:
                content = f.read()
                h = hashlib.md5(content).hexdigest()
                hashes[str(file)] = h
    return hashes

# -----------------------------
# E2E Tests
# -----------------------------
def e2e_tests(output_dir):
    print("\n[+] Running E2E Tests...")
    # Python syntax check
    for py_file in output_dir.glob("*.py"):
        try:
            subprocess.check_call(["python", "-m", "py_compile", str(py_file)])
        except subprocess.CalledProcessError:
            print(f"[X] Python syntax error: {py_file}")
            return False
    print("[✓] Python syntax check passed")

    # Java compile check (requires javac)
    for java_file in output_dir.glob("*.java"):
        try:
            subprocess.check_call(["javac", str(java_file)])
        except subprocess.CalledProcessError:
            print(f"[X] Java compile error: {java_file}")
            return False
    print("[✓] Java compilation check passed")
    return True

# -----------------------------
# Main CLI
# -----------------------------
def main():
    parser = argparse.ArgumentParser(description="Backend Factory V1 Runner & Test")
    parser.add_argument("--spec", type=str, default="valid_spec.json", help="Path to spec JSON")
    parser.add_argument("--out", type=str, default="generated", help="Output directory")
    parser.add_argument("--mode", type=str, default="test", choices=["test", "generate"], help="Mode: test or generate")
    args = parser.parse_args()

    # Load spec
    spec_path = SPEC_DIR / args.spec
    if not spec_path.exists():
        if args.spec == "valid_spec.json":
            spec_path.write_text(json.dumps(VALID_SPEC, indent=2))
        elif args.spec == "invalid_spec.json":
            spec_path.write_text(json.dumps(INVALID_SPEC, indent=2))
        print(f"[i] Spec file created: {spec_path}")

    with open(spec_path) as f:
        spec = json.load(f)

    # Validate
    errors = validate_spec(spec)
    if errors:
        print("[!] Validation Errors / Warnings:")
        for e in errors:
            print(f" - {e}")
        if args.mode == "generate":
            print("[X] Code generation blocked due to validation errors")
            return

    # Generate code
    out_dir = Path(args.out)
    generate_code(spec, out_dir)
    print(f"[✓] Code generated in {out_dir}")

    # E2E Tests
    if args.mode == "test":
        hashes_before = deterministic_hash(out_dir)
        success = e2e_tests(out_dir)
        hashes_after = deterministic_hash(out_dir)
        if hashes_before != hashes_after:
            print("[!] Warning: Code not deterministic")
        if success:
            print("[✓] All E2E tests passed")
        else:
            print("[X] E2E tests failed")

if __name__ == "__main__":
    main()
