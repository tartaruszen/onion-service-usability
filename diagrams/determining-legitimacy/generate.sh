#!/bin/bash

Rscript plot-determining-legitimacy.R
pdfcrop determining-legitimacy.pdf
cp determining-legitimacy-crop.pdf ../../paper/figures/determining-legitimacy.pdf
