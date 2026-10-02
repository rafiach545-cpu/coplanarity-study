import hashlib, os

root = "/home/rafia/coplanarity_study/05_coplanarity_analysis/FULL_STATISTICAL_AUDIT_1000_2000_v1"
lines = []
for dirpath, dirnames, filenames in os.walk(root):
    dirnames.sort()
    for fn in sorted(filenames):
        if fn == "SHA256_MANIFEST.txt":
            continue
        p = os.path.join(dirpath, fn)
        h = hashlib.sha256()
        with open(p, "rb") as f:
            h.update(f.read())
        rel = os.path.relpath(p, root)
        lines.append(f"{h.hexdigest()}  ./{rel}")

with open(os.path.join(root, "SHA256_MANIFEST.txt"), "w") as f:
    f.write("\n".join(lines) + "\n")

print(f"Wrote {len(lines)} hashes.")
for l in lines:
    print(l)
