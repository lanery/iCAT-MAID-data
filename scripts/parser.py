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


# def parse_yaml(filepath):
#     """Parse CATMAID project.yaml file to compile stack data

#     Parameters
#     ----------

#     Returns
#     -------
#     """
#     pass
