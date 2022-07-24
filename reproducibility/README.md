
# Guide to reproduce paper

### Compile all figures

```bash
bash reproduce.sh
```


### Description of single figures

Figure 1: Object relations in the KEGG database

```bash
dot figure1.dot -Tpng > figure1.png
```


# Notebook execution
```bash
jupyter notebook --to notebook --inplace --execute notebook.ipynb
```


