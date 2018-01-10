#!/bin/bash

Rscript plot-onion-operation-concerns.R
pdfcrop onion-operation-concerns.pdf
cp onion-operation-concerns-crop.pdf ../../paper/figures/onion-operation-concerns.pdf
