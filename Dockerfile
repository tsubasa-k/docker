FROM continuumio/anaconda3:2021.05

RUN conda config --append channels conda-forge && \
    conda install -c conda-forge tensorflow-gpu keras

#COPY model_test /app


CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
