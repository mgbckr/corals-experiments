install.packages("devtools", version = "2.4.2", repos="http://cran.us.r-project.org")

library(devtools)
install_version("RhpcBLASctl", version = "0.21-247", repos = "http://cran.us.r-project.org")
install_version("bench", version = "1.1.1", repos = "http://cran.us.r-project.org")
install_version("optparse", version = "1.6.6", repos = "http://cran.us.r-project.org")

if (!requireNamespace("BiocManager", quietly = TRUE))
    install.packages("BiocManager", repos = "http://cran.us.r-project.org")
BiocManager::install(version = "3.12")
BiocManager::install("rhdf5")#, version = "2.34.0")

# baselines
BiocManager::install("WGCNA")#, version = "1.70-3")
BiocManager::install("coop")#, version = "0.6-3")
BiocManager::install("HiClimR")#, version = "2.2.0")
BiocManager::install("Rfast")#, version = "2.0.3")
