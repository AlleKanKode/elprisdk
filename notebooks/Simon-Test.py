# /// script
# [tool.marimo.runtime]
# auto_instantiate = false
# on_cell_change = "lazy"
# [tool.marimo.display]
# theme = "dark"
# cell_output = "below"
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium")


@app.cell
def _():
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Demo af Dark Mode

    Følgende skal indsættes først i ens Marimo Notebook:
    """)
    return


@app.cell
def _():
    # /// script
    # [tool.marimo.runtime]
    # auto_instantiate = false
    # on_cell_change = "lazy"
    # [tool.marimo.display]
    # theme = "dark"
    # cell_output = "below"
    # ///
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## [Kilde](https://docs.marimo.io/guides/configuration/theming/#forcing-dark-mode)
    """)
    return


if __name__ == "__main__":
    app.run()
