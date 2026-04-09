#!/bin/bash
# Download MHD datasets from The Well
# Usage: ./download_data.sh [base_path]
#
# Requires: pip install the_well

set -euo pipefail

BASE_PATH="${1:-./data}"

echo "=== Downloading MHD_64 ==="
the-well-download --base-path "$BASE_PATH" --dataset MHD_64 --split train
the-well-download --base-path "$BASE_PATH" --dataset MHD_64 --split valid
the-well-download --base-path "$BASE_PATH" --dataset MHD_64 --split test

echo ""
echo "=== MHD_64 download complete ==="
echo ""
echo "MHD_256 is very large (~4.58 TB). Download selectively:"
echo "  the-well-download --base-path $BASE_PATH --dataset MHD_256 --split train"
echo ""
echo "Or use HuggingFace streaming (no download needed):"
echo "  base_path='hf://datasets/polymathic-ai/'"
