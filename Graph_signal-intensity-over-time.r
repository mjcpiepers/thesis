#This script was made with the help of ChatGPT
# Install and load the required package for reading Excel files
if (!require("readxl")) {
  install.packages("readxl")
  library(readxl)
}

# Read the Excel file "dataR_wt.xlsx" into a data frame
df <- read_excel("Pictures/Dissertation Figures/2. what is the cue/4. mechanical alterations/Data/dataR_control_normMax.xlsx")

# Check the structure of the data to confirm column names
str(df)

# Determine y-axis limits that cover both lengthNorm and ratioNormalised
y_limits <- range(c(0, 1), na.rm = TRUE)

colorOne <- "#cccccc"
colorTwo <- "#08dcef"

# Fit smooth spline curves to both variables.
# Adjust the 'spar' parameter (between 0 and 1) to control the smoothing (0 less smooth, 1 more smooth)
spline_length <- smooth.spline(df$time, df$lengthNorm, spar = 0.5)
spline_ratio  <- smooth.spline(df$time, df$ratioNormalised, spar = 0.5)

# Create an empty plot with the right axis limits and labels.
plot(
  df$time,
  df$lengthNorm,
  type = "n",  # Set up the plot without drawing the original jagged line
  xlab = "",
  ylab = "",
  ylim = y_limits,
  yaxt = "n"  # suppress default y-axis drawing
)

# Draw the smooth spline lines on the plot.
lines(spline_length, col = colorOne, lwd = 2)
lines(spline_ratio, col = colorTwo, lwd = 2)

# Manually specify more y-axis ticks.
y_ticks <- seq(from = 0, to = 1, by = 1)

# Draw the custom y-axis with new tick positions and labels.
axis(2, at = y_ticks, las = 1)