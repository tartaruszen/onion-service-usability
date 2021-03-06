library(tikzDevice)
library(ggplot2)
library(reshape2)

tikz(file = "perceived-security.tex", height=1.2, width=3.1)

d <- read.csv("data.csv", check.names = FALSE)

df <- melt(d)

# Order perception by significance instead of alphabetically.
df$Perception <- factor(df$Perception, levels = df$Perception[c(5, 4, 3, 2, 1)])

ggplot(data = df, aes(x = variable, y = value, fill = Perception)) +
       geom_bar(stat = "identity") +
       labs(x = "Technology") +
       labs(y = "Percentage") +
       coord_flip() +
       theme_minimal() +
       theme(axis.title = element_text(size = rel(0.9))) +
       theme(legend.key.size = unit(0.8, "line")) +
       scale_fill_brewer(palette = "Blues", direction = -1)

dev.off()
