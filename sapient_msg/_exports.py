from __future__ import annotations

import importlib
import re
from pathlib import Path
from typing import Final

from google.protobuf.internal.enum_type_wrapper import EnumTypeWrapper
from google.protobuf.message import Message

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

_TOP_LEVEL_TYPE_PATTERN: Final[re.Pattern[str]] = re.compile(r"^class (\w+)")
_TYPE_REGISTRIES: dict[str | None, dict[str, str]] = {}


def _pb2_module_name(pb2_name: str, *, version: str | None) -> str:
    if version is None:
        return f"sapient_msg.latest.{pb2_name}"
    return f"sapient_msg.{version}.{pb2_name}"


def _type_names_from_pyi(version: str) -> tuple[str, ...]:
    names: set[str] = set()
    pkg_dir = Path(__file__).parent / version
    for pyi in sorted(pkg_dir.glob("*_pb2.pyi")):
        for line in pyi.read_text().splitlines():
            match = _TOP_LEVEL_TYPE_PATTERN.match(line)
            if match is not None:
                names.add(match.group(1))
    return tuple(sorted(names))


def _collect_public_types(module: object) -> dict[str, object]:
    types: dict[str, object] = {}
    for name, obj in vars(module).items():
        if name.startswith("_") or name == "DESCRIPTOR":
            continue
        if isinstance(obj, type) and issubclass(obj, Message):
            types[name] = obj
        elif isinstance(obj, EnumTypeWrapper):
            types[name] = obj
    return types


def _get_type_registry(*, version: str | None) -> dict[str, str]:
    if version in _TYPE_REGISTRIES:
        return _TYPE_REGISTRIES[version]

    resolved_version = "latest" if version is None else version
    registry: dict[str, str] = {}
    for pb2_name in PB2_MODULES:
        module = importlib.import_module(_pb2_module_name(pb2_name, version=version))
        for type_name in _collect_public_types(module):
            registry[type_name] = pb2_name

    _TYPE_REGISTRIES[version] = registry
    return registry


def _public_names(*, version: str | None, include_proto_options: bool) -> tuple[str, ...]:
    resolved_version = "latest" if version is None else version
    type_names = _type_names_from_pyi(resolved_version)
    if include_proto_options:
        module_names = ("proto_options_pb2", *sorted(PB2_MODULES))
    else:
        module_names = tuple(sorted(PB2_MODULES))
    return tuple(sorted(set(module_names) | set(type_names)))


_ROOT_PUBLIC_NAMES: Final[tuple[str, ...]] = _public_names(version=None, include_proto_options=True)
_VERSION_PUBLIC_NAMES: Final[tuple[str, ...]] = _public_names(
    version="latest", include_proto_options=False
)


def _resolve_module(package: str, name: str, *, version: str | None) -> object:
    if name == "proto_options_pb2":
        if version is not None:
            raise AttributeError(f"module {package!r} has no attribute {name!r}")
        return importlib.import_module("sapient_msg.proto_options_pb2")

    if name not in PB2_MODULES:
        raise AttributeError(f"module {package!r} has no attribute {name!r}")

    return importlib.import_module(_pb2_module_name(name, version=version))


def _resolve_type(package: str, name: str, *, version: str | None) -> object:
    registry = _get_type_registry(version=version)
    pb2_name = registry.get(name)
    if pb2_name is None:
        raise AttributeError(f"module {package!r} has no attribute {name!r}")

    module = importlib.import_module(_pb2_module_name(pb2_name, version=version))
    return getattr(module, name)


def make_getattr(package: str, *, version: str | None = None):
    def __getattr__(name: str) -> object:
        if name == "proto_options_pb2" or name in PB2_MODULES:
            return _resolve_module(package, name, version=version)
        return _resolve_type(package, name, version=version)

    return __getattr__


def make_root_dir() -> list[str]:
    return list(_ROOT_PUBLIC_NAMES)


def make_version_dir() -> list[str]:
    return list(_VERSION_PUBLIC_NAMES)