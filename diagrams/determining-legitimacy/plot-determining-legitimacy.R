library(tikzDevice)
library(ggplot2)

tikz(file = "determining-legitimacy.tex", height=1.6, width=3.1)

df <- data.frame(
    freq = c("Verify address bar", "Use bookmarks",
             "Check clearnet ref.", "Often cannot tell",
             "Use trusted source", "Check HTTPS cert.",
             "Don't check", "Other"),
    pct = c(45.54, 52.91, 40.50, 29.07, 64.92, 36.43, 10.47, 13.18)
)

df$freq <- factor(df$freq, levels = df$freq[order(df$pct)])

ggplot(data = df, aes(x = freq, y = pct)) +
       geom_bar(stat = "identity", fill = "steelblue") +
       labs(x = "How to determine a\nservice's legitimacy?") +
       labs(y = "Percentage") +
       coord_flip() +
       theme_minimal() +
       theme(axis.title = element_text(size = rel(0.9)))

dev.off()
