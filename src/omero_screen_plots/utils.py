from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.figure import Figure

current_dir = Path(__file__).parent
style_path = (current_dir / "../../hhlab_style01.mplstyle").resolve()
plt.style.use(style_path)
prop_cycle = plt.rcParams["axes.prop_cycle"]
COLORS = prop_cycle.by_key()["color"]


def save_fig(
    fig: Figure,
    path: Path,
    fig_id: str,
    tight_layout: bool = True,
    fig_extension: str = "pdf",
    resolution: int = 300,
) -> None:
    """
    Save a matplotlib figure to a file.

    Parameters
    ----------
    fig : Figure
        The figure to save.
    path : Path
        The path for saving the figure.
    fig_id : str
        The name of the saved figure.
    tight_layout : bool, optional
        Whether to use tight layout (default is True).
    fig_extension : str, optional
        The file extension for the saved figure (default is 'pdf').
    resolution : int, optional
        The resolution of the saved figure in dpi (default is 300).

    Returns
    -------
    None
        Saves the figure in the specified format.
    """

    dest = path / f"{fig_id}.{fig_extension}"
    print("Saving figure", fig_id)
    if tight_layout:
        fig.tight_layout()
    plt.savefig(
        dest,
        format=fig_extension,
        dpi=resolution,
        facecolor="white",
        edgecolor="white",
    )


def selector_val_filter(
    df: pd.DataFrame,
    selector_col: Optional[str],
    selector_val: Optional[str],
    condition_col: Optional[str],
    conditions: Optional[list[str]],
) -> Optional[pd.DataFrame]:
    """Check if selector_val is provided for selector_col and filter df"""
    if condition_col and conditions:
        df = df[df[condition_col].isin(conditions)].copy()
    if selector_col and selector_val:
        return df[df[selector_col] == selector_val].copy()
    elif selector_col:
        raise ValueError(f"selector_val for {selector_col} must be provided")
    else:
        return df.copy()


def get_repeat_points(
    df: pd.DataFrame, condition_col: str, y_col: str
) -> pd.DataFrame:
    return df.groupby(["plate_id", condition_col])[y_col].count().reset_index()


def show_repeat_points(
    df: pd.DataFrame,
    conditions: list[str],
    condition_col: str,
    y_col: str,
    ax: Axes,
) -> None:
    """Show repeat points"""

    sns.stripplot(
        data=df,
        x=condition_col,
        y=y_col,
        marker="o",
        size=3,
        color="lightgray",
        dodge=True,
        legend=False,
        order=conditions,
        ax=ax,
        edgecolor="black",
        linewidth=0.5,
    )


def select_datapoints(
    df: pd.DataFrame, conditions: list[str], condition_col: str, n: int = 30
) -> pd.DataFrame:
    """Select 30 random datapoints per category and plate-id"""
    df_sampled = pd.DataFrame()
    for condition in conditions:
        for plate_id in df.plate_id.unique():
            df_sub = df[
                (df[condition_col] == condition) & (df.plate_id == plate_id)
            ]
            if len(df_sub) > n:
                df_sub = df_sub.sample(n=n, random_state=1)
                df_sampled = pd.concat([df_sampled, df_sub])
    return df_sampled
