import coralsarticle.data.utils


def prepare_synthetic_data():

    # prepare synthetic data

    data_m_base = 50
    data_n_base = 20000
    data_m_range = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500]
    data_n_range = [1000, 2500, 5000, 10000, 20000, 40000, 60000]

    synthetic_data_grid = \
        [(data_m_base, p_n) for p_n in data_n_range] +\
        [(p_m, data_n_base) for p_m in data_m_range]

    synthetic_data = []
    for m, n in synthetic_data_grid:
        name, X = coralsarticle.data.utils.load_data(dataset="synthetic_mn", m=m, n=n)
        synthetic_data.append(name)

    return synthetic_data


def prepare_real_data():

    # prepare real world data
    real_data = []
    real_data_params = dict(
        postprocess_data_negative=True,
        postprocess_data_drop_duplicates=True)

    name, _ = coralsarticle.data.utils.load_data(dataset="preeclampsia", **real_data_params)
    real_data.append(name)

    name, _ = coralsarticle.data.utils.load_data(dataset="pregnancy", **real_data_params)
    real_data.append(name)

    name, _ = coralsarticle.data.utils.load_data(dataset="cancer", sample_size=0.25, **real_data_params)
    real_data.append(name)

    name, _ = coralsarticle.data.utils.load_data(dataset="cancer", sample_size=0.50, **real_data_params)
    real_data.append(name)

    name, _ = coralsarticle.data.utils.load_data(dataset="cancer", sample_size=1.00, **real_data_params)
    real_data.append(name)

    name, _ = coralsarticle.data.utils.load_data(dataset="singlecell")
    real_data.append(name)
    
    name, _ = coralsarticle.data.utils.load_data(dataset="singlecell_large")
    real_data.append(name)
    
    name, X = coralsarticle.data.utils.load_data(dataset_name_prefix="large_", dataset="synthetic_mn", m=500, n=200000)
    real_data.append(name)

    return real_data


def prepare_all():
    prepare_synthetic_data()
    prepare_real_data()


if __name__ == "__main__":
    prepare_all()