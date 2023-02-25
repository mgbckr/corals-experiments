using HDF5
using DataFrames


function load_data(;
        type="synthetic_mn", 
        m=nothing, 
        n=nothing, 
        data_dir="data/processed",
        do_prepare_data=true,
        do_prepare_data_negative=false,
        do_prepare_data_drop_duplicates=false,
        sample_size=nothing, 
        return_name=true)

    if type == "synthetic_mn"
        X = rand(m, n)
        name = "synthetic_mn_m-$(m)_n-$(n)"
    else
        h5open(data_dir * "/data_$(type).h5", "r") do f
            X = read(f["data"])'
        end
        name = type
    end

    if do_prepare_data
        X = prepare_data(X; negative=do_prepare_data_negative, drop_duplicates=do_prepare_data_drop_duplicates)
        if do_prepare_data_negative
            name *= "_negative"
        end
        if do_prepare_data_drop_duplicates
            name *= "_dropduplicates"
        end
    end
    
    if sample_size !== nothing
        X = X[:,1:trunc(Int, size(X, 2) * sample_size)]
        name *= "_sample-$(@sprintf("%.02f", sample_size))"
    end

    if return_name
        return name, X
    else
        return X
    end
end


function load_data_pregnancy(; data_dir="./data/processed")
    h5open(data_dir * "/data_pregnancy.h5", "r") do f
        return read(f["data"])'
    end
end

function prepare_data(X; negative=false, drop_duplicates=false, min_nunique=2)

    X = copy(X)

    if negative
        X[findall(X.<=0)] .= 0
    end

    if drop_duplicates
        sunique = findall(nonunique(DataFrame(copy(X'))).==0)
        X = X[:, sunique]
    end

    if min_nunique !== nothing
        ss = findall(map(i->length(unique(X[:,i])),1:size(X,2)) .>= min_nunique)
        X = X[:, ss]
    end

    return X
end