# install_r_packages.R

# --- Configuration ---
# Set a default CRAN mirror so the script can run non-interactively.
options(repos = c(CRAN = "https://cloud.r-project.org"))

# --- Function to ensure a package is installed ---
# This function checks if a package exists. If not, it installs it.
ensure_package <- function(pkg_name) {
  if (!require(pkg_name, character.only = TRUE)) {
    print(paste("Installing package:", pkg_name))
    install.packages(pkg_name)
  }
}

# --- CRAN Packages ---
# Use our new function to install packages only if they are missing.
ensure_package("devtools")
ensure_package("dplyr")
ensure_package("ggplot2")
# Add any other CRAN packages you need here...


# --- GitHub Packages ---
# We can use a similar check for the GitHub package.
if (!require("ConnectednessApproach")) {
  print("Installing ConnectednessApproach from GitHub...")
  remotes::install_github("GabauerDavid/ConnectednessApproach")
}


print("All required R packages are installed and ready.")