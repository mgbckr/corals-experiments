# syntax=docker/dockerfile:1
FROM continuumio/miniconda3:4.9.2

# Update 2022-09-17: the R part of the Docker container does not build anymore due to issues with R dependencies
#    Something must have changed in the underlying packages or R versions.
#    For now, I am providing the previously built Docker image via Dockerhub.
#    If you want to build the container, try uncommenting the R portion of this file (Line 43-44).

# install required packages 
# and set custom shell (because it really is more fun that way)
# note: the last line of packages is for fixing 'devtools' (/'pkgdown') installation 
#     which for some weird reason is suddenly missing freetype
#     source: https://github.com/r-lib/pkgdown/issues/1427#issuecomment-1224053086
RUN  apt-get -y update --allow-releaseinfo-change\
     && apt-get -y autoremove \
     && apt-get clean \
     && apt-get install -y \
     zsh \
     wget \
     vim \
     git \
     unzip \
     libzmq3-dev libharfbuzz-dev libfribidi-dev libfreetype6-dev libpng-dev libtiff5-dev libjpeg-dev build-essential libcurl4-openssl-dev libxml2-dev libssl-dev libfontconfig1-dev \
     && rm -rf /var/lib/apt/lists/*
RUN sh -c "$(wget https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)"
RUN chsh -s $(which zsh)
RUN conda init zsh

# install conda environment
WORKDIR /workspace
COPY environment.yml .
RUN conda env create -f environment.yml
RUN echo "source activate benchmark" >> ~/.bashrc
RUN echo "source activate benchmark" >> ~/.zshrc
ENV PATH /opt/conda/envs/env/bin:$PATH
# activate conda environment for RUN commands
# source: https://pythonspeed.com/articles/activate-conda-dockerfile/
SHELL ["conda", "run", "-n", "benchmark", "/bin/bash", "-c"]
RUN echo $CONDA_PREFIX

# setup R (most of it is installed in the conda environment)
# NOTE: this takes long!
COPY requirements.R .
RUN echo "This can take a LONG time and will not produce output until it is done:"; Rscript requirements.R

# setup julia
WORKDIR /opt/julia
ARG JULIA_VERSION=1.5.2
RUN wget https://julialang-s3.julialang.org/bin/linux/x64/1.5/julia-${JULIA_VERSION}-linux-x86_64.tar.gz
RUN tar zxvf julia-${JULIA_VERSION}-linux-x86_64.tar.gz
ENV PATH /opt/julia/julia-${JULIA_VERSION}/bin:$PATH
COPY requirements.jl .
RUN julia requirements.jl

# install libraries
WORKDIR /opt/libraries

# RUN ssh-keyscan -t rsa github.com > ~/.ssh/known_hosts
# RUN ssh-keyscan -t rsa bitbucket.org > ~/.ssh/known_hosts

# # * julia
# RUN git clone git@bitbucket.org:mgbckr/nalab-fastcor-lib-julia.git --config core.sshCommand="ssh -i ./lib-id_rsa" julia
COPY lib-julia julia
RUN julia -e "using Pkg; Pkg.add(path=\"./julia\"); Pkg.develop(\"Corals\")"; rm -r "/root/.julia/dev/Corals"; ln -s "/opt/libraries/julia" "/root/.julia/dev/Corals"

# # * r
# RUN git clone git@bitbucket.org:mgbckr/nalab-fastcor-lib-r.git --config core.sshCommand="ssh -i ./lib-id_rsa" r
COPY lib-r r
RUN R CMD INSTALL ./r

# # * python
# RUN git clone git@bitbucket.org:mgbckr/nalab-fastcor-lib-python.git --config core.sshCommand="ssh -i ./lib-id_rsa" python
COPY lib-python python
RUN cd ./python; python setup.py develop; cd ..

# back to workspace
WORKDIR /workspace
