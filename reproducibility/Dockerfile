
# Step 1: Render dot figures

FROM ubuntu:18.04 as figures-dot

RUN apt-get update \
  && apt-get install -y --no-install-recommends graphviz \
  && rm -rf /var/lib/apt/lists/*


WORKDIR /root

# Copy all dit files to workdir
COPY ./figures/figure1.dot /root/figure1.dot

# Convert dot files to png


# Step 2: Execute notebooks and render figures




# Step 3: Copy images from build states to last stage and build final pdf from tex





