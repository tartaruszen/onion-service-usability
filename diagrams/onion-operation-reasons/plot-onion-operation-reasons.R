library(tikzDevice)
library(ggplot2)

tikz(file = "onion-operation-reasons.tex", height=1.3, width=3.1)

df <- data.frame(
    freq = c("Anonymity", "End-to-end security",
             "Third-party tool", "NAT traversal",
             "Curiosity", "Other"),
    pct = c(46.34, 61.46, 27.32, 55.12, 59.51, 21.95)
)

df$freq <- factor(df$freq, levels = df$freq[order(df$pct)])

ggplot(data = df, aes(x = freq, y = pct)) +
       geom_bar(stat = "identity", fill = "steelblue") +
       labs(x = "Why run onion\nservices?") +
       labs(y = "Percentage") +
       coord_flip() +
       theme_minimal() +
       theme(axis.title = element_text(size = rel(0.9)))

dev.off()
