import copy
import numpy as np
import scipy.stats as stats
from tqdm import tqdm
from property_pricer import get_optimal_kde, calculate_critical_value
from typing import Tuple

def get_price_range(
    prices : np.ndarray, threshold : float = 0.05, 
    n_bootstraps : int = 10, bootstrap_fraction : float = 0.8
) -> Tuple[np.ndarray, np.ndarray, float, float]:
    """
    Calculate the price range for a given two-sided confidence interval
    using a kernel density estimator, based on a given threshold and 
    calculate the uncertainty in the interval using bootstrap sampling.
    
    Parameters
    ----------
    prices : np.ndarray
        Observed prices from the unknown price probability distribution
    threshold : float
        two sided confidence interval i.e. 0.05 corresponds to the 90%
        confidence interval.
    n_bootstraps : int
        The number of bootstrap sampling rounds to run for the estimates
    bootstrap_fraction : float
        Proportion of samples to be included in each bootstrap run
    
    Returns
    -------
    lower_bound_estimate : int
        The lower bound price in the confidence interval
    upper_bound_estimate : int
        The upper bound price in the confidence interval
    lower_bound_uncertainty : int
        The uncertainty in the lower bound estimate
    upper_bound_uncertainty : int
        The uncertainty in the upper bound estimate
    threshold : float
        The true threshold used in the calculation (will be different
        from input if numerical precision is exceeded).
    """
    lower_bound_estimates = []
    upper_bound_estimates = []
    
    # Run the bootstrap resamples
    for _ in tqdm(range(n_bootstraps)):
        
        # randomly select a subset of the prices
        price_sample = np.random.choice(
            prices,
            size = int(len(prices)*bootstrap_fraction)
        )
        
        # Normalise prices to [0,1] range
        price_sample_normalised, sample_min, sample_max =(
            min_max_normalize(price_sample)
        )
        
        # Fit optimal kernel density estimator to prices
        optimal_kde = get_optimal_kde(
            price_sample_normalised
        )

        # Estimate normalised upper and lower bounds
        lb_normalised, ub_normalised, threshold = (
            calculate_critical_value(
                optimal_kde, threshold=threshold
            )
        )
        
        # Undo normalisation on estimates 
        lb, ub = (
            unnormalize(lb_normalised,sample_max, sample_min),
            unnormalize(ub_normalised,sample_max, sample_min)
        )

        lower_bound_estimates.append(lb)
        upper_bound_estimates.append(ub)

    lower_bound_estimates = np.array(lower_bound_estimates)
    upper_bound_estimates = np.array(upper_bound_estimates)
    
    # Compute uncertainty in threshold estimates
    lower_bound_uncertainty = int(calculate_uncertainty(lower_bound_estimates))
    upper_bound_uncertainty = int(calculate_uncertainty(upper_bound_estimates))
    
    # Compute average estimate in the mean bound price
    lower_bound_estimate = int(np.mean(lower_bound_estimates))
    upper_bound_estimate = int(np.mean(upper_bound_estimates))
    
    return (
        lower_bound_estimate, upper_bound_estimate, 
        lower_bound_uncertainty, upper_bound_uncertainty, threshold
    )



def upsample_data(
    neighbours_to_visit : set, samples : list, price_type : str, 
    property_type : str, data : dict, needed_samples : int, 
    visited_neighbours : set
)-> list:
    """
    Recursively upsample data by including neighbouring 
    postcode data, until statistical significance is reached.
    
    Parameters
    ----------
    neighbours_to_visit : set
        The queue of neighbouring postcodes to visit next
        in the recursion
    samples : list
        The property sale price samples currently in the path
    price_type : str
        Whether to use 'adjusted' or 'unadjusted' prices for
        the samples.
    property_type : str
        The property type to be used in the sample collection
    data : dict
        The full property sales data json
    needed_samples : int
        The lower bound on the number of samples needed for statistical
        significance.
    visited_neighbours : set
        The neighbouring postcodes that have already been included in the 
        upsampling random walk
    
    Returns
    -------
    samples : list
        The list of upregulated samples (or None if no possible upsampling
        walk could be found).
    """
    if len(neighbours_to_visit) == 0:
        print('No possible path of neighbours with sufficient data could be found')
        return None
    
    neighbour = neighbours_to_visit.pop()
    visited_neighbours.add(neighbour)
    
    print(f'Adding in samples from postcode: {neighbour}')
    neighbour_data = data[neighbour]
    neighbours_to_visit.union(set(neighbour_data['Neighbours']))
    
    samples = samples + neighbour_data[property_type][price_type]
                               
    if len(samples) < needed_samples:
        upsample_data(
            neighbours_to_visit, samples, 
            price_type, property_type, data, needed_samples, visited_neighbours
        )
    return samples







def calculate_property_prices(data, postcode, pricing_type, property_type, confidence):
    
    # Convert confidence to 2-sided threshold value
    threshold = (1-confidence)/2
    
    # heuristic based on having a quarter
    # of a standard deviation of error in an unobserved 
    # normal distribution at a given threshold
    needed_samples = int(np.ceil(16 * 4 * (stats.norm.ppf(1 - threshold)**2)))
    
    # Obtain samples we currently have for postcode
    postcode_data =  data[postcode]
    samples = postcode_data[property_type][pricing_type]
    
    if len(samples) < needed_samples:
        samples = upsample_data(
            set(postcode_data['Neighbours']), samples, 
            pricing_type, property_type, copy.deepcopy(data), 
            needed_samples, set()
        )
    
    if not samples:
        print(
            'Could not obtain a sufficient number' 
            ' of samples - returning no estimate'
        )
        return None
    
    lb_estimate, ub_estimate, lb_uncertainty, ub_uncertainty, threshold = (
        get_price_range(
            np.array(samples),
            threshold
        )
    )
    return lb_estimate, ub_estimate, lb_uncertainty, ub_uncertainty, threshold










def calculate_uncertainty(estimates):
    return (estimates.max() - estimates.min()) / 2

def min_max_normalize(vals):
    vmax = vals.max()
    vmin = vals.min()
    vals_normalised = (vals - vmin) / (vmax-vmin)
    
    return vals_normalised, vmin, vmax

def unnormalize(val_normalized, vmax, vmin):
    val = (val_normalized * (vmax - vmin)) + vmin
    return val