"""SAPIENT protobuf bindings."""

from sapient_msg._exports import _ROOT_PUBLIC_NAMES, make_getattr, make_root_dir

__all__ = list(_ROOT_PUBLIC_NAMES)
__getattr__ = make_getattr(__name__)
__dir__ = make_root_dir