library(ggplot2)

cairo_pdf("onion-usage.pdf", height=1.4, width=4)

df <- data.frame(
    freq = c("Additional anonymity", "Additional security",
             "Only way to access content", "Random encounters",
             "Curiosity about “Dark Web”", "Other"),
    pct = c(69.83, 61.48, 45.92, 18.60, 26.76, 11.39)
)

df$freq <- factor(df$freq, levels = df$freq[order(df$pct)])

ggplot(data = df, aes(x = freq, y = pct)) +
       geom_bar(stat = "identity", fill = "steelblue") +
       labs(x = "Why use onion\nservices?") +
       labs(y = "Percentage") +
       coord_flip() +
       theme_minimal()

dev.off()
