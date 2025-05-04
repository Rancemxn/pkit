import os

import src.phicain.utils.official.pkg_fetcher as fetcher


def test_download_pkg_from_taptap():
    path = fetcher.fetch(platform="taptap", name="./[Test]Phigros.apk")
    assert path
    assert os.path.exists(path)
    os.remove(path)
