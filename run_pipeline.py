"""Run the whole pipeline: load (incremental) -> transform.

Run:  python run_pipeline.py
Safe to run as many times as you like, and safe to put on a schedule.
Logs go to the console AND to pipeline.log.
"""
import logging
import sys

import load
import transform

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("pipeline.log", encoding="utf-8")],
)
log = logging.getLogger("pipeline")


def main():
    log.info("===== Pipeline run started =====")
    try:
        load.run()
        log.info("Running transformations")
        transform.main()
    except SystemExit as exc:  # transform.py exits with a message when validation fails
        log.error("Transform/validation failed: %s", exc)
        sys.exit(1)
    except Exception as exc:
        log.error("Pipeline failed: %s", exc)
        sys.exit(1)
    log.info("===== Pipeline run finished OK =====")


if __name__ == "__main__":
    main()
