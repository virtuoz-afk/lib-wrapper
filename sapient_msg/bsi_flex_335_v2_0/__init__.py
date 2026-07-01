from sapient_msg._exports import _VERSION_PUBLIC_NAMES, make_getattr, make_version_dir

__all__ = list(_VERSION_PUBLIC_NAMES)
__getattr__ = make_getattr(__name__, version="bsi_flex_335_v2_0")
__dir__ = make_version_dir