#!/bin/bash

Rscript plot-usage.R
pdfcrop onion-usage.pdf
cp onion-usage-crop.pdf ../../paper/figures/onion-usage.pdf

Rscript plot-discovery.R
pdfcrop onion-discovery.pdf
cp onion-discovery-crop.pdf ../../paper/figures/onion-discovery.pdf
