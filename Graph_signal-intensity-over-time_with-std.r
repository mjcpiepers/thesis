#This script was made with the help of ChatGPT
#Install and load the required package for reading Excel files
library(readxl)
library(dplyr)
library(ggplot2)
library(tidyr)

# Read the Excel file
df <- read_excel("/Users/maizellab06/Pictures/Dissertation Figures/3. SOSEKI function/SOK5_priorDiv/LR/data/dataR_priorDiv_LR_allValues.xlsx")

# Convert to long format
df_long <- df %>%
  tidyr::pivot_longer(
    cols = -time,
    names_to = "cell",
    values_to = "signal"
  ) %>%
  filter(!is.na(signal))  # remove missing values

# Calculate mean and standard deviation for each timepoint
summary_df <- df_long %>%
  group_by(time) %>%
  summarise(
    mean_signal = mean(signal, na.rm = TRUE),
    sd_signal = sd(signal, na.rm = TRUE),
    .groups = "drop"
  )

# Remove rows with NA before plotting
summary_df_clean <- summary_df %>%
  filter(!is.na(mean_signal) & !is.na(sd_signal))
print(summary_df_clean)

# Plot: mean ± SD
ggplot(summary_df_clean, aes(x = time, y = mean_signal)) +
  geom_line(aes(group = 1), color = "black", size = 0.8) +
  geom_point(color = "black", size = 2) +
  geom_vline(xintercept = 0, color = "black", linewidth = 0.8) +
  scale_x_continuous(breaks = seq(-120, 60, by = 30), limits = c(-120, 60)) +
  scale_y_continuous(breaks = seq(0, 1, by = 0.2), limits = c(-0.1, 1.1)) +
  geom_ribbon(aes(
    ymin = mean_signal - sd_signal,
    ymax = mean_signal + sd_signal,
    group = 1  # ✅ force continuous ribbon
  ), fill = "#158CCE", alpha = 0.35) +
  labs(
    x = "Time (min)",
    y = "Normalised mean signal intensity"
  ) +
  theme_minimal(base_size = 24) +
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major = element_line(color = "grey90")
  )