import pandas as pd
import matplotlib.pyplot as plt

def load_run_data(run_name):
    path = f'./Lassen_{run_name}.XLSX'

    df_eruptions = pd.read_excel(path, sheet_name='Eruptions Open', skiprows=[1, 2])

    df_summary = pd.read_excel(path, sheet_name='RunSummary')

    return df_eruptions, df_summary

def clean_settp_duplicates(df):
    if df.index.name:
        mask = ~(df.index.astype(str).str.contains('SetTP', na=False))
        mask.iloc[0] = True
        df_cleaned = df[mask]
    else:
        first_col = df.columns[0]
        mask = ~(df[first_col].astype(str).str.contains('SetTP', na=False))
        mask.iloc[0] = True
        df_cleaned = df[mask]

    return df_cleaned

def plot_all_oxides_vs_pressure(df_list, run_names, ncols=4):
    oxides = [
        'Melt SiO2 wt%', 'Melt TiO2 wt%', 'Melt Al2O3 wt%',
        'Melt Fe2O3 wt%', 'Melt Cr2O3 wt%', 'Melt FeO wt%',
        'Melt MnO wt%', 'Melt MgO wt%', 'Melt NiO wt%',
        'Melt CoO wt%', 'Melt CaO wt%', 'Melt Na2O wt%',
        'Melt K2O wt%', 'Melt P2O5 wt%', 'Melt H2O wt%',
        'Melt CO2 wt%'
    ]

    run_colors = ['darkred', 'darkblue', 'darkgreen', 'purple', 'orange',
                  'brown', 'crimson', 'navy', 'teal', 'magenta']

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
        oxide_name = oxide.replace('Melt ', '').replace(' wt%', '')
        axes[i].set_xlabel(f'{oxide_name} (wt%)', fontsize=11)
        axes[i].set_ylabel('Pressure (bars)', fontsize=11)
        axes[i].set_title(oxide_name, fontsize=12, fontweight='bold')
        axes[i].grid(True, alpha=0.3, linestyle='--')
        axes[i].legend(fontsize=8, loc='best')

    for i in range(len(oxides), len(axes)):
        axes[i].axis('off')

    fig.suptitle('Oxide Evolution', fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.show()

def plot_temperature_vs_pressure(df_list, run_names):
    run_colors = ['darkred', 'darkblue', 'darkgreen', 'purple', 'orange',
                  'brown', 'crimson', 'navy', 'teal', 'magenta']

    plt.figure(figsize=(8, 6))

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
    plt.show()

def plot_fluid_mass(df_list, run_names):

    run_colors = ['darkred', 'darkblue', 'darkgreen', 'purple', 'orange',
                  'brown', 'crimson', 'navy', 'teal', 'magenta']

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for df, run_name, color in zip(df_list, run_names, run_colors):
        axes[0].plot(df['Temperature (deg C)'], df['fluid Mass (m.u.)'],
                     linewidth=2, color=color, marker='o', markersize=4,
                     alpha=0.7, label=run_name)

    axes[0].set_xlabel('Temperature (°C)', fontsize=12)
    axes[0].set_ylabel('Fluid Mass (m.u.)', fontsize=12)
    axes[0].set_title('Fluid Mass vs Temperature', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3, linestyle='--')
    axes[0].legend(fontsize=10)

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
    plt.show()
