#!/bin/bash

Rscript plot-os-growth.R os-growth.csv
pdfcrop os-growth.pdf
cp os-growth-crop.pdf ../../paper/figures/os-growth.pdf
