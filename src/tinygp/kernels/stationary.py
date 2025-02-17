# -*- coding: utf-8 -*-

from __future__ import annotations

__all__ = [
    "Distance",
    "L1Distance",
    "L2Distance",
    "Stationary",
    "Exp",
    "ExpSquared",
    "Matern32",
    "Matern52",
    "Cosine",
    "ExpSineSquared",
    "RationalQuadratic",
]

from abc import ABCMeta, abstractmethod
from typing import Optional

import jax.numpy as jnp
import numpy as np

from tinygp.helpers import JAXArray, dataclass
from tinygp.kernels import Kernel


class Distance(metaclass=ABCMeta):
    """An abstract base class defining a distance metric interface"""

    @abstractmethod
    def distance(self, X1: JAXArray, X2: JAXArray) -> JAXArray:
        """Compute the distance between two coordinates under this metric"""
        raise NotImplementedError()

    def squared_distance(self, X1: JAXArray, X2: JAXArray) -> JAXArray:
        """Compute the squared distance between two coordinates

        By default this returns the squared result of
        :func:`tinygp.kernels.stationary.Distance.distance`, but some metrics
        can take advantage of these separate implementations to avoid
        unnecessary square roots.
        """
        return jnp.square(self.distance(X1, X2))


@dataclass
class L1Distance(Distance):
    """The L1 or Manhattan distance between two coordinates"""

    def distance(self, X1: JAXArray, X2: JAXArray) -> JAXArray:
        return jnp.sum(jnp.abs(X1 - X2))


@dataclass
class L2Distance(Distance):
    """The L2 or Euclidean distance bettwen two coordaintes"""

    def distance(self, X1: JAXArray, X2: JAXArray) -> JAXArray:
        return jnp.sqrt(self.squared_distance(X1, X2))

    def squared_distance(self, X1: JAXArray, X2: JAXArray) -> JAXArray:
        return jnp.sum(jnp.square(X1 - X2))


@dataclass
class Stationary(Kernel):
    """A stationary kernel is defined with respect to a distance metric

    Note that a stationary kernel is *always* isotropic. If you need more
    non-isotropic length scales, wrap your kernel in a transform using
    :class:`tinygp.transforms.Linear` or :class:`tinygp.transforms.Cholesky`.

    Args:
        scale: The length scale, in the same units as ``distance`` for the
            kernel. This must be a scalar.
        distance: An object that implements ``distance`` and
            ``squared_distance`` methods. Typically a subclass of
            :class:`tinygp.kernels.stationary.Distance`. Each stationary kernel
            also has a ``default_distance`` property that is used when
            ``distance`` isn't provided.
    """

    scale: JAXArray = jnp.ones(())
    distance: Distance = L1Distance()

    def __post_init__(self) -> None:
        if jnp.ndim(self.scale):
            raise ValueError(
                "Only scalar scales are permitted for stationary kernels; use"
                "transforms.Linear or transforms.Cholesky for more flexiblity"
            )


@dataclass
class Exp(Stationary):
    r"""The exponential kernel

    .. math::

        k(\mathbf{x}_i,\,\mathbf{x}_j) = \exp(-r)

    where, by default,

    .. math::

        r = ||(\mathbf{x}_i - \mathbf{x}_j) / \ell||_1

    Args:
        scale: The parameter :math:`\ell`.
    """

    def evaluate(self, X1: JAXArray, X2: JAXArray) -> JAXArray:
        return jnp.exp(-self.distance.distance(X1, X2) / self.scale)


@dataclass
class ExpSquared(Stationary):
    r"""The exponential squared or radial basis function kernel

    .. math::

        k(\mathbf{x}_i,\,\mathbf{x}_j) = \exp(-r^2 / 2)

    where, by default,

    .. math::

        r^2 = ||(\mathbf{x}_i - \mathbf{x}_j) / \ell||_2^2

    Args:
        scale: The parameter :math:`\ell`.
    """

    distance: Distance = L2Distance()

    def evaluate(self, X1: JAXArray, X2: JAXArray) -> JAXArray:
        r2 = self.distance.squared_distance(X1, X2) / jnp.square(self.scale)
        return jnp.exp(-0.5 * r2)


@dataclass
class Matern32(Stationary):
    r"""The Matern-3/2 kernel

    .. math::

        k(\mathbf{x}_i,\,\mathbf{x}_j) = (1 + \sqrt{3}\,r)\,\exp(-\sqrt{3}\,r)

    where, by default,

    .. math::

        r = ||(\mathbf{x}_i - \mathbf{x}_j) / \ell||_1

    Args:
        scale: The parameter :math:`\ell`.
    """

    def evaluate(self, X1: JAXArray, X2: JAXArray) -> JAXArray:
        r = self.distance.distance(X1, X2) / self.scale
        arg = np.sqrt(3) * r
        return (1 + arg) * jnp.exp(-arg)


@dataclass
class Matern52(Stationary):
    r"""The Matern-5/2 kernel

    .. math::

        k(\mathbf{x}_i,\,\mathbf{x}_j) = (1 + \sqrt{5}\,r +
            5\,r^2/\sqrt{3})\,\exp(-\sqrt{5}\,r)

    where, by default,

    .. math::

        r = ||(\mathbf{x}_i - \mathbf{x}_j) / \ell||_1

    Args:
        scale: The parameter :math:`\ell`.
    """

    def evaluate(self, X1: JAXArray, X2: JAXArray) -> JAXArray:
        r = self.distance.distance(X1, X2) / self.scale
        arg = np.sqrt(5) * r
        return (1 + arg + jnp.square(arg) / 3) * jnp.exp(-arg)


@dataclass
class Cosine(Stationary):
    r"""The cosine kernel

    .. math::

        k(\mathbf{x}_i,\,\mathbf{x}_j) = \cos(2\,\pi\,r)

    where, by default,

    .. math::

        r = ||(\mathbf{x}_i - \mathbf{x}_j) / P||_1

    Args:
        scale: The parameter :math:`P`.
    """

    def evaluate(self, X1: JAXArray, X2: JAXArray) -> JAXArray:
        r = self.distance.distance(X1, X2) / self.scale
        return jnp.cos(2 * jnp.pi * r)


@dataclass
class ExpSineSquared(Stationary):
    r"""The exponential sine squared or quasiperiodic kernel

    .. math::

        k(\mathbf{x}_i,\,\mathbf{x}_j) = \exp(-\Gamma\,\sin^2 \pi r)

    where, by default,

    .. math::

        r = ||(\mathbf{x}_i - \mathbf{x}_j) / P||_1

    Args:
        scale: The parameter :math:`P`.
        gamma: The parameter :math:`\Gamma`.
    """

    gamma: Optional[JAXArray] = None

    def __post_init__(self) -> None:
        if self.gamma is None:
            raise ValueError("Missing required argument 'gamma'")

    def evaluate(self, X1: JAXArray, X2: JAXArray) -> JAXArray:
        assert self.gamma is not None
        r = self.distance.distance(X1, X2) / self.scale
        return jnp.exp(-self.gamma * jnp.square(jnp.sin(jnp.pi * r)))


@dataclass
class RationalQuadratic(Stationary):
    r"""The rational quadratic

    .. math::

        k(\mathbf{x}_i,\,\mathbf{x}_j) = (1 + r^2 / 2\,\alpha)^{-\alpha}

    where, by default,

    .. math::

        r^2 = ||(\mathbf{x}_i - \mathbf{x}_j) / \ell||_2^2

    Args:
        scale: The parameter :math:`\ell`.
        alpha: The parameter :math:`\alpha`.
    """

    alpha: Optional[JAXArray] = None

    def __post_init__(self) -> None:
        if self.alpha is None:
            raise ValueError("Missing required argument 'alpha'")

    def evaluate(self, X1: JAXArray, X2: JAXArray) -> JAXArray:
        assert self.alpha is not None
        r2 = self.distance.squared_distance(X1, X2) / jnp.square(self.scale)
        return (1.0 + 0.5 * r2 / self.alpha) ** -self.alpha
