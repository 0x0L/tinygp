.. _api-ref:

API
===

Computation engine
------------------

.. autoclass:: tinygp.GaussianProcess
   :members:


.. _api-kernels:

Kernels
-------

.. autoclass:: tinygp.kernels.Kernel
   :members:

.. autoclass:: tinygp.kernels.Custom
.. autoclass:: tinygp.kernels.Constant
.. autoclass:: tinygp.kernels.DotProduct
.. autoclass:: tinygp.kernels.Polynomial


.. _api-stationary:

Stationary Kernels
------------------

Stationary kernels are defined with a distance metric implementing the
:class:`tinygp.kernels.stationary.Distance` interface.

.. autoclass:: tinygp.kernels.Stationary
.. autoclass:: tinygp.kernels.Exp
.. autoclass:: tinygp.kernels.ExpSquared
.. autoclass:: tinygp.kernels.Matern32
.. autoclass:: tinygp.kernels.Matern52
.. autoclass:: tinygp.kernels.Cosine
.. autoclass:: tinygp.kernels.ExpSineSquared
.. autoclass:: tinygp.kernels.RationalQuadratic


.. _api-distance:

Distance Metrics
----------------

.. autoclass:: tinygp.kernels.stationary.Distance
   :members:

.. autoclass:: tinygp.kernels.stationary.L1Distance
.. autoclass:: tinygp.kernels.stationary.L2Distance


.. _api-transforms:

Transforms
----------

In ``tinygp``, a "transform" is any callable that takes an input coordinate and
returns a transformed coordinate. There are some built in implementations for
standard linear transformations that can be used to handle multivariate vector
inputs.

.. autoclass:: tinygp.transforms.Transform
.. autoclass:: tinygp.transforms.Linear
.. autoclass:: tinygp.transforms.Cholesky
   :members:
.. autoclass:: tinygp.transforms.Subspace
