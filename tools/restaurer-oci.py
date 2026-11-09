"""Restore the pinned, locally supplied OCI layouts. No network or Docker calls."""

import argparse
import hashlib
import io
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import zipfile


ROOT = Path(__file__).resolve().parents[1] / "demonstrateur"
OUTER = "f0ffe32b0ae709b842b189d224db990ca1697c73f9cbe6040821ab57f345fedb"
INNER = "a44ecd91ec0ac8b0ebf91d2916e83599ffd198d38dffa068c38da073615143de"
INNER_NAME = "THIGA-Livraison-Corrigee-2026-11-09.zip"


def manifest(data):
    return {name: digest for digest, name in (
        line.split("  ", 1) for line in data.decode("utf-8").splitlines()
    )}


def verify_layouts(archive):
    sealed = manifest(archive.read("SHA256SUMS"))
    if len(sealed) != 79 or set(sealed) != set(archive.namelist()) - {"SHA256SUMS"}:
        raise ValueError("Manifeste technique incomplet.")
    for name, digest in sealed.items():
        with archive.open(name) as stream:
            if hashlib.file_digest(stream, "sha256").hexdigest() != digest:
                raise ValueError(f"Empreinte technique divergente : {name}")

    for name, digest in manifest((ROOT / "RUNTIME-SHA256SUMS").read_bytes()).items():
        path = ROOT / name
        if not path.is_file() or sealed.get(name) != digest or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"Source locale absente ou différente du paquet : {name}")

    return sorted(name for name in sealed if name.startswith(("vendor/app/", "vendor/guard/")))


def restore(archive, members):
    vendor = ROOT / "vendor"
    if vendor.is_symlink() or (hasattr(vendor, "is_junction") and vendor.is_junction()) or vendor.resolve() != ROOT.resolve() / "vendor":
        raise ValueError("Le dossier vendor doit appartenir à cette copie locale.")
    existing = [vendor / name for name in ("app", "guard") if os.path.lexists(vendor / name)]
    if existing:
        raise ValueError("Bases déjà présentes. Utiliser une copie neuve pour éviter un écrasement.")

    with TemporaryDirectory(prefix="thiga-oci-", dir=vendor) as tmp:
        staging = Path(tmp)
        for member in members:
            relative = Path(member).relative_to("vendor")
            target = staging / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as src, target.open("xb") as dst:
                shutil.copyfileobj(src, dst)
        for name in ("app", "guard"):
            (staging / name).rename(vendor / name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="ZIP de remise ou ZIP technique déjà obtenu")
    parser.add_argument("--verifier-seulement", action="store_true", help="vérifier sans écrire")
    args = parser.parse_args()
    with args.archive.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest not in {OUTER, INNER}:
        raise ValueError("Empreinte du ZIP inconnue.")
    with zipfile.ZipFile(args.archive) as original:
        raw = original.read(INNER_NAME) if digest == OUTER else None
        if raw is not None and hashlib.sha256(raw).hexdigest() != INNER:
            raise ValueError("Empreinte du ZIP technique divergente.")
        with zipfile.ZipFile(io.BytesIO(raw) if raw is not None else args.archive) as technical:
            members = verify_layouts(technical)
            if not args.verifier_seulement:
                restore(technical, members)
    print(f"{len(members)} membres OCI vérifiés" + ("." if args.verifier_seulement else " et restaurés."))


if __name__ == "__main__":
    main()
