"""
Entry point for running the end-to-end X automation workflow.
"""

from x_auto.workflow.pipeline import run_pipeline


def main() -> None:
    """
    Initialize configuration and execute the primary workflow.

    This function is intended to:
    - load environment variables and credentials
    - orchestrate the fetch → match → decide → reply → log pipeline
    - handle top-level exceptions and exit codes
    """
    run_pipeline()


if __name__ == "__main__":
    main()
