from loguru import logger
from pysmartdl2 import SmartDL

from phicain.utils.official.pkg_fetcher import taptap


def fetch(platform: str = "taptap", name: str = ".", threads: int = 32) -> None | str:
    url = ""
    match platform:
        case "taptap":
            url = taptap.get_download_info()["data"]["apk"]["download"]
            logger.info("taptap url Detected.")
        case _:
            logger.warning("Unknown Platform Detected. Ignored")
            return

    task = SmartDL(urls=url, dest=name, logger=logger, threads=threads, verify=False)

    logger.info("Download Start.")

    task.start()

    if task.isSuccessful():
        logger.info("Done.")
        logger.info(f"Saved to {task.get_dest()}")
        return task.get_dest()
    else:
        logger.error("Error occurred while downloading")
        logger.error(f"{task.get_errors()}")
        return


if __name__ == "__main__":
    fetch()
