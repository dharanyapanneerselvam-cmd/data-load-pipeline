"""Run the whole pipeline: load (incremental) -> transform -> build model + quality gates.

Run:  python run_pipeline.py
Safe to run as many times as you like, and safe to put on a schedule.
Logs go to the console AND to pipeline.log.
Exit code is 1 if anything fails (including a failed quality test).
"""
import logging
import sys

import build_warehouse
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
        log.info("Building dimensional model + quality gates")
        build_warehouse.main()
    except SystemExit as exc:  # transform / quality gate stop the run with a message
        log.error("Pipeline stopped: %s", exc)
        sys.exit(1)
    except Exception as exc:
        log.error("Pipeline failed: %s", exc)
        sys.exit(1)
    log.info("===== Pipeline run finished OK =====")


if __name__ == "__main__":
    main()
