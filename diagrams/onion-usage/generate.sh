#!/bin/bash

Rscript plot-usage.R
mv onion-usage.tex ../../paper/figures/

Rscript plot-discovery.R
mv onion-discovery.tex ../../paper/figures/
