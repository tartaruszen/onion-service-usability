#!/bin/bash

Rscript plot-perceived-security.R
pdfcrop perceived-security.pdf
cp perceived-security-crop.pdf ../../paper/figures/perceived-security.pdf
