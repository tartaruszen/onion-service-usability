library(ggplot2)

cairo_pdf("tor-usage.pdf", height=1.4, width=4)

df <- data.frame(
    freq = c("Less than monthly", "Monthly", "Weekly", "Daily", "Main browser"),
    pct = c(9, 12.64, 28.54, 30.08, 19.54)
)

df$freq <- factor(df$freq, levels = df$freq[c(1, 2, 3, 4, 5)])

ggplot(data = df, aes(x = freq, y = pct)) +
       geom_bar(stat = "identity", fill = "steelblue") +
       labs(x = "Usage\nfrequency") +
       labs(y = "Percentage") +
       coord_flip() +
       theme_minimal()

dev.off()
