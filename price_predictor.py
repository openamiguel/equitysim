## Code tries to predict the price of a given asset based on prior dataframe
## Author: Eric Frankel
## Version: 1.0

import numpy as np
import pandas as pdb

class Past_Sampler():
    '''Gets training samples for predicting future data from past data'''

    def __init__(self, N, K, sliding_window = True):
        '''
        Predict K future samples using N previous samples
        '''
        self.K = K
        self.N = N
        self.sliding_window = sliding_window

    def transform(self, A):
        M = self.N + self.K # Number of samples per prelim_download
        #indexes
        if self.sliding_window:
            I = np.arange(M) + np.arange(A.shape[0] - M + 1).reshape(-1,1)
        else:
            if A.shape[0]%M == 0:
                I = np.arange(M)+np.arange(0,A.shape[0],M).reshape(-1,1)
            else:
                I = np.arange(M)+np.arange(0,A.shape[0]-M,M).reshape(-1,1)

        B = A[I].reshape(-1)
