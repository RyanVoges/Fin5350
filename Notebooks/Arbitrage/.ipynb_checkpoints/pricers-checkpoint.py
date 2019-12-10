import numpy as np
from scipy.stats import binom, norm
from collections import namedtuple

PricerResult = namedtuple("PricerResult", ['price', 'stderr'])

def european_binomial(option, spot, rate, vol, div, steps):
    strike = option.strike
    expiry = option.expiry
    call_t = 0.0
    spot_t = 0.0
    h = expiry / steps
    num_nodes = steps + 1
    u = np.exp((rate - div) * h + vol * np.sqrt(h))
    d = np.exp((rate - div) * h - vol * np.sqrt(h))
    pstar = (np.exp(rate * h) - d) / ( u - d)
    
    for i in range(num_nodes):
        spot_t = spot * (u ** (steps - i)) * (d ** (i))
        call_t += option.payoff(spot_t) * binom.pmf(steps - i, steps, pstar)

    call_t *= np.exp(-rate * expiry)
    
    return call_t

def american_binomial(option, spot, rate, vol, div, steps):
    strike = option.strike
    expiry = option.expiry
    call_t = 0.0
    spot_t = 0.0
    h = expiry / steps
    num_nodes = steps + 1
    u = np.exp((rate - div) * h + vol * np.sqrt(h))
    d = np.exp((rate - div) * h - vol * np.sqrt(h))
    pstar = (np.exp(rate * h) - d) / ( u - d)
    disc = np.exp(-rate * h) 
    spot_t = np.zeros(num_nodes)
    prc_t = np.zeros(num_nodes)
    
    for i in range(num_nodes):
        spot_t[i] = spot * (u ** (steps - i)) * (d ** (i))
        prc_t[i] = option.payoff(spot_t[i])


    for i in range((steps - 1), -1, -1):
        for j in range(i+1):
            prc_t[j] = disc * (pstar * prc_t[j] + (1 - pstar) * prc_t[j+1])
            spot_t[j] = spot_t[j] / u
            prc_t[j] = np.maximum(prc_t[j], option.payoff(spot_t[j]))
                    
    return prc_t[0]

def naive_monte_carlo_pricer(option, spot, rate, vol, div, reps):
    strike = option.strike
    expiry = option.expiry
    dt = expiry
    nudt = (rate - div - 0.5 * vol * vol) * dt
    sigdt = vol * np.sqrt(dt)
    
    z = np.random.normal(size=reps)
    paths = spot * np.exp(nudt + sigdt  * z)
    payoffs = np.exp(-rate * dt) * option.payoff(paths) 
    prc = np.mean(payoffs)
    se = np.std(payoffs, ddof=1) / np.sqrt(reps)
    
    return PricerResult(prc, se)

def stratified_normals(M):
    u = np.random.uniform(size=M)
    i = np.arange(M)
    uhat = (u + i) / M
    return norm.ppf(uhat)

def stratified_monte_carlo_pricer(option, spot, rate, vol, div, reps):
    strike = option.strike
    expiry = option.expiry
    dt = expiry
    nudt = (rate - div - 0.5 * vol * vol) * dt
    sigdt = vol * np.sqrt(dt)
    
    z = stratified_normals(reps)
    paths = spot * np.exp(nudt + sigdt  * z)
    payoffs = np.exp(-rate * dt) * option.payoff(paths) 
    prc = np.mean(payoffs)
    se = np.std(payoffs, ddof=1) / np.sqrt(reps)
    
    return PricerResult(prc, se)


if __name__ == "__main__":
    print("This is a module. Not intended to be run standalone.")
