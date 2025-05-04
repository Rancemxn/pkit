import sys


def check_android() -> bool:
    try:
        import android  # type: ignore  # noqa: F401

        return True
    except ImportError:
        return False


os: str = ""

match sys.platform:
    case "linux":
        os = "linux" if not check_android() else "android"
    case "win32":
        os = "windows"
    case "darwin":
        os = "macos"
