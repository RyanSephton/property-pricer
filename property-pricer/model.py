from sklearn.neighbors import KernelDensity # non-parametric
from sklearn.model_selection import GridSearchCV
from sklearn.base import BaseEstimator
from scipy import integrate
from typing import Tuple
import numpy as np
import warnings

def get_optimal_kde(
    price_data : np.ndarray, 
    bandwidth_search_space : np.ndarray = None,
    cross_validation_folds : int = 5
) -> BaseEstimator:
    """
    Computes the optimal KDE model for a given set of normalized 
    1D data.
    
    Parameters
    ----------
    price_data : np.array
        Contains the min-max normalized price data to be interpolated
    
    Returns
    -------
    opt_model : BaseEstimator
        The optimal kernel density estimator model for interpolating
        the PDF.
    """
    if not isinstance(bandwidth_search_space, np.ndarray):
        bandwidth_search_space = np.exp(np.linspace(-5,2,30))
    
    # Grid search for optimal bandwidth
    grid = GridSearchCV(
        KernelDensity(kernel='gaussian'), 
        {'bandwidth': bandwidth_search_space}, 
        cv=cross_validation_folds
    ) 
    grid.fit(price_data.reshape(-1,1))
    
    # Obtain optimal model
    opt_model = grid.best_estimator_
    
    return opt_model


def calculate_critical_value(
    optimal_kde : BaseEstimator, 
    threshold: float =0.05, 
    n_samples : int = 1000
) -> Tuple[float, float]:
    """
    Computes the critical values from a KDE estimate of 
    an unobserved pdf (2 sided).
    
    Parameters
    ----------
    optimal_kde : BaseEstimator
        The optimal kernel density estimator model for interpolating
        the PDF.
    threshold : float
        Specifies the critical value threshold to determine,
        NOTE: both the threshold and 1-threshold are determined
    n_samples : int
        The number of samples to take in the x direction (this
        is the sames as the discretization of the integration).
    
    Returns
    -------
    lower_bound : float
        The lower bounded critical value of the pdf (normalised).
    lower_bound : float
        The upper bounded critical value of the pdf (normalised).
    threshold : float
        The true threshold used in the calculation (will be different
        from input if numerical precision is exceeded).
    """
    # sample pdf at linear intervals along x axis
    x_pdf_sample = np.linspace(0,1,num = n_samples)
    
    # Invert log likelihood to get probability estimate
    prob_densities = np.exp(
        optimal_kde.score_samples(x_pdf_sample[:,np.newaxis])
    )


    def find_nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return idx
    
    # Store discretised CDF to find critical values 
    pdf = []
    
    # This is not efficient, but good enough for now
    for i in range(1,len(prob_densities)):
        pdf.append(
            integrate.simpson(
                prob_densities[:i], 
                dx=1 / (len(prob_densities)-1)
            )
        )
    
    if threshold < (1-pdf[-1]):
        warnings.warn(
            f'Threshold exceeds integration precision, setting to maximum ({pdf[-1]})'
        )
        threshold = 1-pdf[-1]
    
    lower_bound_idx, upper_bound_idx = (
        find_nearest(pdf,threshold), 
        find_nearest(pdf, 1- threshold)
    )
    lower_bound, upper_bound = (
        x_pdf_sample[lower_bound_idx], 
        x_pdf_sample[upper_bound_idx]
    )
    
    return lower_bound, upper_bound, threshold