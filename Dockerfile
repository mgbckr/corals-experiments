# syntax=docker/dockerfile:1

ARG BASE_IMAGE=mgbckr/corals-experiments-base:latest
FROM ${BASE_IMAGE}

# install libraries
WORKDIR /opt/libraries

# prepare cloning repositories
RUN mkdir -p ~/.ssh; ssh-keyscan -t rsa github.com > ~/.ssh/known_hosts
COPY lib-id_rsa .

# start conda environment
SHELL ["conda", "run", "-n", "benchmark", "/bin/bash", "-c"]
RUN echo $CONDA_PREFIX

# # * julia
# COPY lib-julia julia
ARG CORALS_JULIA_VERSION=0.1.0
RUN git clone --depth 1 --branch ${CORALS_JULIA_VERSION} git@github.com:mgbckr/corals-lib-julia.git --config core.sshCommand="ssh -i ./lib-id_rsa" julia
RUN julia -e "using Pkg; Pkg.add(path=\"./julia\"); Pkg.develop(\"Corals\")"; rm -r "/root/.julia/dev/Corals"; ln -s "/opt/libraries/julia" "/root/.julia/dev/Corals"

# # * r
# COPY lib-r r
ARG CORALS_R_VERSION=0.1.0
RUN git clone --depth 1 --branch ${CORALS_R_VERSION} git@github.com:mgbckr/corals-lib-r.git --config core.sshCommand="ssh -i ./lib-id_rsa" r
RUN R CMD INSTALL ./r

# # * python
ARG CORALS_PYTHON_VERSION=0.1.4
# COPY lib-python python
RUN git clone --depth 1 --branch ${CORALS_PYTHON_VERSION} git@github.com:mgbckr/corals-lib-python.git --config core.sshCommand="ssh -i ./lib-id_rsa" python
RUN cd ./python; python setup.py develop; cd ..

RUN rm lib-id_rsa

# back to workspace
WORKDIR /workspace

# make sure coralsarticle module is installed
ENTRYPOINT ["/bin/zsh"]
