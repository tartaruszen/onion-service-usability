library(ggplot2)

cairo_pdf("tor-threats.pdf", height=2, width=4)

df <- data.frame(
    threats = c("My government", "Other governments", "My ISP", "My school",
                "My employer", "Friends and family", "Advertising companies",
                "Hackers in open WiFis", "Other"),
    count = c(84.25, 71.35, 86.34, 16.89, 23.53, 23.72, 69.26, 47.63, 13.09)
)

df$threats <- factor(df$threats, levels = df$threats[order(df$count)])

ggplot(data = df, aes(x = threats, y = count)) +
       geom_bar(stat = "identity", fill = "steelblue") +
       labs(x = "Actors in threat model") +
       labs(y = "Percentage") +
       coord_flip() +
       theme_minimal()

dev.off()
