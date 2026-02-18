import sys
import os
import argparse
import random
from pathlib import Path
from typing import Iterable, Optional
import zipfile
from PIL import Image, ImageEnhance

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
}

def zip_folder(folder_path: Path) -> Path:
    """
    Zips the entire folder and returns the zip file path.
    """
    zip_path = folder_path.with_suffix('.zip')

    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in folder_path.rglob('*'):
            if file.is_file():
                arcname = file.relative_to(folder_path)
                zipf.write(file, arcname)

    return zip_path



def random_signed_delta(rng: random.Random, min_percent: float, max_percent: float) -> float:
    pct = rng.uniform(min_percent, max_percent) / 100.0
    return pct if rng.random() < 0.5 else -pct


def apply_gamma(image: Image.Image, gamma_factor: float) -> Image.Image:
    if gamma_factor <= 0:
        gamma_factor = 1.0
    inv_gamma = 1.0 / gamma_factor

    table = [int(((i / 255.0) ** inv_gamma) * 255.0 + 0.5) for i in range(256)]

    if image.mode == "RGBA":
        r, g, b, a = image.split()
        rgb = Image.merge("RGB", (r, g, b)).point(table * 3)
        r2, g2, b2 = rgb.split()
        return Image.merge("RGBA", (r2, g2, b2, a))

    if image.mode not in {"RGB", "L"}:
        image = image.convert("RGB")

    if image.mode == "L":
        return image.point(table)

    return image.point(table * 3)


def tweak_image(
    input_path: Path,
    output_path: Path,
    rng: random.Random,
    min_percent: float,
    max_percent: float,
) -> tuple[float, float, float, float]:
    brightness_delta = random_signed_delta(rng, min_percent, max_percent)
    contrast_delta = random_signed_delta(rng, min_percent, max_percent)
    saturation_delta = random_signed_delta(rng, min_percent, max_percent)
    gamma_delta = random_signed_delta(rng, min_percent, max_percent)

    brightness_factor = max(0.05, 1.0 + brightness_delta)
    contrast_factor = max(0.05, 1.0 + contrast_delta)
    saturation_factor = max(0.0, 1.0 + saturation_delta)
    gamma_factor = max(0.05, 1.0 + gamma_delta)

    with Image.open(input_path) as img:
        out = img.copy()
        out = ImageEnhance.Brightness(out).enhance(brightness_factor)
        out = ImageEnhance.Contrast(out).enhance(contrast_factor)
        out = ImageEnhance.Color(out).enhance(saturation_factor)
        out = apply_gamma(out, gamma_factor)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        out.save(output_path)

    return brightness_delta, contrast_delta, saturation_delta, gamma_delta


def is_supported_image(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS


def resolve_input_file(user_value: str, script_dir: Path, input_dir: Path) -> Path:
    raw = Path(user_value).expanduser()
    candidates = []

    if raw.is_absolute():
        candidates.append(raw)
    else:
        candidates.append((Path.cwd() / raw))
        candidates.append((script_dir / raw))
        candidates.append((input_dir / raw.name))

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    raise FileNotFoundError(f"Input file not found: {user_value}")


def get_batch_inputs(input_dir: Path) -> Iterable[Path]:
    return sorted([p for p in input_dir.iterdir() if is_supported_image(p)], key=lambda p: p.name.lower())


def build_output_path(output_dir: Path, source_path: Path) -> Path:
    base = output_dir / f"{source_path.stem}_random{source_path.suffix.lower()}"
    if not base.exists():
        return base

    i = 1
    while True:
        candidate = output_dir / f"{source_path.stem}_random_{i}{source_path.suffix.lower()}"
        if not candidate.exists():
            return candidate
        i += 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Randomly tweak image brightness/contrast/saturation/gamma by 5-15% (up or down). "
            "By default, reads all images from ./input and writes to ./output."
        )
    )
    parser.add_argument(
        "--input",
        default=None,
        help="Optional single input image path. If omitted, all supported images in ./input are processed.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help=(
            "Optional output file path for single input mode, or output directory for batch mode. "
            "Defaults to ./output next to this script."
        ),
    )
    parser.add_argument("--min-percent", type=float, default=5.0, help="Minimum random change percent (default: 5)")
    parser.add_argument("--max-percent", type=float, default=15.0, help="Maximum random change percent (default: 15)")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed for reproducible output.")
    parser.add_argument(
        "--folder",
        help="Folder containing images to process"
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    script_dir = Path(args.folder).resolve()
    input_dir = script_dir
    output_dir = script_dir / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.min_percent < 0 or args.max_percent < 0:
        print("min/max percent must be non-negative.", file=sys.stderr)
        return 1
    if args.min_percent > args.max_percent:
        print("min-percent cannot be greater than max-percent.", file=sys.stderr)
        return 1

    rng = random.Random(args.seed)

    try:
        if args.input:
            source = resolve_input_file(args.input, script_dir, input_dir)
            if not is_supported_image(source):
                print(f"Unsupported file extension: {source}", file=sys.stderr)
                return 1

            if args.output:
                user_output = Path(args.output).expanduser()
                if user_output.suffix:
                    out_path = user_output if user_output.is_absolute() else (script_dir / user_output)
                else:
                    out_dir = user_output if user_output.is_absolute() else (script_dir / user_output)
                    out_path = build_output_path(out_dir, source)
            else:
                out_path = build_output_path(output_dir, source)

            deltas = tweak_image(source, out_path, rng, args.min_percent, args.max_percent)
            print(
                f"{source.name} -> {out_path}\n"
                f"  brightness={deltas[0] * 100:+.2f}% "
                f"contrast={deltas[1] * 100:+.2f}% "
                f"saturation={deltas[2] * 100:+.2f}% "
                f"gamma={deltas[3] * 100:+.2f}%"
            )
            return 0

        batch_inputs = list(get_batch_inputs(input_dir))
        if not batch_inputs:
            print(f"No supported images found in: {input_dir}")
            return 0

        if args.output:
            user_output = Path(args.output).expanduser()
            batch_output_dir = user_output if user_output.is_absolute() else (script_dir / user_output)
        else:
            batch_output_dir = output_dir
        batch_output_dir.mkdir(parents=True, exist_ok=True)

        for source in batch_inputs:
            out_path = build_output_path(batch_output_dir, source)
            deltas = tweak_image(source, out_path, rng, args.min_percent, args.max_percent)
            print(
                f"{source.name} -> {out_path}\n"
                f"  brightness={deltas[0] * 100:+.2f}% "
                f"contrast={deltas[1] * 100:+.2f}% "
                f"saturation={deltas[2] * 100:+.2f}% "
                f"gamma={deltas[3] * 100:+.2f}%"
            )

        zip_folder(output_dir)
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
