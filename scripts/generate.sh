#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python -m grpc_tools.protoc \
  --proto_path="sapient_msg=." \
  --python_out=. \
  --pyi_out=. \
  sapient_msg/proto_options.proto \
  sapient_msg/bsi_flex_335_v2_0/*.proto