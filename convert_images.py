#!/usr/bin/env python3
"""Convert images (png/jpg/jpeg/webp/bmp/tiff/...) to a target size and save
WebP + AVIF copies of each image.

Features:
  - Accepts one or more image files, or directories (processes all images inside).
  - Center-crops to the target aspect ratio, then resizes to the given size.
  - Saves <name>.webp and <name>.avif next to the source (or into -o dir).
  - Optionally also writes a JPG copy with --also-jpg.
  - AVIF encoding: uses pillow-avif-plugin if installed; otherwise falls back
    to macOS `sips`; if neither works, only WebP is written and a warning shown.

Usage examples:
  python3 convert_images.py photo.png --size 200x273
  python3 convert_images.py ./media --size 200x273 --quality 85 --also-jpg
  python3 convert_images.py a.png b.jpg --size 1200x630 --no-crop
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

SUPPORTED_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff", ".gif"}


def center_crop(im, tw, th):
    """Center-crop to the target aspect ratio (cover)."""
    w, h = im.size
    target_ratio = tw / th
    cur_ratio = w / h
    if cur_ratio > target_ratio:
        # too wide: crop the width
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return im.crop((left, 0, left + new_w, h))
    # too tall: crop the height
    new_h = int(w / target_ratio)
    top = (h - new_h) // 2
    return im.crop((0, top, w, top + new_h))


def to_rgb(im):
    """Flatten to RGB (transparent PNG gets a white background)."""
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        return bg
    return im.convert("RGB")


def save_avif_with_pillow(im, out_path, quality):
    try:
        import pillow_avif  # noqa: F401  # registers the AVIF encoder
        im.save(out_path, "AVIF", quality=quality)
        return True
    except Exception:
        return False


def save_avif_with_sips(im, out_path, quality):
    """Fallback: macOS `sips` can encode AVIF from a temporary PNG."""
    sips = shutil.which("sips")
    if sips is None:
        return False
    tmp = out_path.with_suffix(".tmp.png")
    try:
        im.save(tmp, "PNG")
        subprocess.run(
            [
                sips,
                "-s", "format", "avif",
                "-s", "formatOptions", str(quality),
                str(tmp), "--out", str(out_path),
            ],
            check=True,
            capture_output=True,
        )
        return True
    except Exception:
        return False
    finally:
        if tmp.exists():
            tmp.unlink()


def process_one(img_path, args):
    base = Path(img_path)
    name = base.stem
    outdir = Path(args.outdir) if args.outdir else base.parent
    outdir.mkdir(parents=True, exist_ok=True)

    try:
        im = Image.open(base)
        im.load()
    except Exception as e:
        print(f"  [skip] {base.name}: cannot open ({e})")
        return

    im = to_rgb(im)
    if not args.no_crop:
        im = center_crop(im, args.width, args.height)
    im = im.resize((args.width, args.height), Image.LANCZOS)

    webp_path = outdir / f"{name}.webp"
    im.save(webp_path, "WEBP", quality=args.quality)
    print(f"  [ok] {webp_path}")

    avif_path = outdir / f"{name}.avif"
    if save_avif_with_pillow(im, avif_path, args.quality):
        print(f"  [ok] {avif_path} (pillow-avif-plugin)")
    elif save_avif_with_sips(im, avif_path, args.quality):
        print(f"  [ok] {avif_path} (sips)")
    else:
        print(
            "  [warn] AVIF skipped: install pillow-avif-plugin "
            "(`pip3 install pillow-avif-plugin`) or use a machine with `sips`"
        )

    if args.also_jpg:
        jpg_path = outdir / f"{name}.jpg"
        im.save(jpg_path, "JPEG", quality=args.quality)
        print(f"  [ok] {jpg_path}")


def collect_paths(paths):
    files = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            files.extend(
                f
                for f in p.iterdir()
                if f.is_file() and f.suffix.lower() in SUPPORTED_EXT
            )
        elif p.is_file():
            files.append(p)
        else:
            print(f"[skip] {p}: not found")
    return files


def main():
    parser = argparse.ArgumentParser(
        description="Convert images to a target size and save WebP + AVIF copies."
    )
    parser.add_argument("paths", nargs="+", help="image files or directories")
    parser.add_argument(
        "-s", "--size", default="200x273",
        help="target size WxH, e.g. 200x273 (default: 200x273)",
    )
    parser.add_argument(
        "-o", "--outdir", help="output directory (default: same as input)",
    )
    parser.add_argument(
        "-q", "--quality", type=int, default=85,
        help="encoding quality 1-100 (default: 85)",
    )
    parser.add_argument(
        "--no-crop", action="store_true",
        help="do not center-crop; resize directly (may distort)",
    )
    parser.add_argument(
        "--also-jpg", action="store_true", help="also write a .jpg copy",
    )
    args = parser.parse_args()

    try:
        w, h = (int(x) for x in args.size.lower().split("x"))
    except ValueError:
        parser.error("--size must be like 200x273")
    args.width, args.height = w, h

    files = collect_paths(args.paths)
    if not files:
        print("No images found.")
        sys.exit(1)

    for f in files:
        print(f"== {f} ==")
        process_one(f, args)


if __name__ == "__main__":
    main()
