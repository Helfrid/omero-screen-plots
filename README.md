# omero-screen-plots

Plotting Functions for Omero-Screen Immuno-fluorescence Data.
## Status


Version: ![version](https://img.shields.io/badge/version-0.1.1-blue)

[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features
Examples for each plot can be found in jupyter notebooks in tests/examples.
### combplot
Cell Cycle analysis with one selected feature column
platted as a scatterplot along the DAPI axis. (Requires EdU labelling data and cell cycle analysis in the csv file)

```python
from omero_screen_plots.combplot import comb_plot

comb_plot(
    df=df,
    conditions=conditions,
    feature_col="intensity_mean_yH2AX_nucleus",
    feature_y_lim=6000,
    condition_col="condition",  # default
    selector_col="cell_line",  # default
    selector_val="RPE1wt",
    title="combplot test",
    cell_number=1000,
    save=False,
    path=None,
)
```
<img src="./images/combplot.png" alt="combplot" width="300">

### cellcycle plot
Quantitative analysis of cell cycle phases for IF data with EdU labeling.
If data from three imaging plates are present statistical analysis is performed
using the scipy stats.ttest_indep function and pvalues are indicated with *, ** and ***
indicating < 0.05, < 0.01, < 0.001

```python
from omero_screen_plots.combplot import cellcycle_plot

for cell_line in df.cell_line.unique():
    cellcycle_plot(
        df=df,
        conditions=conditions,
        condition_col="condition",  # default
        selector_col="cell_line",  # default
        selector_val=cell_line,
        title=f"{cell_line} cell cycle plots",
        save=False,
        path=None,
)
```
<img src="./images/cellcycle.png" alt="cellcycle-plot" width="300">

### cellcycle stacked barplot
Similar to cellcycle plot but bars are stacked.
Error bars are shown but no stats analysis.

```python
from omero_screen_plots.combplot import stacked_barplot

stacked_barplot(
    df,
    condition_col="condition",
    conditions=conditions,
    selector_col="cell_line",
    selector_val="RPE1wt",
    title="RPE1 WT stacked barplot",
    save=False,
    path=None,
)
```
<img src="./images/stacked_barplot.png" alt="stacked_barplot" width="300">

## Installation

```bash
# Clone the repository
git clone https://github.com/Helfrid/omero-screen-plots.git
# Change into the project directory
cd omero-screen-plots
# Create and activate virtual environment
uv venv
source .venv/bin/activate
# Install the package
uv pip install -e .
```

## Project Structure
```text
omero-screen-plots/
├── src/
│ └── omero-screen-plots/
├── tests/
├── docs/
└── examples/
```
## Versioning

This project uses [Semantic Versioning](https://semver.org/) and [Conventional Commits](https://www.conventionalcommits.org/).

To bump the version use commitizen:
https://commitizen-tools.github.io/commitizen/

```bash
cz bump
```
## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`cz commit`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Authors


Created by Helfrid Hochegger
Email: hh65@sussex.ac.uk


## Dependencies

Requires Python 3.13 or greater

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

Thanks to the contributors of matplotlib, pandas, seaborn and scipy!
