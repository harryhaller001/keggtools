


### Step 1: Render dot figures

FROM ubuntu:18.04 as dot-stage

RUN apt-get update \
  && apt-get install -y --no-install-recommends graphviz \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /root

# Copy all dit files to workdir
COPY ./figures/figure1.dot /root/figure1.dot

# Render figure
RUN dot /root/figure1.dot -Tpng > /root/figure1.png



### Step 2: Execute notebooks and render figures

FROM jupyter/datascience-notebook AS notebook-stage

# Update pip
RUN pip3 install pip --upgrade

# Install python dependencies
RUN pip3 install scanpy python-igraph louvain leidenalg scikit-learn matplotlib pandas numpy umap-learn

# Copy notebook to workdir
COPY ./notebooks/*.ipynb /home/jovyan/work/notebooks/

# download rawdata
COPY ./download.sh /home/jovyan/work/download.sh
RUN bash /home/jovyan/work/download.sh

# Execute notebook and render figures (TODO: execute all notebooks script)
RUN jupyter notebook --to notebook --inplace --execute notebook.ipynb



### Step 3: Copy images from build states to last stage and build final pdf from tex

FROM ubuntu:18.04 as latex-stage

# Update ubuntu and install pdflatex and dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    graphviz \
    texlive-base \
    texlive \
    texlive-latex-extra \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /root


# Copy latex files


# Copy figures from pre build stages


# Render tex file to PDF



