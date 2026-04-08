# ============================================================
# imports
# ============================================================
import pandas as pd
import matplotlib.pyplot as plt
import os

# ============================================================
# load the data
# ============================================================
def load_run_data(run_name):
    """
    Loads eruption and summary data from Excel file.

    Args:
        run_name (str): Name of the run (e.g. '33', 'C100'). Used to build the file path.

    Returns:
        df_eruptions (DataFrame): Eruptions Open sheet data, with header rows skipped.
        df_summary (DataFrame): RunSummary sheet data.
    """
    path = f'../Runs/Lassen_{run_name}.XLSX'

    df_eruptions = pd.read_excel(path, sheet_name='Eruptions Open', skiprows=[1, 2])
    df_summary = pd.read_excel(path, sheet_name='RunSummary')

    return df_eruptions, df_summary

# ============================================================
# clean the set tp duplicates in the eruptions tab
# ============================================================
def clean_settp_duplicates(df):
    """
    Removes duplicate 'SetTP' rows from a DataFrame, keeping the first row always.

    Args:
        df (DataFrame): Raw DataFrame from load_run_data.

    Returns:
        df_cleaned (DataFrame): DataFrame with SetTP duplicate rows removed.
    """
    if df.index.name:
        # if the index is named, check the index for SetTP strings
        mask = ~(df.index.astype(str).str.contains('SetTP', na=False))
        mask.iloc[0] = True  # always keep the first row regardless
        df_cleaned = df[mask]
    else:
        # Otherwise check the first column for SetTP strings
        first_col = df.columns[0]
        mask = ~(df[first_col].astype(str).str.contains('SetTP', na=False))
        mask.iloc[0] = True  # always keep the first row regardless
        df_cleaned = df[mask]

    return df_cleaned

# ============================================================
# function to add anhydrous columns to the df
# ============================================================
def add_anhydrous_columns(df):
    """
    Adds anhydrous-normalized oxide columns to a DataFrame.
    Each oxide is divided by the sum of all non-volatile oxides and multiplied
    by 100, removing the dilution effect of H2O and CO2.
    New columns are added with the suffix '_anhy' (e.g. 'Melt SiO2_anhy wt%').
    H2O and CO2 are excluded from normalization but kept as-is for separate plotting.

    Args:
        df (DataFrame): Eruption DataFrame from load_run_data.

    Returns:
        df (DataFrame): Copy of input DataFrame with additional _anhy columns appended.
    """
    # Non-volatile oxides to normalize
    oxides = [
        'Melt SiO2 wt%', 'Melt TiO2 wt%', 'Melt Al2O3 wt%',
        'Melt Fe2O3 wt%', 'Melt Cr2O3 wt%', 'Melt FeO wt%',
        'Melt MnO wt%', 'Melt MgO wt%', 'Melt NiO wt%',
        'Melt CoO wt%', 'Melt CaO wt%', 'Melt Na2O wt%',
        'Melt K2O wt%', 'Melt P2O5 wt%'
    ]

    # Only normalize oxides that actually exist in this DataFrame
    present_oxides = [col for col in oxides if col in df.columns]

    # Sum of all non-volatile oxides per row (the anhydrous denominator)
    anhydrous_sum = df[present_oxides].sum(axis=1)

    df = df.copy()  # avoid mutating the original DataFrame
    for col in present_oxides:
        anhy_col = col.replace(' wt%', '_anhy wt%')
        df[anhy_col] = (df[col] / anhydrous_sum) * 100

    return df

# ============================================================
# function to plot oxides vs pressure
# ============================================================
def plot_all_oxides_vs_pressure(df_list, run_names, ncols=4, anhydrous=False):
    """
    Plots all melt oxide compositions vs pressure for one or more runs on a grid of subplots.
    Can plot either raw (hydrous) or anhydrous-normalized oxide values.

    Args:
        df_list (list of DataFrame): List of eruption DataFrames from load_run_data.
        run_names (list of str): Run name labels corresponding to each DataFrame.
        ncols (int): Number of columns in the subplot grid. Default is 4.
        anhydrous (bool): If True, plots anhydrous-normalized oxides (H2O and CO2 excluded
                          from normalization sum). H2O is still plotted raw. Default is False.

    Returns:
        fig (Figure): Matplotlib figure object.
    """
    if anhydrous:
        df_list = [add_anhydrous_columns(df) for df in df_list]
        oxides = [
            'Melt SiO2_anhy wt%', 'Melt TiO2_anhy wt%', 'Melt Al2O3_anhy wt%',
            'Melt Fe2O3_anhy wt%', 'Melt Cr2O3_anhy wt%', 'Melt FeO_anhy wt%',
            'Melt MnO_anhy wt%', 'Melt MgO_anhy wt%', 'Melt NiO_anhy wt%',
            'Melt CoO_anhy wt%', 'Melt CaO_anhy wt%', 'Melt Na2O_anhy wt%',
            'Melt K2O_anhy wt%', 'Melt P2O5_anhy wt%', 'Melt H2O wt%'
        ]
        title = 'Anhydrous Oxide Evolution'
    else:
        oxides = [
            'Melt SiO2 wt%', 'Melt TiO2 wt%', 'Melt Al2O3 wt%',
            'Melt Fe2O3 wt%', 'Melt Cr2O3 wt%', 'Melt FeO wt%',
            'Melt MnO wt%', 'Melt MgO wt%', 'Melt NiO wt%',
            'Melt CoO wt%', 'Melt CaO wt%', 'Melt Na2O wt%',
            'Melt K2O wt%', 'Melt P2O5 wt%', 'Melt H2O wt%',
            'Melt CO2 wt%'
        ]
        title = 'Oxide Evolution'

    run_colors = ['blue', 'orange', 'green', 'red', 'purple']

    # Calculate grid dimensions from number of oxides
    nrows = (len(oxides) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(5*ncols, 4*nrows))
    axes = axes.flatten()

    for i, oxide in enumerate(oxides):
        for df, run_name, color in zip(df_list, run_names, run_colors):
            if oxide in df.columns:
                axes[i].plot(df[oxide], df['Pressure (bars)'],
                            linewidth=2, color=color, marker='o',
                            markersize=3, alpha=0.7, label=run_name)

        axes[i].invert_yaxis()
        # Strip 'Melt' prefix and 'wt%' suffix for cleaner axis labels
        oxide_name = oxide.replace('Melt ', '').replace(' wt%', '')
        axes[i].set_xlabel(f'{oxide_name} (wt%)', fontsize=11)
        axes[i].set_ylabel('Pressure (bars)', fontsize=11)
        axes[i].set_title(oxide_name, fontsize=12, fontweight='bold')
        axes[i].grid(True, alpha=0.3, linestyle='--')
        axes[i].legend(fontsize=8, loc='best')

    # Hide any unused subplot panels
    for i in range(len(oxides), len(axes)):
        axes[i].axis('off')

    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    return fig

# ============================================================
# function to plot temperature vs pressure
# ============================================================
def plot_temperature_vs_pressure(df_list, run_names):
    """
    Plots temperature vs pressure for one or more runs on a single figure.

    Args:
        df_list (list of DataFrame): List of eruption DataFrames from load_run_data.
        run_names (list of str): Run name labels corresponding to each DataFrame.

    Returns:
        fig (Figure): Matplotlib figure object.
    """
    run_colors = ['blue', 'orange', 'green', 'red', 'purple']

    fig = plt.figure(figsize=(8, 6))

    for df, run_name, color in zip(df_list, run_names, run_colors):
        plt.plot(df['Temperature (deg C)'], df['Pressure (bars)'],
                 linewidth=2, color=color, marker='o', markersize=4,
                 alpha=0.7, label=run_name)

    plt.gca().invert_yaxis()
    plt.xlabel('Temperature (°C)', fontsize=12)
    plt.ylabel('Pressure (bars)', fontsize=12)
    plt.title('Temperature vs Pressure', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=10)
    plt.tight_layout()
    return fig

# ============================================================
# function to plot fluid mass versus temperature and pressure
# ============================================================
def plot_fluid_mass(df_list, run_names):
    """
    Plots fluid mass evolution for one or more runs as two side-by-side subplots:
    fluid mass vs temperature (left) and fluid mass vs pressure (right).

    Args:
        df_list (list of DataFrame): List of eruption DataFrames from load_run_data.
        run_names (list of str): Run name labels corresponding to each DataFrame.

    Returns:
        fig (Figure): Matplotlib figure object.
    """
    run_colors = ['blue', 'orange', 'green', 'red', 'purple']

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Left panel: fluid mass vs temperature
    for df, run_name, color in zip(df_list, run_names, run_colors):
        axes[0].plot(df['Temperature (deg C)'], df['fluid Mass (m.u.)'],
                     linewidth=2, color=color, marker='o', markersize=4,
                     alpha=0.7, label=run_name)

    axes[0].set_xlabel('Temperature (°C)', fontsize=12)
    axes[0].set_ylabel('Fluid Mass (m.u.)', fontsize=12)
    axes[0].set_title('Fluid Mass vs Temperature', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3, linestyle='--')
    axes[0].legend(fontsize=10)

    # Right panel: fluid mass vs pressure
    for df, run_name, color in zip(df_list, run_names, run_colors):
        axes[1].plot(df['fluid Mass (m.u.)'], df['Pressure (bars)'],
                     linewidth=2, color=color, marker='o', markersize=4,
                     alpha=0.7, label=run_name)

    axes[1].invert_yaxis()
    axes[1].set_xlabel('Fluid Mass (m.u.)', fontsize=12)
    axes[1].set_ylabel('Pressure (bars)', fontsize=12)
    axes[1].set_title('Fluid Mass vs Pressure', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3, linestyle='--')
    axes[1].legend(fontsize=10)

    fig.suptitle('Fluid Mass Evolution', fontsize=16, fontweight='bold', y=1.00)
    plt.tight_layout()
    return fig

# ============================================================
# function to plot crystallinity versus pressure
# ============================================================
def plot_pressure_crystallinity(df_list, run_names):
    """
    Plots solid mass vs pressure for one or more runs.

    Args:
        df_list (list of DataFrame): List of eruption DataFrames from load_run_data.
        run_names (list of str): Run name labels corresponding to each DataFrame.

    Returns:
        fig (Figure): Matplotlib figure object.
    """
    run_colors = ['blue', 'orange', 'green', 'red', 'purple']

    fig = plt.figure(figsize=(8, 6))

    for df, run_name, color in zip(df_list, run_names, run_colors):
        plt.plot(df['Solids Mass (m.u.)'], df['Pressure (bars)'],
                 linewidth=2, color=color, marker='o', markersize=4,
                 alpha=0.7, label=run_name)

    plt.gca().invert_yaxis()
    plt.xlabel('Solids Mass (m.u.)', fontsize=12)
    plt.ylabel('Pressure (bars)', fontsize=12)
    plt.title('Crystallinity vs Pressure', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=10)
    plt.tight_layout()
    return fig

# ============================================================
# function to save a figure
# ============================================================
def save_fig(fig, file_name, path='../figures'):
    """
    Saves a matplotlib figure as a PNG to the specified directory.

    Args:
        fig (Figure): Matplotlib figure object to save.
        file_name (str): Output filename. '.png' extension is added if not present.
        path (str): Directory to save the figure in. Default is '../figures'.

    Returns:
        None
    """
    # Append .png extension if not already present
    if not file_name.endswith('.png'):
        file_name += '.png'

    full_path = os.path.join(path, file_name)
    fig.savefig(full_path, dpi=300)

# ============================================================
# function to plot oxides versus silica
# ============================================================
def plot_all_oxides_vs_silica(df_list, run_names, ncols=4):
    """
    Plots all melt oxide compositions vs silica for one or more runs on a grid of subplots. 

    Args:
        df_list (list of DataFrame): List of eruption DataFrames from load_run_data.
        run_names (list of str): Run name labels corresponding to each DataFrame.
        ncols (int): Number of columns in the subplot grid. Default is 4.

    Returns:
        fig (Figure): Matplotlib figure object.
    """
    oxides = [
        'Melt SiO2 wt%', 'Melt TiO2 wt%', 'Melt Al2O3 wt%',
        'Melt Fe2O3 wt%', 'Melt Cr2O3 wt%', 'Melt FeO wt%',
        'Melt MnO wt%', 'Melt MgO wt%', 'Melt NiO wt%',
        'Melt CoO wt%', 'Melt CaO wt%', 'Melt Na2O wt%',
        'Melt K2O wt%', 'Melt P2O5 wt%', 'Melt H2O wt%',
        'Melt CO2 wt%'
    ]

    run_colors = ['blue', 'orange', 'green', 'red', 'purple']

    # Calculate grid dimensions from number of oxides
    nrows = (len(oxides) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(5*ncols, 4*nrows))
    axes = axes.flatten()

    for i, oxide in enumerate(oxides):
        for df, run_name, color in zip(df_list, run_names, run_colors):
            if oxide in df.columns:
                axes[i].plot(df[oxide], df['Melt SiO2 wt%'],
                            linewidth=2, color=color, marker='o',
                            markersize=3, alpha=0.7, label=run_name)

        axes[i].invert_yaxis()
        # Strip 'Melt' prefix and 'wt%' suffix for cleaner axis labels
        oxide_name = oxide.replace('Melt ', '').replace(' wt%', '')
        axes[i].set_xlabel(f'{oxide_name} (wt%)', fontsize=11)
        axes[i].set_ylabel('Silica (wt%)', fontsize=11)
        axes[i].set_title(oxide_name, fontsize=12, fontweight='bold')
        axes[i].grid(True, alpha=0.3, linestyle='--')
        axes[i].legend(fontsize=8, loc='best')

    # Hide any unused subplot panels
    for i in range(len(oxides), len(axes)):
        axes[i].axis('off')

    fig.suptitle('Oxide vs. Silica Evolution', fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    return fig
    
# ============================================================
# function to plot solids mass versus temperature and pressure
# ============================================================
def plot_solids_mass(df_list, run_names):
    """
    Plots solid mass evolution for one or more runs as two side-by-side subplots:
    solid mass vs temperature (left) and solid mass vs pressure (right).

    Args:
        df_list (list of DataFrame): List of eruption DataFrames from load_run_data.
        run_names (list of str): Run name labels corresponding to each DataFrame.

    Returns:
        fig (Figure): Matplotlib figure object.
    """
    run_colors = ['blue', 'orange', 'green', 'red', 'purple']

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Left panel: solid mass vs temperature
    for df, run_name, color in zip(df_list, run_names, run_colors):
        axes[0].plot(df['Temperature (deg C)'], df['Solids Mass (m.u.)'],
                     linewidth=2, color=color, marker='o', markersize=4,
                     alpha=0.7, label=run_name)

    axes[0].set_xlabel('Temperature (°C)', fontsize=12)
    axes[0].set_ylabel('Solid Mass (m.u.)', fontsize=12)
    axes[0].set_title('Solid Mass vs Temperature', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3, linestyle='--')
    axes[0].legend(fontsize=10)

    # Right panel: solid mass vs pressure
    for df, run_name, color in zip(df_list, run_names, run_colors):
        axes[1].plot(df['Solids Mass (m.u.)'], df['Pressure (bars)'],
                     linewidth=2, color=color, marker='o', markersize=4,
                     alpha=0.7, label=run_name)

    axes[1].invert_yaxis()
    axes[1].set_xlabel('Solid Mass (m.u.)', fontsize=12)
    axes[1].set_ylabel('Pressure (bars)', fontsize=12)
    axes[1].set_title('Solid Mass vs Pressure', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3, linestyle='--')
    axes[1].legend(fontsize=10)

    fig.suptitle('Solid Mass Evolution', fontsize=16, fontweight='bold', y=1.00)
    plt.tight_layout()
    return fig

# ============================================================
# function to parse through melts.out files
# ============================================================
def parse_melts_out(filepath):
    """
    Parses a MELTS .out file and extracts temperature, pressure, feldspar
    end-member compositions, and fluid volume fraction for each pressure step.
    Rows without feldspar or fluid present will have NaN for those columns.

    Args:
        filepath (str): Path to the MELTS .out file.

    Returns:
        df (DataFrame): One row per pressure step with columns:
                        'Temperature (deg C)', 'Pressure (kbars)', 'Pressure (bars)',
                        'Feldspar Albite (mol%)', 'Feldspar Anorthite (mol%)',
                        'Feldspar Sanidine (mol%)', 'Fluid Volume (cc)',
                        'System Volume (cc)', 'Fluid Volume Fraction'
    """
    import re

    with open(filepath, 'r') as f:
        content = f.read()

    # Each pressure step is separated by this delimiter
    blocks = content.split('**********----------**********')

    records = []
    for block in blocks:

        # Extract temperature and pressure from block header
        tp_match = re.search(r'T\s*=\s*([\d.]+)\s*\(C\).*?P\s*=\s*([\d.]+)\s*\(kbars\)', block)
        if not tp_match:
            continue

        T = float(tp_match.group(1))
        P_kbar = float(tp_match.group(2))
        P_bar = P_kbar * 1000  # convert to bars to match xlsx DataFrames

        # Extract feldspar end-members -- will be None if feldspar is not a stable phase
        albite = None
        anorthite = None
        sanidine = None
        feldspar_match = re.search(
            r'feldspar.*?albite\s+anorthite\s+sanidine\s+([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)',
            block, re.DOTALL
        )
        if feldspar_match:
            albite = float(feldspar_match.group(1))
            anorthite = float(feldspar_match.group(2))
            sanidine = float(feldspar_match.group(3))

        # Extract fluid volume if fluid is a stable phase
        fluid_V = None
        fluid_match = re.search(r'fluid\s+mass.*?V\s*=\s*([\d.]+)\s*\(cc\)', block, re.DOTALL)
        if fluid_match:
            fluid_V = float(fluid_match.group(1))

        # Extract system volume
        system_V = None
        system_match = re.search(r'System\s+mass.*?V\s*=\s*([\d.]+)\s*\(cc\)', block, re.DOTALL)
        if system_match:
            system_V = float(system_match.group(1))

        # Calculate fluid volume fraction -- None if fluid is not a stable phase
        fluid_vol_fraction = (fluid_V / system_V) if (fluid_V is not None and system_V is not None) else None

        records.append({
            'Temperature (deg C)': T,
            'Pressure (kbars)': P_kbar,
            'Pressure (bars)': P_bar,
            'Feldspar Albite (mol%)': albite,
            'Feldspar Anorthite (mol%)': anorthite,
            'Feldspar Sanidine (mol%)': sanidine,
            'Fluid Volume (cc)': fluid_V,
            'System Volume (cc)': system_V,
            'Fluid Volume Fraction': fluid_vol_fraction,
        })

    df = pd.DataFrame(records)
    # Drop duplicate pressure steps, keeping the last
    df = df.drop_duplicates(subset='Pressure (bars)', keep='last').reset_index(drop=True)
    return df
# ============================================================
# function to load melts.out
# ============================================================
def load_melts_out(melts_name):
    """
    Loads and parses a MELTS .out file for a given run from the tbl-files directory.

    Args:
        melts_name (str): Name of the run folder (e.g. '33', 'C100', 'D100', 'P100').

    Returns:
        df (DataFrame): Parsed output from parse_melts_out with temperature, pressure,
                        and feldspar end-member compositions.
    """
    path = f'../runs/tbl-files/{melts_name}/melts.out'
    return parse_melts_out(path)

# ============================================================
# function to plot anorthite versus pressure
# ============================================================
def plot_anorthite_vs_pressure(df_list, run_names):
    """
    Plots feldspar anorthite content vs pressure for one or more runs.
    Steps where feldspar is not a stable phase are automatically excluded.

    Args:
        df_list (list of DataFrame): List of DataFrames from load_melts_out.
        run_names (list of str): Run name labels corresponding to each DataFrame.

    Returns:
        fig (Figure): Matplotlib figure object.
    """
    run_colors = ['red', 'gold', 'seagreen', 'cyan', 'purple',
                  'pink', 'lime', 'dodgerblue']

    fig = plt.figure(figsize=(8, 6))

    for df, run_name, color in zip(df_list, run_names, run_colors):
        # Drop rows where feldspar is not a stable phase
        df_feld = df.dropna(subset=['Feldspar Anorthite (mol%)'])
        plt.plot(df_feld['Feldspar Anorthite (mol%)'], df_feld['Pressure (bars)'],
                 linewidth=2, color=color, marker='o', markersize=4,
                 alpha=0.7, label=run_name)

    plt.gca().invert_yaxis()
    plt.xlabel('Anorthite (mol%)', fontsize=12)
    plt.ylabel('Pressure (bars)', fontsize=12)
    plt.title('Feldspar Anorthite vs Pressure', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=10)
    plt.tight_layout()
    return fig



def plot_fluid_volume_fraction(df_list, run_names):
    """
    Plots fluid volume fraction vs pressure for one or more runs.
    Only plots steps where fluid is a stable phase (below ~1500 bars).

    Args:
        df_list (list of DataFrame): List of DataFrames from load_melts_out.
        run_names (list of str): Run name labels corresponding to each DataFrame.

    Returns:
        fig (Figure): Matplotlib figure object.
    """
    run_colors = ['blue', 'orange', 'green', 'red', 'purple']
    run_styles = [(1, 0), (5, 2), (5, 2, 1, 2), (1, 2)]

    fig = plt.figure(figsize=(8, 6))

    for df, run_name, color, style in zip(df_list, run_names, run_colors, run_styles):
        df_fluid = df.dropna(subset=['Fluid Volume Fraction'])
        plt.plot(df_fluid['Fluid Volume Fraction'], df_fluid['Pressure (bars)'],
                 linewidth=2, color=color, dashes=style,
                 marker='o', markersize=4, alpha=0.7, label=run_name)

    plt.gca().invert_yaxis()
    plt.xlabel('Fluid Volume Fraction', fontsize=12)
    plt.ylabel('Pressure (bars)', fontsize=12)
    plt.title('Fluid Volume Fraction vs Pressure', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=10)
    plt.tight_layout()
    return fig