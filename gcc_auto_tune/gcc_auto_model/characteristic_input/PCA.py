#
# file: PCA.py
# function: convert perf result vector to n-dimensional vector 
#


import numpy as np
from sklearn.decomposition import PCA
from perf_result import result_handler


class pca_model():

    def __init__(self) -> None:
        self.n = None
        self.pca = PCA()

    def select_dimension(self, x) -> None:
        x = np.atleast_2d(x).reshape((1, -1))
        print(x)
        self.pca.fit(x)
        cumulative_variance_ratio = np.cumsum(self.pca.explained_variance_ratio_)
        self.n = np.argmax(cumulative_variance_ratio >= 0.95) + 1
        print(self.n)


if __name__ == "__main__":
    handler = result_handler()
    raw_vec = handler.get_vector()
    model = pca_model()
    model.select_dimension(raw_vec)
