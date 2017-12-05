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
       #guides(shape = guide_legend(override.aes = list(size = 2))) +
       theme(legend.key.size = unit(0.8, "line")) +
       scale_fill_manual(values=c("#043061", "#1f66ab", "#4293c3", "#92c4de", "#d1e5f0"))

dev.off()
