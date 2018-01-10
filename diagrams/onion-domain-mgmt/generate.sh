#!/bin/bash

Rscript plot-onion-domain-mgmt.R
pdfcrop onion-domain-mgmt.pdf
cp onion-domain-mgmt-crop.pdf ../../paper/figures/onion-domain-mgmt.pdf
