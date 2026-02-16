"""
angle_utils.py
==============
Utility function for computing the angle formed by three points
using NumPy.
"""

import numpy as np


def calculate_angle(
    a: list | tuple | np.ndarray,
    b: list | tuple | np.ndarray,
    c: list | tuple | np.ndarray,
) -> float:
    """
    Calculate the angle ∠ABC in **degrees**, where B is the vertex.

    Parameters
    ----------
    a, b, c : array-like of shape (2,) or (3,)
        Coordinates of the three points.
        Example: ``[x, y]`` or ``[x, y, z]``.

    Returns
    -------
    float
        Angle in degrees, range 0–180.
    """
    a = np.array(a, dtype=np.float64)
    b = np.array(b, dtype=np.float64)
    c = np.array(c, dtype=np.float64)

    ba = a - b  # vector B → A
    bc = c - b  # vector B → C

    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
    cosine = np.clip(cosine, -1.0, 1.0)

    angle = np.degrees(np.arccos(cosine))
    return float(angle)
