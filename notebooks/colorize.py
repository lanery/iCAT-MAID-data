import numpy as np
from skimage import (img_as_ubyte, img_as_float,
                     io, color, util, exposure)


def transform(fp, T):
    """Colorize image

    Parameters
    ----------
    fp : `Path`
        Filepath to image

    Returns
    -------
    rescaled : rgba float array
        Image array after color transformation
    """
    # Read image as float
    image = img_as_float(io.imread(fp.as_posix()))
    # Convert to rgba
    rgba = color.grey2rgb(image, alpha=True)
    # Apply transform
    transformed = np.dot(rgba, T)
    rescaled = exposure.rescale_intensity(transformed)
    return rescaled


def trevni(fp):
    """Invert contrast

    Parameters
    ----------
    fp : `Path`
        Filepath to image

    Returns
    -------
    rgba : rgba float array
        Image array after contrast inversion
    """
    # Read image as float
    image = img_as_float(io.imread(fp.as_posix()))
    # Invert contrast
    inverted = util.invert(image)
    # Convert to rgba
    rgba = color.grey2rgb(inverted, alpha=True)
    return rgba
