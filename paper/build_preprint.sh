#!/usr/bin/env bash
# Rebuild preprint PDF from section markdown files.
set -euo pipefail
cd "$(dirname "$0")"

ROOT="$(cd .. && pwd)"
PYTHON="${ROOT}/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON=python3
fi

"$PYTHON" << 'PY'
from pathlib import Path

paper = Path('.')
abstract = Path('OUTLINE.md').read_text(encoding='utf-8')
# Prefer stable abstract block from OUTLINE between "## Abstract" and "**Keywords:**"
import re
m = re.search(r'## Abstract \(draft\)\n\n(.+?)\n\n\*\*Keywords:\*\*(.+?)\n', abstract, re.S)
if not m:
    raise SystemExit('Could not parse abstract from OUTLINE.md')
abs_body = m.group(1).strip()
keywords = m.group(2).strip()

header = f'''# Quantifying the evidence for Austro-Tai with permutation tests

Jeremy Collins

Companion code and data: [github.com/jeremycollinsmpi/austro-tai-llm-test](https://github.com/jeremycollinsmpi/austro-tai-llm-test).

## Abstract

{abs_body}

**Keywords:** {keywords}
'''

fig_block = '''
## Figure: Null distribution

![Null histogram of hit counts with observed count marked](figures/null_histogram.png)

**Figure 1.** Distribution of hit counts (generosity score of 4 or higher) under 100 random reassignments of Tier A PAN forms to Tier A PKD slots. Red line: observed hits (27).
'''

order = [
    'INTRODUCTION.md',
    'LITERATURE.md',
    'DATA.md',
    'METHODS.md',
    'RESULTS.md',
    'DISCUSSION.md',
    'APPENDIX.md',
    'REFERENCES.md',
]

chunks = [header.strip(), '']
for name in order:
    chunks.append(Path(name).read_text(encoding='utf-8').strip())
    chunks.append('')
    if name == 'RESULTS.md':
        chunks.append(fig_block.strip())
        chunks.append('')

Path('MANUSCRIPT.md').write_text('\n\n'.join(chunks) + '\n', encoding='utf-8')
print('Wrote MANUSCRIPT.md')
PY

pandoc MANUSCRIPT.md -t typst -o preprint.typ
typst compile preprint.typ preprint.pdf
ls -la preprint.pdf
echo "OK: paper/preprint.pdf"
