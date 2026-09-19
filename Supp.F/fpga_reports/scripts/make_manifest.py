#!/usr/bin/env python3
"""Build manifest.json and SHA256SUMS for the reports tree."""
import hashlib, json, sys
from pathlib import Path

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    manifest, sums = {}, []
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix in {".rpt", ".csv", ".log", ".xdc", ".tcl"}:
            rel = str(p.relative_to(root))
            digest = sha256(p)
            manifest[rel] = {"sha256": digest, "size": p.stat().st_size}
            sums.append(f"{digest}  {rel}")
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2))
    (root / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    print(f"Wrote manifest.json ({len(manifest)} files) and SHA256SUMS")

if __name__ == "__main__":
    main()