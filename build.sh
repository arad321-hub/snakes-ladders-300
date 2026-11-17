#!/usr/bin/env bash
# Build the board: search a layout (optional), render SVG, export PDF + PNG preview.
# Usage:
#   ./build.sh            -> render from the existing src/layout.json
#   ./build.sh search 200 -> search 200 seeds for a new layout, then render
set -euo pipefail
cd "$(dirname "$0")/src"
if [[ "${1:-}" == "search" ]]; then
  python3 gen.py "${2:-120}"
fi
python3 render.py
mv board.svg ../output/board.svg
rsvg-convert -f pdf -o ../output/board.pdf ../output/board.svg
rsvg-convert -w 2400 -o ../output/preview.png ../output/board.svg
echo "Done: output/board.pdf, output/board.svg, output/preview.png"
