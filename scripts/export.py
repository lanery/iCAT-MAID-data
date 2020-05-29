from pathlib import Path
from shutil import copy2

import numpy as np
import pandas as pd
from tqdm import tqdm


def create_DataFrame(project_dir, stacks=None):
    """
    Parameters
    ----------
    project_dir : `Path`
        Filepath to project directory
    stacks : list
        List of stacks to export

    Returns
    -------
    df : pd.DataFrame
        DataFrame of filepaths to tile data
            z | y | x | zoom |   stack1     |   stack2
            ----------------------------------------------
            0 | 0 | 0 |  0   | path/to/file | path/to/file
            0 | 0 | 0 |  0   | path/to/file | path/to/file
            0 | 0 | 0 |  0   | path/to/file | path/to/file
    """
    # Accept all stacks if none provided
    if stacks is None:
        stacks = [d.name for d in project_dir.glob('*') if d.is_dir()]

    # Create container for row data
    rows = []
    # Iterate through image tiles
    for stack_dir in project_dir.glob('*'):
        if stack_dir.name in stacks:
            for fp in stack_dir.glob('*/*_*_*.png'):
                stack = fp.parents[1].name
                z = int(fp.parents[0].name)
                y, x, zoom = [int(i) for i in fp.stem.split('_')]
                rows.append([stack, z, y, x, zoom, fp])

    # Create DataFrame
    columns = ['stack', 'z', 'y', 'x', 'zoom', 'filepath']
    df = pd.DataFrame(rows, columns=columns)\
           .sort_values(['stack', 'z', 'y', 'x', 'zoom'])\
           .pivot_table(index=['z', 'y', 'x', 'zoom'],
                        columns='stack',
                        values='filepath',
                        aggfunc='first')\
           .reset_index()
    return df


def export(export_dir, source, mapping):
    """Export data to 

    Parameters
    ----------
    export_dir : `pathlib.Path`
        Directory to export data to. Ideally,
        .../iCAT-MAID-data/projects/{project}/
    source : `pd.DataFrame`
        DataFrame of filepaths
    mapping : dict
        Mapping from stack name on CATMAID server to stack name within iCAT-MAID-data
    """
    # Create directories
    # .../projects/{project}/{stack}/{z}/
    for stack, z in zip(mapping.values(),
                        source['z'].unique()):
        tgt_dir = export_dir / stack / z
        tgt_dir.mkdir(parents=True, exist_ok=True)

    # Loop through correlative tiles
    for i, row in tqdm(source.iterrows()),
                       total=len(source)):
        # Loop through each stack
        for stack in stack_map.keys():
            tgt = export_dir / stack / str(z)
            tgt/= row[stack].name
            copy2(row[stack].as_posix(),
                  tgt.as_posix())


if __name__ == '__main__':

    # Project name
    # ------------
    project = '20200507_RL012'

    # Project location
    # ----------------
    project_dir = Path('//sonic/long_term_storage/rlane/CATMAID/projects/')
    project_dir /= project

    # Export directory
    # ----------------
    export_dir = Path('M://tnw/ist/do/projects/iCAT/development/iCAT-MAID-data/projects')
    export_dir /= project

    # Stacks to export
    # ----------------
    stack_map = {
        'lil_EM_montaged': 'EM',
        'hoechst_correlated': 'hoechst',
        'insulin_correlated': 'insulin'
    }

    # Compile project DataFrame
    # -------------------------
    df = create_DataFrame(project_dir,
                          stacks=stack_map.keys())

    # Set min/max zoom levels
    # -----------------------
    zoom_min = 2
    zoom_max = 6

    # Filter to min/max zoom levels
    # -----------------------------
    source = df.loc[(df['zoom'] >= zoom_min) &\
                    (df['zoom'] <= zoom_max)].dropna(axis=0)

    # Copy files to export directory
    # ------------------------------
    # .../iCAT-MAID-data/projects/{project}/{stack}/{z}/{row}_{col}_{zoom}.png
    export(df=source,
           mapping=stack_map)
