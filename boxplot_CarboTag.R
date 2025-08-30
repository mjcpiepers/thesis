# Packages
if (!require("readxl")) install.packages("readxl")
if (!require("dplyr"))  install.packages("dplyr")
if (!require("ggplot2")) install.packages("ggplot2")
if (!require("ggpubr"))  install.packages("ggpubr")

library(readxl)
library(dplyr)
library(ggplot2)
library(ggpubr)

# Read the data
data <- read_excel("/Users/maizellab06/Pictures/Dissertation Figures/2. what is the cue/Carbotag/DataR_CarboTag_RAM.xlsx")
data$Region <- as.factor(data$Region)

# Define your palette (same as bar plot)
bar_colors <- c("#1f77b4", "#2ca02c", "#ff7f0e", "#d62728")

# y-axis limits
y_lower <- 3.0
y_upper <- 4.0

# n per Region for axis labels
region_counts <- data %>%
  count(Region)

axis_lab_with_n <- function(x) {
  paste0(x, "\n(n=", region_counts$n[match(x, region_counts$Region)], ")")
}

# All pairwise comparisons for Wilcoxon tests
comparisons <- combn(levels(data$Region), 2, simplify = FALSE)

# Plot
p <- ggplot(data, aes(x = Region, y = Mean, fill = Region)) +
  geom_boxplot(width = 0.6, outlier.shape = NA, alpha = 0.6) +
  geom_jitter(width = 0.15, size = 2, alpha = 0.8) +
  stat_summary(fun = mean, geom = "point", shape = 23, size = 3, fill = "white") +
  scale_fill_manual(values = bar_colors) +          # << your colors
  scale_y_continuous(limits = c(y_lower, y_upper),
                     breaks = seq(y_lower, y_upper, by = 0.1)) +
  scale_x_discrete(labels = axis_lab_with_n) +
  labs(x = "Region", y = "Intensity weighted lifetime") +
  theme_classic(base_size = 12) +
  theme(legend.position = "none")

# Add Wilcoxon stars with Bonferroni correction
p + stat_compare_means(method = "wilcox.test",
                       comparisons = comparisons,
                       label = "p.signif",
                       p.adjust.method = "bonferroni",
                       hide.ns = TRUE)
