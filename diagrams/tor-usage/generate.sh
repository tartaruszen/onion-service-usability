#!/bin/bash

Rscript plot-usage.R
pdfcrop tor-usage.pdf
cp tor-usage-crop.pdf ../../paper/figures/tor-usage.pdf

Rscript plot-threats.R
pdfcrop tor-threats.pdf
cp tor-threats-crop.pdf ../../paper/figures/tor-threats.pdf
