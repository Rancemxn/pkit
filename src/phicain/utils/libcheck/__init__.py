import subprocess

from loguru import logger


def cmd(cmd: list) -> int:
    logger.info(f"Check Command: {cmd}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        logger.error(
            f"Command '{' '.join(result.args)}' returned non-zero exit status {result.returncode}."
        )
        logger.error("--- stdout ---")
        logger.error(result.stdout)
        logger.error("--- stderr ---")
        logger.error(result.stderr)
        logger.error("---------------------")
    else:
        logger.info(f"Command '{' '.join(result.args)}' executed successfully.")
        logger.info("--- stdout ---")
        logger.info(result.stdout)
        logger.info("---------------------")

    return result.returncode
