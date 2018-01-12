#!/bin/bash

Rscript plot-usage.R
mv tor-usage.tex ../../paper/figures/

Rscript plot-threats.R
mv tor-threats.tex ../../paper/figures/
