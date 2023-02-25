using Pkg
Pkg.add.([
    Pkg.PackageSpec(;name="Revise", version="3.1.15"),
    Pkg.PackageSpec(;name="BenchmarkTools", version="0.5.0"),
    Pkg.PackageSpec(;name="HDF5", version="0.13.7"),
    Pkg.PackageSpec(;name="ArgParse", version="1.1.1"),
    Pkg.PackageSpec(;name="RData", version="0.7.3"),
    Pkg.PackageSpec(;name="MultivariateStats", version="0.8.0"),
])