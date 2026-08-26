#!/usr/bin/env bash
# Rebuild Chinese preprint PDF from MANUSCRIPT_zh.md
set -euo pipefail
cd "$(dirname "$0")"

pandoc MANUSCRIPT_zh.md -t typst -o preprint_zh_body.typ

cat > preprint_zh_header.typ << 'TYP'
#set page(margin: (x: 2.2cm, y: 2.4cm))
#set text(
  lang: "zh",
  font: ("Songti SC", "STSong", "Hiragino Sans GB", "Heiti SC", "Arial Unicode MS"),
  size: 10.5pt,
)
#set par(justify: true, leading: 0.75em)
#show heading: set text(font: ("Heiti SC", "Hiragino Sans GB", "Songti SC", "Arial Unicode MS"))
#show raw: set text(font: ("Menlo", "Courier New", "Arial Unicode MS"), size: 8.5pt)
TYP

cat preprint_zh_header.typ preprint_zh_body.typ > preprint_zh.typ
rm -f preprint_zh_body.typ
typst compile preprint_zh.typ preprint_zh.pdf
ls -la preprint_zh.pdf
echo "OK: paper/preprint_zh.pdf"
