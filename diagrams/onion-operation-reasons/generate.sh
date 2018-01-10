#!/bin/bash

Rscript plot-onion-operation-reasons.R
pdfcrop onion-operation-reasons.pdf
cp onion-operation-reasons-crop.pdf ../../paper/figures/onion-operation-reasons.pdf
