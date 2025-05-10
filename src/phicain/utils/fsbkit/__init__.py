from ..audios.vgmstream_fixer import run
import tempfile
from pathlib import Path


def decode(data: bytes, outputPath: Path | str):
    with tempfile.TemporaryDirectory(
        prefix="FSB5DECODE", suffix="TEMP"
    ) as tmpdir:
        tmpdir = Path(tmpdir)
        tf = tmpdir / "tmp.fsb"
        with tf.open(mode="wb") as f:
            f.write(data)
        run(
            [
                str(tf.absolute()),
                "-o",
                str((Path(str(outputPath))).absolute()),
            ]
        )
