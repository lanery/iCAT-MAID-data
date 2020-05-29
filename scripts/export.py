from pathlib import Path
from shutil import copy2
from itertools import product

from tqdm import tqdm
import numpy as np
import pandas as pd


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
        if (stack_dir.name in stacks) and (stack_dir.is_dir()):
            for fp in stack_dir.glob('[0-9]/*_*_*.png'):
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
    for tgt_stack, z in product(mapping.values(),
                                source['z'].unique()):
        tgt_dir = export_dir / tgt_stack / str(z)
        tgt_dir.mkdir(parents=True, exist_ok=True)

    # Loop through correlative tiles
    for i, row in tqdm(source.iterrows(),
                       total=len(source)):
        # Loop through each stack
        for src_stack, tgt_stack in mapping.items():
            tgt = export_dir / tgt_stack / str(z)
            if not pd.isna(row[src_stack]):
                copy2(row[src_stack].as_posix(),
                    tgt.as_posix())


if __name__ == '__main__':

    # Project name
    # ------------
    project = '20200429_RL011'

    # Project location
    # ----------------
    project_dir = Path('//sonic/long_term_storage/rlane/CATMAID/projects/')
    project_dir/= project

    # Export directory
    # ----------------
    export_dir = Path('M://tnw/ist/do/projects/iCAT/development/iCAT-MAID-data/projects')
    export_dir/= project

    # Stacks to export
    # ----------------
    stack_map = {
        'lil_EM_montaged': 'EM',
        'hoechst_correlated': 'hoechst',
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
                    (df['zoom'] <= zoom_max)]

    # Copy files to export directory
    # ------------------------------
    # .../iCAT-MAID-data/projects/{project}/{stack}/{z}/{row}_{col}_{zoom}.png
    export(export_dir=export_dir,
           source=source,
           mapping=stack_map)
