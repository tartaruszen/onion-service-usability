library(tikzDevice)
library(ggplot2)
library(reshape2)

tikz(file = "onion-memorize-difficulty.tex", height=1.5, width=3.5)

d <- read.csv("data.csv", check.names = FALSE)

df <- melt(d)

# Order difficulty by significance instead of alphabetically.
df$Difficulty <- factor(df$Difficulty, levels = df$Difficulty[c(5, 4, 3, 2, 1)])

ggplot(data = df, aes(x = variable, y = value, fill = Difficulty)) +
       geom_bar(stat = "identity") +
       labs(x = "Onion domain") +
       labs(y = "Percentage") +
       coord_flip() +
       theme_minimal() +
       theme(legend.text = element_text(size = rel(0.7))) +
       theme(axis.title = element_text(size = rel(0.9))) +
       theme(axis.text.y = element_text(size = rel(0.8))) +
       theme(legend.key.size = unit(0.8, "line")) +
       theme(legend.margin = margin(l=0, unit="cm")) +
       scale_fill_brewer(palette = "Blues", direction = -1)

dev.off()
