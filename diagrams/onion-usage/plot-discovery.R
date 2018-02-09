library(tikzDevice)
library(ggplot2)

tikz(file = "onion-discovery.tex", height=1.3, width=3.1)

df <- data.frame(
    freq = c("Social networking sites", "Search engine lists",
             "Random encounters", "Friends and family",
             "Other", "Not interested"),
    pct = c(47.06, 45.92, 45.35, 18.22, 15.94, 4.17)
)

df$freq <- factor(df$freq, levels = df$freq[order(df$pct)])

ggplot(data = df, aes(x = freq, y = pct)) +
       geom_bar(stat = "identity", fill = "steelblue") +
       labs(x = "Way of\ndiscovery") +
       labs(y = "Percentage") +
       coord_flip() +
       theme_minimal() +
       theme(axis.title = element_text(size = rel(0.9)))

dev.off()
