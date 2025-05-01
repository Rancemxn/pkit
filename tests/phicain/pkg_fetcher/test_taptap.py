import src.phicain.utils.official.pkg_fetcher.taptap as taptap


def test_fetch_official_pkg_taptap():
    result = taptap.get_download_info()
    assert isinstance(result, dict)
    assert "data" in result
    assert "apk" in result["data"]
    assert "version_name" in result["data"]["apk"]
    assert "download" in result["data"]["apk"]
