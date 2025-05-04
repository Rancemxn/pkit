import sys

os: str = ""


def android() -> bool:
    try:
        import android  # type: ignore  # noqa: F401

        return True
    except ImportError:
        return False


def mobile() -> bool:
    return os == "android" or os == "ios"  # ios is on plan(?)


match sys.platform:
    case "linux":
        os = "linux" if not android() else "android"
    case "win32":
        os = "windows"
    case "darwin":
        os = "macos"
