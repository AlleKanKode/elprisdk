import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return


@app.cell
def _():
    from models.energinet import Energinet 
    return


if __name__ == "__main__":
    app.run()
