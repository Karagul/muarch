import functools
from abc import ABC
from typing import Optional

import numpy as np


def _format_simulator(_simulate):
    """Formats input and output of the _simulator method"""

    @functools.wraps(_simulate)
    def decorator(self, size: int, reps: Optional[int] = None):
        if reps is not None:
            if not isinstance(reps, int) or reps <= 0:
                raise ValueError('`reps` must be an integer greater than 0')

        value = _simulate(self, size, reps)

        if isinstance(value, (int, float)):
            value = np.array([value], value)
        return np.asarray(value)

    return decorator


class DistributionMixin(ABC):
    def __init__(self):
        self._custom_dist: np.ndarray = None

    def check_dist_size(self, size):
        """Checks that the size required for the simulation is within the generated custom dist bounds"""
        if self.custom_dist is None:
            raise ValueError(f'method should not be called when custom_dist is not specified')

        if len(self.custom_dist) < size:
            times = round(np.ceil(size / len(self.custom_dist) * 100) / 100, 2)
            raise ValueError(f'rvs array too short. Increase the number of uniform rvs generated by {times}x')

    @property
    def custom_dist(self) -> Optional[np.ndarray]:
        """
        Optional density with fitted object from which to simulate

        The custom.dist option allows for defining a custom density which exists in the users workspace with methods for “r” (sampling, e.g. rnorm) and “d” (density e.g. dnorm). It must take a single fit object as its second argument. Alternatively, custom.dist can take any name in the name slot (e.g.“sample”) and a matrix in the fit slot with dimensions equal to m.sim (columns) and n.sim (rows). It is understood that what is supplied are the standardized (0,1) innovations and not the unstandardized residuals. The usefulness of this becomes apparent when one is considering the copula-GARCH approach or the bootstrap method.

        Returns
        -------
        {ndarray, None}
            Array of density values or None
        """
        return self._custom_dist

    @custom_dist.setter
    def custom_dist(self, values: Optional[np.ndarray]):
        if values is None:
            self._custom_dist = None
        else:
            values = np.asarray(values)
            self._custom_dist = float(values) if values.size == 1 else values
