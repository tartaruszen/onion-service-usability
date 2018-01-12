library(tikzDevice)
library(ggplot2)

tikz(file = "onion-domain-mgmt.tex", height=1.7, width=3.2)

df <- data.frame(
    freq = c("Save in local text file", "Save with pen and paper",
             "Bookmark in Tor Browser", "Web-based bookmarking",
             "Use search engines", "Refer to trusted websites", "Memorization",
             "No good solution", "Other"),
    pct = c(36.24, 7.78, 51.23, 2.66, 17.84, 34.16, 16.32, 25.24, 9.11)
)

df$freq <- factor(df$freq, levels = df$freq[order(df$pct)])

ggplot(data = df, aes(x = freq, y = pct)) +
       geom_bar(stat = "identity", fill = "steelblue") +
       labs(x = "How do you handle\nonion domains?") +
       labs(y = "Percentage") +
       coord_flip() +
       theme_minimal() +
       theme(axis.title = element_text(size = rel(0.9)))

dev.off()
