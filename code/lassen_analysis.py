# ============================================================
# imports
# ============================================================
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import seaborn as sns

# ============================================================
# load the data
# ============================================================
def load_run_data(run_name):
    path = f'../Runs/Lassen_{run_name}.XLSX'

    df_eruptions = pd.read_excel(path, sheet_name='Eruptions Open', skiprows=[1, 2])
    df_summary = pd.read_excel(path, sheet_name='RunSummary')

    return df_eruptions, df_summary

# ============================================================
# clean the set tp duplicates in the eruptions tab
# ============================================================
def clean_settp_duplicates(df):
    if df.index.name:
        mask = ~(df.index.astype(str).str.contains('SetTP', na=False))
        mask.iloc[0] = True  # always keep the first row regardless
        df_cleaned = df[mask]
    else:
        first_col = df.columns[0]
        mask = ~(df[first_col].astype(str).str.contains('SetTP', na=False))
        mask.iloc[0] = True
        df_cleaned = df[mask]

    return df_cleaned

# ============================================================
# function to add anhydrous columns to the df
# ============================================================
def add_anhydrous_columns(df):
    # Non-volatile oxides to normalize
    oxides = [
        'Melt SiO2 wt%', 'Melt TiO2 wt%', 'Melt Al2O3 wt%',
        'Melt Fe2O3 wt%', 'Melt Cr2O3 wt%', 'Melt FeO wt%',
        'Melt MnO wt%', 'Melt MgO wt%', 'Melt NiO wt%',
        'Melt CoO wt%', 'Melt CaO wt%', 'Melt Na2O wt%',
        'Melt K2O wt%', 'Melt P2O5 wt%'
    ]

    present_oxides = [col for col in oxides if col in df.columns]

    anhydrous_sum = df[present_oxides].sum(axis=1)

    df = df.copy()
    for col in present_oxides:
        anhy_col = col.replace(' wt%', '_anhy wt%')
        df[anhy_col] = (df[col] / anhydrous_sum) * 100

    return df

# ============================================================
# function to plot oxides vs pressure
# ============================================================
def plot_all_oxides_vs_pressure(df_list, run_names, ncols=4, anhydrous=False):
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

    run_colors = [
    '#e6194b',
    '#f58231',
    '#ffe119',
    '#3cb44b',
    '#4363d8',
    '#911eb4',
    '#42d4f4', 
    '#f032e6',
    ]

    run_styles = [
    (0, (3, 5, 1, 5)),
    (0, (3, 10, 1, 10)),
    (0, (3, 10, 1, 10, 1, 10)),
    (0, (5, 1)),
    (0, (1, 10)),
    (0, (1, 5)),
    (0, (5, 5)),
    (0, (3, 1, 1, 1)),]

    # calculate grid dimensions from number of oxides
    nrows = (len(oxides) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(5*ncols, 4*nrows))
    axes = axes.flatten()

    for i, oxide in enumerate(oxides):
        for df, run_name, color, style in zip(df_list, run_names, run_colors, run_styles):
            if oxide in df.columns:
                axes[i].plot(df[oxide], df['Pressure (bars)'],
                            linewidth=2, color=color, linestyle=style, marker='o',
                            markersize=3, alpha=0.7, label=run_name)

        axes[i].invert_yaxis()
        oxide_name = oxide.replace('Melt ', '').replace(' wt%', '')
        axes[i].set_xlabel(f'{oxide_name} (wt%)', fontsize=11)
        axes[i].set_ylabel('Pressure (bars)', fontsize=11)
        axes[i].set_title(oxide_name, fontsize=12, fontweight='bold')
        axes[i].grid(True, alpha=0.3, linestyle='--')
        axes[i].legend(fontsize=8, loc='best')

    for i in range(len(oxides), len(axes)):
        axes[i].axis('off')

    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    return fig

# ============================================================
# function to plot temperature vs pressure
# ============================================================
def plot_temperature_vs_pressure(df_list, run_names):
    run_colors = [
    '#e6194b',
    '#f58231',
    '#ffe119', 
    '#3cb44b',
    '#4363d8',
    '#911eb4',
    '#42d4f4',
    '#f032e6',
    ]
    
    run_styles = [
    (0, (3, 5, 1, 5)),
    (0, (3, 10, 1, 10)),
    (0, (3, 10, 1, 10, 1, 10)),
    (0, (5, 1)),
    (0, (1, 10)),
    (0, (1, 5)),
    (0, (5, 5)),
    (0, (3, 1, 1, 1)),]

    fig = plt.figure(figsize=(8, 6))

    for df, run_name, color, style in zip(df_list, run_names, run_colors, run_styles):
        plt.plot(df['Temperature (deg C)'], df['Pressure (bars)'],
                 linewidth=2, color=color, linestyle=style, marker='o', markersize=4,
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
    run_colors = [
    '#e6194b',
    '#f58231',
    '#ffe119', 
    '#3cb44b',
    '#4363d8',
    '#911eb4',
    '#42d4f4',
    '#f032e6',
    ]

    run_styles = [
    (0, (3, 5, 1, 5)),
    (0, (3, 10, 1, 10)),
    (0, (3, 10, 1, 10, 1, 10)),
    (0, (5, 1)),
    (0, (1, 10)),
    (0, (1, 5)),
    (0, (5, 5)),
    (0, (3, 1, 1, 1)),]

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for df, run_name, color, style in zip(df_list, run_names, run_colors, run_styles):
        axes[0].plot(df['Temperature (deg C)'], df['fluid Mass (m.u.)'],
                     linewidth=2, color=color, linestyle=style, marker='o', markersize=4,
                     alpha=0.7, label=run_name)

    axes[0].set_xlabel('Temperature (°C)', fontsize=12)
    axes[0].set_ylabel('Fluid Mass (m.u.)', fontsize=12)
    axes[0].set_title('Fluid Mass vs Temperature', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3, linestyle='--')
    axes[0].legend(fontsize=10)

    for df, run_name, color, style in zip(df_list, run_names, run_colors, run_styles):
        axes[1].plot(df['fluid Mass (m.u.)'], df['Pressure (bars)'],
                     linewidth=2, color=color, linestyle=style, marker='o', markersize=4,
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
    run_colors = [
    '#e6194b',
    '#f58231',
    '#ffe119', 
    '#3cb44b',
    '#4363d8',
    '#911eb4',
    '#42d4f4',
    '#f032e6',
    ]

    run_styles = [
    (0, (3, 5, 1, 5)),
    (0, (3, 10, 1, 10)),
    (0, (3, 10, 1, 10, 1, 10)),
    (0, (5, 1)),
    (0, (1, 10)),
    (0, (1, 5)),
    (0, (5, 5)),
    (0, (3, 1, 1, 1)),]

    fig = plt.figure(figsize=(8, 6))

    for df, run_name, color, style in zip(df_list, run_names, run_colors, run_styles):
        plt.plot(df['Solids Mass (m.u.)'], df['Pressure (bars)'],
                 linewidth=2, color=color, linestyle=style, marker='o', markersize=4,
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
    if not file_name.endswith('.png'):
        file_name += '.png'

    full_path = os.path.join(path, file_name)
    fig.savefig(full_path, dpi=300)

# ============================================================
# function to plot oxides versus silica
# ============================================================
def plot_all_oxides_vs_silica(df_list, run_names, ncols=4):
    oxides = [
        'Melt SiO2 wt%', 'Melt TiO2 wt%', 'Melt Al2O3 wt%',
        'Melt Fe2O3 wt%', 'Melt Cr2O3 wt%', 'Melt FeO wt%',
        'Melt MnO wt%', 'Melt MgO wt%', 'Melt NiO wt%',
        'Melt CoO wt%', 'Melt CaO wt%', 'Melt Na2O wt%',
        'Melt K2O wt%', 'Melt P2O5 wt%', 'Melt H2O wt%',
        'Melt CO2 wt%'
    ]

    run_colors = [
    '#e6194b',
    '#f58231',
    '#ffe119', 
    '#3cb44b',
    '#4363d8',
    '#911eb4',
    '#42d4f4',
    '#f032e6',
    ]

    run_styles = [
    (0, (3, 5, 1, 5)),
    (0, (3, 10, 1, 10)),
    (0, (3, 10, 1, 10, 1, 10)),
    (0, (5, 1)),
    (0, (1, 10)),
    (0, (1, 5)),
    (0, (5, 5)),
    (0, (3, 1, 1, 1)),]

    nrows = (len(oxides) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(5*ncols, 4*nrows))
    axes = axes.flatten()

    for i, oxide in enumerate(oxides):
        for df, run_name, color, style in zip(df_list, run_names, run_colors, run_styles):
            if oxide in df.columns:
                axes[i].plot(df[oxide], df['Melt SiO2 wt%'],
                            linewidth=2, color=color, linestyle=style, marker='o',
                            markersize=3, alpha=0.7, label=run_name)

        axes[i].invert_yaxis()
        oxide_name = oxide.replace('Melt ', '').replace(' wt%', '')
        axes[i].set_xlabel(f'{oxide_name} (wt%)', fontsize=11)
        axes[i].set_ylabel('Silica (wt%)', fontsize=11)
        axes[i].set_title(oxide_name, fontsize=12, fontweight='bold')
        axes[i].grid(True, alpha=0.3, linestyle='--')
        axes[i].legend(fontsize=8, loc='best')

    for i in range(len(oxides), len(axes)):
        axes[i].axis('off')

    fig.suptitle('Oxide vs. Silica Evolution', fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    return fig
    
# ============================================================
# function to plot solids mass versus temperature and pressure
# ============================================================
def plot_solids_mass(df_list, run_names):
    run_colors = [
    '#e6194b',
    '#f58231',
    '#ffe119', 
    '#3cb44b',
    '#4363d8',
    '#911eb4',
    '#42d4f4',
    '#f032e6',
    ]

    run_styles = [
    (0, (3, 5, 1, 5)),
    (0, (3, 10, 1, 10)),
    (0, (3, 10, 1, 10, 1, 10)),
    (0, (5, 1)),
    (0, (1, 10)),
    (0, (1, 5)),
    (0, (5, 5)),
    (0, (3, 1, 1, 1)),]

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for df, run_name, color, style in zip(df_list, run_names, run_colors, run_styles):
        axes[0].plot(df['Temperature (deg C)'], df['Solids Mass (m.u.)'],
                     linewidth=2, color=color, linestyle=style, marker='o', markersize=4,
                     alpha=0.7, label=run_name)

    axes[0].set_xlabel('Temperature (°C)', fontsize=12)
    axes[0].set_ylabel('Solid Mass (m.u.)', fontsize=12)
    axes[0].set_title('Solid Mass vs Temperature', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3, linestyle='--')
    axes[0].legend(fontsize=10)

    for df, run_name, color, style in zip(df_list, run_names, run_colors, run_styles):
        axes[1].plot(df['Solids Mass (m.u.)'], df['Pressure (bars)'],
                     linewidth=2, color=color, linestyle=style, marker='o', markersize=4,
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
    import re

    with open(filepath, 'r') as f:
        content = f.read()

    blocks = content.split('**********----------**********')

    records = []
    for block in blocks:

        # extract temperature and pressure from block header
        tp_match = re.search(r'T\s*=\s*([\d.]+)\s*\(C\).*?P\s*=\s*([\d.]+)\s*\(kbars\)', block)
        if not tp_match:
            continue

        T = float(tp_match.group(1))
        P_kbar = float(tp_match.group(2))
        P_bar = P_kbar * 1000  # convert to bars

        # extract feldspar end-members
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

        # extract fluid volume if fluid is a stable phase
        fluid_V = None
        fluid_match = re.search(r'fluid\s+mass.*?V\s*=\s*([\d.]+)\s*\(cc\)', block, re.DOTALL)
        if fluid_match:
            fluid_V = float(fluid_match.group(1))

        # extract system volume
        system_V = None
        system_match = re.search(r'System\s+mass.*?V\s*=\s*([\d.]+)\s*\(cc\)', block, re.DOTALL)
        if system_match:
            system_V = float(system_match.group(1))

        # calculate fluid volume fraction
        fluid_vol_fraction = (fluid_V / system_V) if (fluid_V is not None and system_V is not None) else None

        # extract system density
        system_density = None
        density_match = re.search(r'System\s+mass.*?density\s*=\s*([\d.]+)\s*\(gm/cc\)', block, re.DOTALL)
        if density_match:
            system_density = float(density_match.group(1))

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
            'System Density (gm/cc)': system_density,
        })

    df = pd.DataFrame(records)
    df = df.drop_duplicates(subset='Pressure (bars)', keep='last').reset_index(drop=True)
    return df

# ============================================================
# function to load melts.out
# ============================================================
def load_melts_out(melts_name):
    path = f'../runs/tbl-files/{melts_name}/melts.out'
    return parse_melts_out(path)

def plot_anorthite_vs_pressure(df_list, run_names):
    run_colors = [
    '#e6194b',
    '#f58231',
    '#ffe119', 
    '#3cb44b',
    '#4363d8',
    '#911eb4',
    '#42d4f4',
    '#f032e6',
    ]
    run_styles = [
        (0, (3, 5, 1, 5)), (0, (3, 10, 1, 10)), (0, (3, 10, 1, 10, 1, 10)),
        (0, (5, 1)), (0, (1, 10)), (0, (1, 5)), (0, (5, 5)), (0, (3, 1, 1, 1)),
    ]

    # observed anorthite range
    SALISBURY_MIN = 29.4
    SALISBURY_MAX = 70.7

    fig = plt.figure(figsize=(8, 6))

    plt.axvspan(SALISBURY_MIN, SALISBURY_MAX,
                alpha=0.12, color='gray',
                label='Salisbury et al. observed range')

    plt.axvline(SALISBURY_MIN, color='gray', linewidth=0.8,
                linestyle='--', alpha=0.6)
    plt.axvline(SALISBURY_MAX, color='gray', linewidth=0.8,
                linestyle='--', alpha=0.6)

    for df, run_name, color, style in zip(df_list, run_names, run_colors, run_styles):
        df_feld = df.dropna(subset=['Feldspar Anorthite (mol%)'])
        plt.plot(df_feld['Feldspar Anorthite (mol%)'], df_feld['Pressure (bars)'],
                 linewidth=2, color=color, linestyle=style, marker='o',
                 markersize=4, alpha=0.7, label=run_name)

    plt.gca().invert_yaxis()
    plt.xlabel('Anorthite (mol%)', fontsize=12)
    plt.ylabel('Pressure (bars)', fontsize=12)
    plt.title('Feldspar Anorthite vs Pressure', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=9)
    plt.tight_layout()
    return fig

# ============================================================
# function to plot fluid volume fraction
# ============================================================

def plot_fluid_volume_fraction(df_list, run_names):
    run_colors = [
    '#e6194b',
    '#f58231',
    '#ffe119', 
    '#3cb44b',
    '#4363d8',
    '#911eb4',
    '#42d4f4',
    '#f032e6',
    ]
        
    run_styles = [
    (0, (3, 5, 1, 5)),
    (0, (3, 10, 1, 10)),
    (0, (3, 10, 1, 10, 1, 10)),
    (0, (5, 1)),
    (0, (1, 10)),
    (0, (1, 5)),
    (0, (5, 5)),
    (0, (3, 1, 1, 1)),]

    fig = plt.figure(figsize=(8, 6))

    for df, run_name, color, style in zip(df_list, run_names, run_colors, run_styles):
        df_fluid = df.dropna(subset=['Fluid Volume Fraction'])
        plt.plot(df_fluid['Fluid Volume Fraction'], df_fluid['Pressure (bars)'],
                 linewidth=2, color=color, linestyle=style,
                 marker='o', markersize=4, alpha=0.7, label=run_name)

    plt.gca().invert_yaxis()
    plt.xlabel('Fluid Volume Fraction', fontsize=12)
    plt.ylabel('Pressure (bars)', fontsize=12)
    plt.title('Fluid Volume Fraction vs Pressure', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=10)
    plt.tight_layout()
    return fig


# ============================================================
# function to plot SiO2 vs pressure
# ============================================================
def plot_silica_vs_pressure(df_list, run_names):
    run_colors = [
    '#e6194b',
    '#f58231',
    '#ffe119', 
    '#3cb44b',
    '#4363d8',
    '#911eb4',
    '#42d4f4',
    '#f032e6',
    ]
    
    run_styles = [
        (0, (3, 5, 1, 5)), (0, (3, 10, 1, 10)), (0, (3, 10, 1, 10, 1, 10)),
        (0, (5, 1)), (0, (1, 10)), (0, (1, 5)), (0, (5, 5)), (0, (3, 1, 1, 1)),
    ]

    fig = plt.figure(figsize=(8, 6))

    for df, run_name, color, style in zip(df_list, run_names, run_colors, run_styles):
        plt.plot(df['Melt SiO2 wt%'], df['Pressure (bars)'],
                 linewidth=2, color=color, linestyle=style, marker='o',
                 markersize=4, alpha=0.7, label=run_name)

    plt.gca().invert_yaxis()
    plt.xlabel('SiO2 (wt%)', fontsize=12)
    plt.ylabel('Pressure (bars)', fontsize=12)
    plt.title('SiO2 vs Pressure', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=10)
    plt.tight_layout()
    return fig

# ============================================================
# function to plot MgO vs pressure
# ============================================================
def plot_mgo_vs_pressure(df_list, run_names):
    run_colors = [
    '#e6194b',
    '#f58231',
    '#ffe119', 
    '#3cb44b',
    '#4363d8',
    '#911eb4',
    '#42d4f4',
    '#f032e6',
    ]
    run_styles = [
        (0, (3, 5, 1, 5)), (0, (3, 10, 1, 10)), (0, (3, 10, 1, 10, 1, 10)),
        (0, (5, 1)), (0, (1, 10)), (0, (1, 5)), (0, (5, 5)), (0, (3, 1, 1, 1)),
    ]

    fig = plt.figure(figsize=(8, 6))

    for df, run_name, color, style in zip(df_list, run_names, run_colors, run_styles):
        plt.plot(df['Melt MgO wt%'], df['Pressure (bars)'],
                 linewidth=2, color=color, linestyle=style, marker='o',
                 markersize=4, alpha=0.7, label=run_name)

    plt.gca().invert_yaxis()
    plt.xlabel('MgO (wt%)', fontsize=12)
    plt.ylabel('Pressure (bars)', fontsize=12)
    plt.title('MgO vs Pressure', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=10)
    plt.tight_layout()
    return fig

# ============================================================
# function to plot total iron vs pressure
# ============================================================
def plot_iron_vs_pressure(df_list, run_names):
    run_colors = [
    '#e6194b',
    '#f58231',
    '#ffe119', 
    '#3cb44b',
    '#4363d8',
    '#911eb4',
    '#42d4f4',
    '#f032e6',
    ]

    fig = plt.figure(figsize=(8, 6))

    for df, run_name, color, style in zip(df_list, run_names, run_colors, run_styles):
        # Sum FeO and Fe2O3 for total iron
        total_iron = df['Melt FeO wt%'] + df['Melt Fe2O3 wt%']
        plt.plot(total_iron, df['Pressure (bars)'],
                 linewidth=2, color=color, linestyle=style, marker='o',
                 markersize=4, alpha=0.7, label=run_name)

    plt.gca().invert_yaxis()
    plt.xlabel('Total Iron as FeO + Fe2O3 (wt%)', fontsize=12)
    plt.ylabel('Pressure (bars)', fontsize=12)
    plt.title('Total Iron vs Pressure', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=10)
    plt.tight_layout()
    return fig

# ============================================================
# function to plot fluid volume vs pressure
# ============================================================
def plot_fluid_volume_vs_pressure(df_list, run_names):
    run_colors = [
    '#e6194b',
    '#f58231',
    '#ffe119', 
    '#3cb44b',
    '#4363d8',
    '#911eb4',
    '#42d4f4',
    '#f032e6',
    ]
    run_styles = [
        (0, (3, 5, 1, 5)), (0, (3, 10, 1, 10)), (0, (3, 10, 1, 10, 1, 10)),
        (0, (5, 1)), (0, (1, 10)), (0, (1, 5)), (0, (5, 5)), (0, (3, 1, 1, 1)),
    ]

    fig = plt.figure(figsize=(8, 6))

    for df, run_name, color, style in zip(df_list, run_names, run_colors, run_styles):
        df_fluid = df.dropna(subset=['Fluid Volume (cc)'])
        plt.plot(df_fluid['Fluid Volume (cc)'], df_fluid['Pressure (bars)'],
                 linewidth=2, color=color, linestyle=style, marker='o',
                 markersize=4, alpha=0.7, label=run_name)

    plt.gca().invert_yaxis()
    plt.xlabel('Fluid Volume (cc)', fontsize=12)
    plt.ylabel('Pressure (bars)', fontsize=12)
    plt.title('Fluid Volume vs Pressure', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=10)
    plt.tight_layout()
    return fig

# ============================================================
# function to plot system volume vs pressure
# ============================================================
def plot_system_volume_vs_pressure(df_list, run_names):
    run_colors = [
        '#e6194b', '#f58231', '#ffe119', '#3cb44b',
        '#4363d8', '#911eb4', '#42d4f4', '#f032e6',
    ]
    run_styles = [
        (0, (3, 5, 1, 5)), (0, (3, 10, 1, 10)), (0, (3, 10, 1, 10, 1, 10)),
        (0, (5, 1)), (0, (1, 10)), (0, (1, 5)), (0, (5, 5)), (0, (3, 1, 1, 1)),
    ]

    fig = plt.figure(figsize=(8, 6))

    for df, run_name, color, style in zip(df_list, run_names, run_colors, run_styles):
        plt.plot(df['System Volume (cc)'], df['Pressure (bars)'],
                 linewidth=2, color=color, linestyle=style, marker='o',
                 markersize=4, alpha=0.7, label=run_name)

    plt.gca().invert_yaxis()
    plt.xlabel('System Volume (cc)', fontsize=12)
    plt.ylabel('Pressure (bars)', fontsize=12)
    plt.title('System Volume vs Pressure', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=10)
    plt.tight_layout()
    return fig

# ============================================================
# function to plot system density vs pressure
# ============================================================
def plot_density_vs_pressure(df_list, run_names):
    run_colors = [
        '#e6194b', '#f58231', '#ffe119', '#3cb44b',
        '#4363d8', '#911eb4', '#42d4f4', '#f032e6',
    ]
    run_styles = [
        (0, (3, 5, 1, 5)), (0, (3, 10, 1, 10)), (0, (3, 10, 1, 10, 1, 10)),
        (0, (5, 1)), (0, (1, 10)), (0, (1, 5)), (0, (5, 5)), (0, (3, 1, 1, 1)),
    ]

    fig = plt.figure(figsize=(8, 6))

    for df, run_name, color, style in zip(df_list, run_names, run_colors, run_styles):
        plt.plot(df['System Density (gm/cc)'], df['Pressure (bars)'],
                 linewidth=2, color=color, linestyle=style, marker='o',
                 markersize=4, alpha=0.7, label=run_name)

    plt.gca().invert_yaxis()
    plt.xlabel('System Density (gm/cc)', fontsize=12)
    plt.ylabel('Pressure (bars)', fontsize=12)
    plt.title('System Density vs Pressure', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=10)
    plt.tight_layout()
    return fig

# ============================================================
# function to plot system fluid volume fraction and density vs pressure
# ============================================================
def plot_foam_signature(df_list, run_names):
    run_colors = [
        '#e6194b', '#f58231', '#ffe119', '#3cb44b',
        '#4363d8', '#911eb4', '#42d4f4', '#f032e6',
    ]
    run_styles = [
        (0, (3, 5, 1, 5)), (0, (3, 10, 1, 10)), (0, (3, 10, 1, 10, 1, 10)),
        (0, (5, 1)), (0, (1, 10)), (0, (1, 5)), (0, (5, 5)), (0, (3, 1, 1, 1)),
    ]

    fig, axes = plt.subplots(2, 1, figsize=(8, 12), sharey=True)

    for df, run_name, color, style in zip(df_list, run_names, run_colors, run_styles):
        df_fluid = df.dropna(subset=['Fluid Volume Fraction'])
        axes[0].plot(df_fluid['Fluid Volume Fraction'], df_fluid['Pressure (bars)'],
                     linewidth=2, color=color, linestyle=style, marker='o',
                     markersize=4, alpha=0.7, label=run_name)

    axes[0].invert_yaxis()
    axes[0].set_xlabel('Fluid Volume Fraction', fontsize=12)
    axes[0].set_ylabel('Pressure (bars)', fontsize=12)
    axes[0].set_title('Fluid Volume Fraction vs Pressure', fontsize=13, fontweight='bold')
    axes[0].grid(True, alpha=0.3, linestyle='--')
    axes[0].legend(fontsize=9)

    for df, run_name, color, style in zip(df_list, run_names, run_colors, run_styles):
        axes[1].plot(df['System Density (gm/cc)'], df['Pressure (bars)'],
                     linewidth=2, color=color, linestyle=style, marker='o',
                     markersize=4, alpha=0.7, label=run_name)

    axes[1].set_xlabel('System Density (gm/cc)', fontsize=12)
    axes[1].set_ylabel('Pressure (bars)', fontsize=12)
    axes[1].set_title('System Density vs Pressure', fontsize=13, fontweight='bold')
    axes[1].grid(True, alpha=0.3, linestyle='--')
    axes[1].legend(fontsize=9)

    fig.suptitle('Mafic Foam Signature', fontsize=15, fontweight='bold')
    plt.tight_layout()
    return fig
# ============================================================
# function to plot paramter sensitivity matrix
# ============================================================
def plot_sensitivity_heatmap(df_normalized, df_summary):
    fig, ax = plt.subplots(figsize=(12, 6))

    sns.heatmap(
        df_normalized,
        ax=ax,
        cmap='YlOrRd',
        linewidths=0.5,
        linecolor='white',
        cbar_kws={'label': 'Normalized Value', 'shrink': 0.8},
        annot=df_normalized.round(2),
        fmt='g',
        annot_kws={'size': 9}
    )

    ax.set_title('Parameter Sensitivity Matrix', fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.tick_params(axis='x', rotation=30, labelsize=9)
    ax.tick_params(axis='y', rotation=0, labelsize=9)

    plt.tight_layout()
    return fig