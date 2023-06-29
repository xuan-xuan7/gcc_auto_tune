#
# file: PCA.py
# function: convert perf result vector to n-dimensional vector 
#


import numpy as np
from sklearn.decomposition import PCA
from result_handle import result_handler


class pca_model():

    def __init__(self) -> None:
        self.n = None
        self.pca = PCA()

    def select_dimension(self, x) -> None:
        x_pca = self.pca.fit_transform(x)
        cumulative_variance_ratio = np.cumsum(self.pca.explained_variance_ratio_)
        self.n = np.argmax(cumulative_variance_ratio >= 0.95) + 1
        print(self.n)

    def run_pca(self, x) -> list:
        self.select_dimension(x)
        self.pca = PCA(n_components = self.n)
        x_pca = self.pca.fit_transform(x)
        return x_pca


if __name__ == "__main__":
    handler = result_handler()
    handler.get_vector(5)
    model = pca_model()
    result = model.run_pca(handler.vec)
    print(result)
