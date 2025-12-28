import json
import logging
import os
import sys
import argparse
from pathlib import Path


def _repo_root() -> Path:
    # backend/scripts/run.py -> backend/scripts -> backend -> repo root
    return Path(__file__).resolve().parents[2]


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    repo_root = _repo_root()

    # Ensure backend/src is importable (agents.*)
    backend_src = repo_root / "backend" / "src"
    sys.path.insert(0, str(backend_src))

    from agents.spec_pipeline.core.discovery import discover  # noqa: WPS433
    from agents.spec_pipeline.core.registry import load_plugin  # noqa: WPS433

    parser = argparse.ArgumentParser()
    parser.add_argument("--brand", default="canon")
    parser.add_argument("--product-type", default="camera")
    parser.add_argument("--stage", default="discovery", choices=["discovery", "extraction", "normalize"])
    args = parser.parse_args()

    plugin = load_plugin(args.brand, args.product_type)
    discovery_config = getattr(plugin, "DISCOVERY_CONFIG")

    if args.stage == "discovery":
        payload = discover(discovery_config)
        out_path = repo_root / discovery_config.output_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        logging.info("Wrote URL inventory: %s", out_path)
        logging.info("Total URLs: %s", payload.get("total_urls"))
        return 0

    # extraction stage
    url_inventory_path = repo_root / discovery_config.output_path
    if not url_inventory_path.exists():
        raise FileNotFoundError(
            f"URL inventory not found at {url_inventory_path}. Run discovery stage first."
        )

    if args.stage == "extraction":
        extract_urls = getattr(plugin, "extract_urls")
        extraction_output_path = extract_urls(str(url_inventory_path))
        logging.info("Wrote extraction JSON: %s", extraction_output_path)
        return 0

    # normalize stage
    db_url = os.environ.get("DATABASE_URL") or os.environ.get("SUPABASE_DB_URL")
    if not db_url:
        raise RuntimeError("Set DATABASE_URL (or SUPABASE_DB_URL) for normalization mapping.")

    normalize_fn = getattr(plugin, "normalize")
    normalized_output_path = normalize_fn(str(url_inventory_path), db_url=db_url)
    logging.info("Wrote normalized JSON: %s", normalized_output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

