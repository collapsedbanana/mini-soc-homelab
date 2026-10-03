#!/bin/sh
# Génère rapport-mini-soc-eisvogel.pdf depuis rapport-mini-soc.md (format Eisvogel).
# Prérequis : pandoc, xelatex (texlive-xetex, texlive-latex-extra, texlive-fonts-extra),
# le modèle eisvogel dans ~/.local/share/pandoc/templates/eisvogel.latex,
# et les polices Source Sans Pro / Source Code Pro installées.
cd "$(dirname "$0")"
pandoc rapport-mini-soc.md -o rapport-mini-soc-eisvogel.pdf \
  --template eisvogel --pdf-engine=xelatex \
  --lua-filter eisvogel-filtre.lua --listings --columns=60
