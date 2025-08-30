#This code was written with the help of chatGPT
library(readxl)
library(tidyr)
library(ggplot2)
library(dplyr)

# Load data
df <- read_excel("/Users/maizellab06/Pictures/Dissertation Figures/Annex 1/tobacco.xlsx")

# Convert to long format
df_long <- df %>%
  pivot_longer(cols = everything(),
               names_to = "Condition", values_to = "Value") %>%
  drop_na()

# Keep the order from the Excel sheet
condition_order <- colnames(df)
df_long$Condition <- factor(df_long$Condition, levels = condition_order)

# Add group index for spacing
group_size <- 3
df_long <- df_long %>%
  mutate(group = (as.numeric(Condition) - 1) %/% group_size,
         x_pos = as.numeric(Condition) + group * 0.5)

# Define colors
color_map <- c(
  "c. B" = "lightblue", "B" = "lightblue", "B - R" = "lightblue",
  "c. D" = "gray40", "D" = "gray40", "D - R" = "gray40",
  "c. WL+B+FR" = "white", "WL+B+FR" = "white", "WL+B+FR - R" = "white"
)

# Plot
ggplot(df_long, aes(x = x_pos, y = Value, fill = Condition)) +
  geom_boxplot(outlier.shape = NA, width = 0.4, color = "black") +  # black outlines
  geom_jitter(width = 0.1, size = 2, shape = 21, stroke = 0.8, color = "black") + # points with outline
  scale_fill_manual(values = color_map) +
  scale_x_continuous(breaks = df_long$x_pos, labels = df_long$Condition,
                     expand = expansion(add = 0.3)) +  # cleaner spacing
  theme_classic() +  # remove gridlines
  labs(title = "Values by Condition", x = "Condition", y = "Value") +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        axis.line.x = element_line(color = "black"),
        axis.line.y = element_line(color = "black"),
        legend.position = "none")