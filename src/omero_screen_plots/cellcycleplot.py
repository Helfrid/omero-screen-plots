"""Module for cell cycle plotting.

This module provides three different cellcycle plots.

1. Cellcycle plot where each cellcycle phase is plotted separately
   with the repeat points and significance marks.
2. Stacked barplot where the cellcycle phases are stacked on top of each other.
3. Grouped stacked barplot where the stacked cellcycle phases are grouped by
   condition. Three repeats are plotted separately in one subgroup separated by
   a black box.
"""

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.patches import Patch, Rectangle

from omero_screen_plots.stats import set_significance_marks
from omero_screen_plots.utils import (
    grouped_x_positions,
    save_fig,
    selector_val_filter,
    show_repeat_points,
)

# Define figure size in inches
width = 9 / 2.54  # 10 cm
height = 6 / 2.54  # 6 cm

current_dir = Path(__file__).parent
style_path = (current_dir / "../../hhlab_style01.mplstyle").resolve()
plt.style.use(style_path)
prop_cycle = plt.rcParams["axes.prop_cycle"]
COLORS = prop_cycle.by_key()["color"]
print(COLORS)
pd.options.mode.chained_assignment = None


def cellcycle_plot(
    df: pd.DataFrame,
    conditions: list[str],
    condition_col: str = "condition",
    selector_col: str | None = "cell_line",
    selector_val: str | None = None,
    title: str | None = None,
    fig_size: tuple[float, float] = (6, 6),
    size_units: str = "cm",
    colors: list[str] = COLORS,
    save: bool = True,
    path: Path | None = None,
    tight_layout: bool = False,
    file_format: str = "pdf",
    dpi: int = 300,
) -> None:
    """Plot the cell cycle phases for each condition.

    Args:
        df: DataFrame containing cell cycle data.
        conditions: List of condition names to plot.
        condition_col: Column name for experimental condition.
        selector_col: Column name for selector (e.g., cell line).
        selector_val: Value to filter selector_col by.
        title: Plot title.
        fig_size: Dimensions of the figure. Default is 6 cm wide and 4 cm high.
        size_units: Units of the figure size. Default is "cm".
        colors: List of colors for plotting.
        save: Whether to save the figure.
        path: Path to save the figure.
        tight_layout: Whether to use tight layout. Default is False.
        file_format: Format of the figure. Default is "pdf".
        dpi: Resolution of the figure. Default is 300.
    """
    print(f"Plotting cell cycle quantifications for {selector_val}")
    if size_units == "cm":
        fig_size = (fig_size[0] / 2.54, fig_size[1] / 2.54)
    df1 = selector_val_filter(
        df, selector_col, selector_val, condition_col, conditions
    )
    assert df1 is not None
    df1 = cc_phase(df1, condition=condition_col)
    fig, ax = plt.subplots(2, 2, figsize=fig_size)
    ax_list = [ax[0, 0], ax[0, 1], ax[1, 0], ax[1, 1]]
    cellcycle = ["G1", "S", "G2/M", "Polyploid"]
    for i, phase in enumerate(cellcycle):
        axes = ax_list[i]
        df_phase = df1[
            (df1.cell_cycle == phase) & (df1[condition_col].isin(conditions))
        ]
        sns.barplot(
            data=df_phase,
            x=condition_col,
            y="percent",
            color=colors[i + 1],
            order=conditions,
            ax=axes,
        )
        show_repeat_points(
            df=df_phase,
            conditions=conditions,
            condition_col=condition_col,
            y_col="percent",
            ax=axes,
        )
        if df1.plate_id.nunique() >= 3:
            set_significance_marks(
                axes,
                df_phase,
                conditions,
                condition_col,
                "percent",
                axes.get_ylim()[1],
            )
        axes.set_title(f"{phase}", fontsize=6, y=1.05)
        if i in [1, 3]:
            axes.set_ylabel(None)
        if i in [0, 1]:
            axes.set_xticklabels([])
        else:
            axes.set_xticks(range(len(conditions)))
            axes.set_xticklabels(conditions, rotation=45, ha="right")
        axes.set_xlabel(None)
    if not title:
        title = f"Cellcycle Analysis {selector_val}"
    fig.suptitle(title, fontsize=8, weight="bold", x=0, y=1, ha="left")
    fig_title = title.replace(" ", "_")
    if save and path:
        save_fig(
            fig,
            path,
            fig_title,
            tight_layout=tight_layout,
            fig_extension=file_format,
            resolution=dpi,
        )


def cellcycle_stacked(
    df: pd.DataFrame,
    conditions: list[str],
    condition_col: str = "condition",
    selector_col: Optional[str] = "cell_line",
    selector_val: Optional[str] = None,
    y_err: bool = True,
    H3: bool = False,
    title: str | None = None,
    fig_size: tuple[float, float] = (6, 6),
    size_units: str = "cm",
    colors: list[str] = COLORS,
    save: bool = True,
    path: Path | None = None,
    tight_layout: bool = False,
    file_format: str = "pdf",
    dpi: int = 300,
    group_size: int = 1,
    within_group_spacing: float = 0.2,
    between_group_gap: float = 0.5,
    bar_width: float = 0.5,
) -> None:
    """Create a stacked barplot for cell cycle phase proportions, with optional grouping of conditions on the x-axis.

    Args:
        df: DataFrame containing cell cycle data.
        conditions: List of condition names to plot.
        condition_col: Column name for experimental condition.
        selector_col: Column name for selector (e.g., cell line).
        selector_val: Value to filter selector_col by.
        y_err: Whether to show error bars. Default is True.
        H3: Whether to use H3 phase naming.
        title: Plot title.
        fig_size: Dimensions of the figure. Default is 6 cm wide and 4 cm high.
        size_units: Units of the figure size. Default is "cm".
        colors: List of colors for plotting.
        save: Whether to save the figure.
        path: Path to save the figure.
        tight_layout: Whether to use tight layout. Default is False.
        file_format: Format of the figure. Default is "pdf".
        dpi: Resolution of the figure. Default is 300.
        group_size: Number of conditions per group on the x-axis (default 1 = no grouping).
        within_group_spacing: Spacing between bars within a group (default 0.5).
        between_group_gap: Spacing between groups (default 1.0).
        bar_width: Width of each bar (default 0.5).
    """
    if size_units == "cm":
        fig_size = (fig_size[0] / 2.54, fig_size[1] / 2.54)
    df1 = selector_val_filter(
        df, selector_col, selector_val, condition_col, conditions
    )
    assert df1 is not None
    df_mean, df_std = prop_pivot(df1, condition_col, conditions, H3)
    n_conditions = len(conditions)
    if H3:
        phases = ["Polyploid", "M", "G2", "S", "G1", "Sub-G1"]
    else:
        phases = ["Polyploid", "G2/M", "S", "G1", "Sub-G1"]
    # Use grouped_x_positions for x-axis positions
    x_positions = grouped_x_positions(
        n_conditions,
        group_size=group_size,
        bar_width=bar_width,
        within_group_spacing=within_group_spacing,
        between_group_gap=between_group_gap,
    )
    x_labels = conditions
    fig, ax = plt.subplots(figsize=fig_size)
    bottoms = [0] * len(x_positions)
    for k, phase in enumerate(phases):
        values = df_mean[phase].values
        ax.bar(
            x_positions,
            values,  # type: ignore
            bar_width,
            bottom=bottoms,
            color=colors[k],
            label=phase,
            edgecolor="white",
            linewidth=0.2,
            alpha=0.9,
            yerr=df_std[phase].values,
        )
        bottoms = [
            bottoms[i] + (values[i] if not pd.isna(values[i]) else 0)
            for i in range(len(values))
        ]
    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_labels, rotation=30, ha="right")
    ax.set_xlabel(condition_col)
    ax.set_ylabel("% of population")
    ax.set_ylim(0, 110)
    # Legend
    handles, labels = ax.get_legend_handles_labels()
    handles, labels = handles[::-1], labels[::-1]
    ax.legend(
        handles,
        labels,
        title="CellCyclePhase",
        bbox_to_anchor=(1.25, 1),
        loc="upper right",
    )
    ax.grid(False)
    if not title:
        title = f"stackedbarplot_{selector_val}"
    fig.suptitle(title, fontsize=8, weight="bold", x=0, y=1.01, ha="left")
    fig_title = title.replace(" ", "_")
    if save and path:
        save_fig(
            fig,
            path,
            fig_title,
            tight_layout=tight_layout,
            fig_extension=file_format,
            resolution=dpi,
        )


def cellcycle_grouped(
    df: pd.DataFrame,
    conditions: list[str],
    group_size: int = 2,
    condition_col: str = "condition",
    selector_col: Optional[str] = "cell_line",
    selector_val: Optional[str] = None,
    phases: Optional[list[str]] = None,
    title: Optional[str] = None,
    ax: Optional[Axes] = None,
    x_label: bool = True,
    fig_size: tuple[float, float] = (6, 6),
    size_units: str = "cm",
    colors: list[str] = COLORS,
    save: bool = True,
    path: Optional[Path] = None,
    tight_layout: bool = False,
    file_format: str = "pdf",
    dpi: int = 300,
    repeat_offset: float = 0.18,
    within_group_spacing: float = 0.2,
    between_group_gap: float = 0.5,
) -> None:
    """Create a grouped stacked barplot for phase proportions, with triplicates boxed and grouped on the x-axis.

    Group bars on the x-axis by group_size, and center three repeats per condition. Larger groups of conditions can be created using group_size, within_group_spacing, and between_group_gap.

    Args:
        df: DataFrame containing cell cycle data.
        conditions: List of condition names to plot.
        group_size: Number of conditions per group on the x-axis.
        condition_col: Column name for experimental condition.
        selector_col: Column name for selector (e.g., cell line).
        selector_val: Value to filter selector_col by.
        phases: List of cell cycle phases.
        title: Plot title.
        ax: Matplotlib axis. If None, a new figure is created.
        x_label: Whether to show the x-axis label. Default is True.
        fig_size: Dimensions of the figure. Default is 6 cm wide and 4 cm high.
        size_units: Units of the figure size. Default is "cm".
        colors: List of colors for plotting.
        save: Whether to save the figure.
        path: Path to save the figure.
        tight_layout: Whether to use tight layout. Default is False.
        file_format: Format of the figure. Default is "pdf".
        dpi: Resolution of the figure. Default is 300.
        repeat_offset: Offset for repeat bars.
        within_group_spacing: Spacing between bars within a group.
        between_group_gap: Spacing between groups.
        x_label: Whether to show the x-axis label. Default is True.
    """
    if size_units == "cm":
        fig_size = (fig_size[0] / 2.54, fig_size[1] / 2.54)
    if ax is None:
        fig, ax = plt.subplots(figsize=fig_size)
    if phases is None:
        custom_phases = False
        phases = ["Polyploid", "G2/M", "S", "G1", "Sub-G1"]
    else:
        custom_phases = True
    df1 = selector_val_filter(
        df, selector_col, selector_val, condition_col, conditions
    )
    assert df1 is not None
    df1 = cc_phase(df1, condition=condition_col)
    n_repeats = 3
    repeat_ids = sorted(df1["plate_id"].unique())[:n_repeats]
    n_conditions = len(conditions)
    # Use grouped_x_positions for x-axis positions of each condition group
    x_base_positions = grouped_x_positions(
        n_conditions,
        group_size=group_size,
        within_group_spacing=within_group_spacing,
        between_group_gap=between_group_gap,
    )

    plot_triplicate_bars(
        ax,
        df1,
        conditions,
        repeat_ids,
        x_base_positions,
        repeat_offset,
        phases,
        colors,
        condition_col,
    )
    ax.set_xticks(x_base_positions)
    if x_label:
        ax.set_xticklabels(conditions, rotation=45, ha="right")
    else:
        ax.set_xticklabels([])
    ax.set_xlabel("")
    ax.set_ylabel("% of population")
    draw_triplicate_boxes(
        ax,
        df1,
        conditions,
        repeat_ids,
        x_base_positions,
        repeat_offset,
        repeat_offset * 1.05,
        n_repeats,
        condition_col,
    )
    build_phase_legend(ax, phases, colors, custom_phases)

    if not title:
        title = f"cellcycle grouped plot {selector_val}"
    fig.suptitle(title, fontsize=8, weight="bold", x=0, y=1.01, ha="left")
    fig_title = title.replace(" ", "_")
    if save and path:
        save_fig(
            fig,
            path,
            fig_title,
            tight_layout=tight_layout,
            fig_extension=file_format,
            resolution=dpi,
        )


# ------------------------helper functions-------------------------------


def cc_phase(df: pd.DataFrame, condition: str = "condition") -> pd.DataFrame:
    """Calculate the percentage of cells in each cell cycle phase for each condition.

    Args:
        df: DataFrame containing cell cycle data.
        condition: Column name for experimental condition.

    Returns:
        DataFrame with percentage of cells in each phase per condition.
    """
    return (
        (
            df.groupby(["plate_id", "cell_line", condition, "cell_cycle"])[
                "experiment"
            ].count()
            / df.groupby(["plate_id", "cell_line", condition])[
                "experiment"
            ].count()
            * 100
        )
        .reset_index()
        .rename(columns={"experiment": "percent"})
    )


def prop_pivot(
    df: pd.DataFrame, condition: str, conditions: list[str], H3: bool = False
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Pivot the cell cycle proportion dataframe and get the mean and std of each phase.

    Args:
        df: DataFrame containing cell cycle data.
        condition: Column name for experimental condition.
        conditions: List of condition names.
        H3: Whether to use H3 phase naming.

    Returns:
        Tuple of (mean DataFrame, std DataFrame) for each phase.
    """
    df_prop = cc_phase(df, condition=condition)
    cc_phases = (
        ["Sub-G1", "G1", "S", "G2/M", "Polyploid"]
        if not H3
        else ["Sub-G1", "G1", "S", "G2", "M", "Polyploid"]
    )
    df_prop1 = df_prop.copy()
    df_prop1[condition] = pd.Categorical(
        df_prop1[condition], categories=conditions, ordered=True
    )
    df_prop1["cell_cycle"] = pd.Categorical(
        df_prop1["cell_cycle"], categories=cc_phases, ordered=True
    )
    df_mean = (
        df_prop1.groupby([condition, "cell_cycle"], observed=False)["percent"]
        .mean()
        .sort_index(level=condition)
        .reset_index()
        .pivot_table(columns=["cell_cycle"], index=[condition], observed=False)
    )
    df_mean.columns = df_mean.columns.droplevel(0)
    df_mean = df_mean[cc_phases]
    if len(df_prop1.plate_id.unique()) > 1:
        df_std = (
            df_prop1.groupby([condition, "cell_cycle"], observed=False)[
                "percent"
            ]
            .std()
            .sort_index(level=condition)
            .reset_index()
            .pivot_table(
                columns=["cell_cycle"], index=[condition], observed=False
            )
        )
        df_std.columns = df_std.columns.droplevel(0)
        df_std = df_std[cc_phases]
    else:
        df_std = pd.DataFrame(0, index=df_mean.index, columns=df_mean.columns)
    return df_mean, df_std


def plot_triplicate_bars(
    ax: Axes,
    df1: pd.DataFrame,
    conditions: list[str],
    repeat_ids: list[str],
    x_base_positions: list[float],
    repeat_offset: float,
    phases: list[str],
    colors: list[str],
    condition_col: str,
) -> None:
    """Plot triplicate bars for grouped stacked barplot.

    Args:
        ax: Matplotlib axis.
        df1: DataFrame with cell cycle data.
        conditions: List of condition names.
        repeat_ids: List of repeat plate IDs.
        x_base_positions: List of x positions for each condition.
        repeat_offset: Offset for repeat bars.
        phases: List of cell cycle phases.
        colors: List of colors for phases.
        condition_col: Column name for experimental condition.
    """
    for cond_idx, cond in enumerate(conditions):
        for rep_idx, plate_id in enumerate(repeat_ids):
            xpos = x_base_positions[cond_idx] + (rep_idx - 1) * repeat_offset
            plate_data = df1[
                (df1[condition_col] == cond) & (df1["plate_id"] == plate_id)
            ]
            if not plate_data.empty:
                pivot = plate_data.set_index("cell_cycle")["percent"]
                y_bottom = 0
                for i, phase in enumerate(phases):
                    val = pivot.get(phase, 0)
                    ax.bar(
                        xpos,
                        val,
                        width=repeat_offset * 1.05,
                        bottom=y_bottom,
                        color=colors[i % len(colors)],
                        edgecolor="white",
                        linewidth=0.7,
                    )
                    y_bottom += val


def draw_triplicate_boxes(
    ax: Axes,
    df1: pd.DataFrame,
    conditions: list[str],
    repeat_ids: list[str],
    x_base_positions: list[float],
    repeat_offset: float,
    bar_width: float,
    n_repeats: int,
    condition_col: str,
) -> None:
    """Draw boxes around triplicate bars in grouped stacked barplot.

    Args:
        ax: Matplotlib axis.
        df1: DataFrame with cell cycle data.
        conditions: List of condition names.
        repeat_ids: List of repeat plate IDs.
        x_base_positions: List of x positions for each condition.
        repeat_offset: Offset for repeat bars.
        bar_width: Width of each bar.
        n_repeats: Number of repeats.
        condition_col: Column name for experimental condition.
    """
    y_min = 0
    for cond_idx, cond in enumerate(conditions):
        trip_xs = [
            x_base_positions[cond_idx] + (rep_idx - 1) * repeat_offset
            for rep_idx in range(n_repeats)
        ]
        trip_data = df1[df1[condition_col] == cond]
        trip_max = max(
            (
                trip_data[trip_data["plate_id"] == plate_id]["percent"].sum()
                for plate_id in repeat_ids
            ),
            default=0,
        )
        y_max_box = trip_max
        left = min(trip_xs) - bar_width / 2
        right = max(trip_xs) + bar_width / 2
        rect = Rectangle(
            (left, y_min),
            width=right - left,
            height=y_max_box - y_min,
            linewidth=0.5,
            edgecolor="black",
            facecolor="none",
            zorder=10,
        )
        ax.add_patch(rect)


def build_phase_legend(
    ax: Axes, phases: list[str], colors: list[str], custom_phases: bool
) -> None:
    """Build legend for cell cycle phases.

    Args:
        ax: Matplotlib axis.
        phases: List of cell cycle phases.
        colors: List of colors for phases.
        custom_phases: Whether to use custom phases.
    """
    labels = ["8N+", "4N", "S", "2N", "2N-"] if not custom_phases else phases
    legend_handles = [
        Patch(
            facecolor=colors[i % len(colors)], edgecolor="white", label=phase
        )
        for i, phase in enumerate(labels)
    ][::-1]
    # Add a dummy handle with a long invisible label for fixed width
    dummy_label = " " * 20
    legend_handles.append(
        Patch(facecolor="none", edgecolor="none", label=dummy_label)
    )
    ax.legend(
        handles=legend_handles,
        title="",
        bbox_to_anchor=(0.95, 1),
        loc="upper left",
        frameon=False,
    )
