import xarray as xr
import warnings
from properscoring import crps_ensemble, crps_gaussian, crps_quadrature, threshold_brier_score


def xr_crps_gaussian(observations, mu, sig):
    """
    xarray version of properscoring.crps_gaussian.

    Parameters
    ----------
    observations : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or
     scalars, Mix of labeled and/or unlabeled observations arrays.
    mu : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or
     scalars, Mix of labeled and/or unlabeled forecasts mean arrays.
    sig : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or
     scalars, Mix of labeled and/or unlabeled forecasts mean arrays.

    Returns
    -------
    Single value or tuple of Dataset, DataArray, Variable, dask.array.Array or
     numpy.ndarray, the first type on that list to appear on an input.

    See Also
    --------
    properscoring.crps_gaussian
    xarray.apply_ufunc
    """
    # check if same dimensions
    if isinstance(mu, (int, float)):
        mu = xr.DataArray(mu)
    if isinstance(sig, (int, float)):
        sig = xr.DataArray(sig)
    if mu.dims != observations.dims:
        observations, mu = xr.broadcast(observations, mu)
    if sig.dims != observations.dims:
        observations, sig = xr.broadcast(observations, sig)
    return xr.apply_ufunc(crps_gaussian,
                          observations,
                          mu,
                          sig,
                          input_core_dims=[[], [], []],
                          dask='parallelized',
                          output_dtypes=[float])


def xr_crps_quadrature(x, cdf_or_dist, xmin=None, xmax=None, tol=1e-6):
    """
    xarray version of properscoring.crps_quadrature.

    Parameters
    ----------
    x : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or
     scalars, Mix of labeled and/or unlabeled x arrays.


    Returns
    -------
    Single value or tuple of Dataset, DataArray, Variable, dask.array.Array or
     numpy.ndarray, the first type on that list to appear on an input.

    See Also
    --------
    properscoring.crps_quadratic
    xarray.apply_ufunc
    """
    # check if same dimensions
    if isinstance(xmin, (int, float)):
        xmin = xr.DataArray(xmin)
    if isinstance(xmax, (int, float)):
        xmax = xr.DataArray(xmax)
    if isinstance(tol, (int, float)):
        tol = xr.DataArray(tol)
    if xmin.dims != x.dims:
        x, xmin = xr.broadcast(x, xmin)
    if xmax.dims != x.dims:
        x, xmax = xr.broadcast(x, xmax)
    if tol.dims != x.dims:
        x, tol = xr.broadcast(x, tol)
    return xr.apply_ufunc(crps_quadrature,
                          x,
                          cdf_or_dist,
                          xmin,
                          xmax,
                          tol,
                          input_core_dims=[[], [], [], [], []],
                          dask='parallelized',
                          output_dtypes=[float])


def xr_crps_ensemble(observations, forecasts, weights=None, issorted=False,
                     axis=-1, dim='member'):
    """
    xarray version of properscoring.crps_ensemble.

    Parameters
    ----------
    observations : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or
     scalars, Mix of labeled and/or unlabeled observations arrays.
    forecasts : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or
     scalars, Mix of labeled and/or unlabeled forecasts arrays with required
     member dimension `dim`.
    weights : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or
     scalars, Mix of labeled and/or unlabeled, optional
     If provided, the CRPS is calculated exactly with the assigned
     probability weights to each forecast. Weights should be positive, but
     do not need to be normalized. By default, each forecast is weighted
     equally.
    issorted : bool, optional
     Optimization flag to indicate that the elements of `ensemble` are
     already sorted along `axis`.
    axis : int, optional
     Axis in forecasts and weights which corresponds to different ensemble
     members, along which to calculate CRPS.
    dim : str, optional
     Name of ensemble member dimension. By default, 'member'.

    Returns
    -------
    Single value or tuple of Dataset, DataArray, Variable, dask.array.Array or
    numpy.ndarray, the first type on that list to appear on an input.

    See Also
    --------
    properscoring.crps_ensemble
    xarray.apply_ufunc
    """
    return xr.apply_ufunc(crps_ensemble,
                          observations,
                          forecasts,
                          input_core_dims=[[], [dim]],
                          kwargs={
                              'axis': axis,
                              'issorted': issorted,
                              'weights': weights
                          },
                          dask='parallelized',
                          output_dtypes=[float]
                          )


def xr_brier_score(observations,
                   forecasts
                   ):
    """
    xarray version of properscoring.brier_score: Calculate Brier score (BS).
    ..math:
        BS(p, k) = (p_1 - k)^2,
    Parameters
    ----------
    observations : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or
     scalars, Mix of labeled and/or unlabeled observations arrays.
    forecasts : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or
     scalars, Mix of labeled and/or unlabeled forecasts arrays.
    Returns
    -------
    Single value or tuple of Dataset, DataArray, Variable, dask.array.Array or
    numpy.ndarray, the first type on that list to appear on an input.
    References
    ----------
    Gneiting, Tilmann, and Adrian E Raftery. “Strictly Proper Scoring Rules,
      Prediction, and Estimation.” Journal of the American Statistical
      Association 102, no. 477 (March 1, 2007): 359–78.
      https://doi.org/10/c6758w.
    See Also
    --------
    properscoring.brier_score
    xarray.apply_ufunc
    """
    return xr.apply_ufunc(brier_score,
                          observations,
                          forecasts,
                          input_core_dims=[[], []],
                          dask='parallelized',
                          output_dtypes=[float])


def xr_threshold_brier_score(observations,
                             forecasts,
                             threshold,
                             issorted=False,
                             axis=-1,
                             dim='member'):
    """
    xarray version of properscoring.threshold_brier_score: Calculate the Brier
     scores of an ensemble for exceeding given thresholds.

    Parameters
    ----------
    observations : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or
     scalars, Mix of labeled and/or unlabeled observations arrays.
    forecasts : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or
     scalars, Mix of labeled and/or unlabeled forecasts arrays with required
     member dimension `dim`.
    threshold : scalar (not yet implemented: or 1d scalar threshold value(s) at
     which to calculate) exceedence Brier scores.
    issorted : bool, optional
        Optimization flag to indicate that the elements of `ensemble` are
        already sorted along `axis`.
    axis : int, optional
        Axis in forecasts which corresponds to different ensemble members,
        along which to calculate the threshold decomposition.
    dim : str, optional
     Name of ensemble member dimension. By default, 'member'.


    Returns
    -------
    Single value or tuple of Dataset, DataArray, Variable, dask.array.Array or
    numpy.ndarray, the first type on that list to appear on an input. (If
    ``threshold`` is a scalar, the result will have the same shape as
    observations. Otherwise, it will have an additional final dimension
    corresponding to the threshold levels. Not implemented yet.)

    References
    ----------
    Gneiting, T. and Ranjan, R. Comparing density forecasts using threshold-
       and quantile-weighted scoring rules. J. Bus. Econ. Stat. 29, 411-422
       (2011). http://www.stat.washington.edu/research/reports/2008/tr533.pdf

    See Also
    --------
    properscoring.threshold_brier_score
    xarray.apply_ufunc
    """
    return xr.apply_ufunc(threshold_brier_score,
                          observations,
                          forecasts,
                          threshold,
                          input_core_dims=[[], [dim], []],
                          kwargs={
                              'axis': axis,
                              'issorted': issorted
                          },
                          dask='parallelized',
                          output_dtypes=[float])
