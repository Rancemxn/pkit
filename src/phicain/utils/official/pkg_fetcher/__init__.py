from pathlib import Path

from loguru import logger
from pysmartdl2 import SmartDL

from . import taptap


def fetch(
    platform: str = "taptap", name: str | Path = ".", threads: int = 32
) -> None | str:
    url = ""
    match platform:
        case "taptap":
            data = taptap.get_download_info()["data"]["apk"]
            version_name = data["version_name"]
            url = data["download"]
            logger.info("taptap url Detected.")
            if str(name) == ".":  # fix filename instead of hashname like
                name = f"./Phigros.{version_name}.apk"
        case _:
            logger.warning("Unknown Platform Detected. Ignored")
            return

    task = SmartDL(
        urls=url, dest=str(name), logger=logger, threads=threads, verify=False
    )

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
    import typer

    app = typer.Typer()

    from typing_extensions import Annotated

    @app.command()
    def fetchPackage(
        platform: Annotated[
            str,
            typer.Option(help="Choose what platform to fetch Official Package."),
        ] = "taptap",
        path: Annotated[
            Path,
            typer.Option(writable=True, help="Choose where to save Package."),
        ] = Path("."),
        threads: Annotated[
            int,
            typer.Option(
                min=1, max=64, help="Choose how many threads to fetch Package."
            ),
        ] = 16,
    ):
        fetch(platform, path, threads)

    app(prog_name="OfficialPackageFetcher")
