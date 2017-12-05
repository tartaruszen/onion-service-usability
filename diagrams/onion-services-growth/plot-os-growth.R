library(ggplot2)
library(scales)
library(grid)

args <- commandArgs(trailingOnly = TRUE)
input_file <- args[1]

cairo_pdf("os-growth.pdf", height=2, width=4)
data <- read.csv(input_file, header=TRUE)
data$date <- as.POSIXct(paste(data$date), format="%Y-%m-%d")
data$date <- as.Date(data$date)

df <- data.frame(x = data$date,
                 y = data$wmedian)

ggplot(df, aes(x, y)) +
       geom_line(fill = "steelblue") +
       labs(x = "Date") +
       labs(y = "Amount") +
       scale_y_continuous(labels=function(x) format(x, big.mark = ",", scientific = FALSE)) +
       scale_x_date(labels = date_format("%b %Y")) +
       theme(legend.key.width = unit(2, "line"),
             legend.key = element_blank()) +
       theme_minimal()

dev.off()
