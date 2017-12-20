library(ggplot2)
library(reshape2)

cairo_pdf("onion-operation-concerns.pdf", height=1.5, width=4)

d <- read.csv("data.csv", check.names = FALSE)

df <- melt(d)

# Order concern by significance instead of alphabetically.
df$Concern <- factor(df$Concern, levels = df$Concern[c(5, 4, 3, 2, 1)])

ggplot(data = df, aes(x = variable, y = value, fill = Concern)) +
       geom_bar(stat = "identity") +
       labs(x = "Attack") +
       labs(y = "Percentage") +
       coord_flip() +
       theme_minimal() +
       theme(legend.key.size = unit(0.8, "line")) +
       scale_fill_brewer(palette = "Blues", direction = -1)

dev.off()
