library(tikzDevice)
library(ggplot2)
library(reshape2)

tikz(file = "onion-memorize-difficulty.tex", height=1.3, width=3.2)

d <- read.csv("data.csv", check.names = FALSE)

df <- melt(d)

# Order concern by significance instead of alphabetically.
df$Concern <- factor(df$Concern, levels = df$Concern[c(5, 4, 3, 2, 1)])

ggplot(data = df, aes(x = variable, y = value, fill = Concern)) +
       geom_bar(stat = "identity") +
       labs(x = "Onion Name") +
       labs(y = "Percentage") +
       coord_flip() +
       theme_minimal() +
       theme(axis.title = element_text(size = rel(0.9))) +
       theme(legend.key.size = unit(0.8, "line")) +
       scale_fill_brewer(palette = "Blues", direction = -1)

dev.off()
