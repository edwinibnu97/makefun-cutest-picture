# make.fun — Make the cutest picture

Entry for the "Make the cutest picture" bounty (make.fun).

`main.py` is a pure Python 3.13 standard-library program (no third-party
modules, no network). It draws a chubby kitten face — big round eyes,
pink nose, blush cheeks, whiskers and a little bow — with simple
geometry, encodes it as a PNG from scratch (zlib + struct only), and
writes it to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output/entry.png`).

Fully deterministic: two runs produce byte-identical output.
Output: 512x512 PNG, ~5 KB.
