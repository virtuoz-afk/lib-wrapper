from __future__ import annotations

import importlib
from typing import Final

PB2_MODULES: Final[frozenset[str]] = frozenset(
    {
        "alert_ack_pb2",
        "alert_pb2",
        "associated_detection_pb2",
        "associated_file_pb2",
        "detection_report_pb2",
        "error_pb2",
        "follow_pb2",
        "location_pb2",
        "range_bearing_pb2",
        "registration_ack_pb2",
        "registration_pb2",
        "sapient_message_pb2",
        "status_report_pb2",
        "task_ack_pb2",
        "task_pb2",
        "velocity_pb2",
    }
)

_ROOT_PUBLIC_NAMES: Final[tuple[str, ...]] = ("proto_options_pb2", *sorted(PB2_MODULES))
_VERSION_PUBLIC_NAMES: Final[tuple[str, ...]] = tuple(sorted(PB2_MODULES))


def _resolve_module(package: str, name: str, *, version: str | None) -> object:
    if name == "proto_options_pb2":
        if version is not None:
            raise AttributeError(f"module {package!r} has no attribute {name!r}")
        return importlib.import_module("sapient_msg.proto_options_pb2")

    if name not in PB2_MODULES:
        raise AttributeError(f"module {package!r} has no attribute {name!r}")

    if version is None:
        module_name = f"sapient_msg.latest.{name}"
    else:
        module_name = f"sapient_msg.{version}.{name}"

    return importlib.import_module(module_name)


def make_getattr(package: str, *, version: str | None = None):
    def __getattr__(name: str) -> object:
        return _resolve_module(package, name, version=version)

    return __getattr__


def make_root_dir() -> list[str]:
    return list(_ROOT_PUBLIC_NAMES)


def make_version_dir() -> list[str]:
    return list(_VERSION_PUBLIC_NAMES)