from loguru import logger
from pysmartdl2 import SmartDL

from . import taptap


def fetch(platform: str = "taptap", name: str = ".", threads: int = 32) -> None | str:
    url = ""
    match platform:
        case "taptap":
            data = taptap.get_download_info()["data"]["apk"]
            version_name = data["version_name"]
            url = data["download"]
            logger.info("taptap url Detected.")
            if name == ".":  # fix filename instead of hashname like
                name = f"./Phigros.{version_name}.apk"
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
