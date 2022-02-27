# Termo-Solver

Helper for solving [term.ooo](https://term.ooo) with statistics.

## Install

Dependencies managed with `conda`. To install this package`s environment, just do: 

```bash
cd termo-solver
conda env create .env -f environment.yml
```

Then to use the solver script:

```bash
conda activate ./.env
termo-solver
```

## Disclaimer

**Under development!**

Currently the code in `cli.py` is very incorrect.

The more correct analysis is in `notebook/tree.ipynb` and `notebook/vetorize.ipynb`.

I went a little overboard with the vectorized operations, but it was fun!

Feel free to open issues and PRs.