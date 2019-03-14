"""
=======================================================
Scalable learning with polynomial kernel aproximation
=======================================================

This example illustrates the use of :class:`PolynomialSampler` to efficiently
generate polynomial kernel feature-space approximations, which can be used
to train linear classifiers that approximate the accuracy of kernelized ones.

.. currentmodule:: sklearn.kernel_approximation

We use the Covtype dataset, trying to reproduce the experiments on the
original paper of Tensor Sketch [1] (i.e., the algorithm implemented by
:class:`PolynomialSampler`).

First, we compute the accuracy of a linear classifier on the original
features. Then, we train linear classifiers on different numbers of features
generated by :class:`PolynomialSampler`, approximatting the accuracy of a
kernelized classifier in a scalable manner.

[1] Pham, N., & Pagh, R. (2013, August). Fast and scalable polynomial
kernels via explicit feature maps. In Proceedings of the 19th ACM SIGKDD
international conference on Knowledge discovery and data mining (pp. 239-247)
(http://chbrown.github.io/kdd-2013-usb/kdd/p239.pdf)

"""
print(__doc__)

# Author: Daniel Lopez-Sanchez <lope@usal.es>
# License: BSD 3 clause

# Load data manipulation functions
from sklearn.datasets import fetch_covtype
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import normalize, MinMaxScaler

# Load linear classifier
from sklearn.svm import LinearSVC

# Load class for polynomial kernel feature-map approximation
from sklearn.kernel_approximation import PolynomialSampler

# Fetch data
data = fetch_covtype()
X, Y = data["data"], data["target"]

# Transform into a binary classification problem to match the format of the
# dataset in the LIBSVM webpage
# ww.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary.html#covtype.binary
Y[Y != 2] = 0
Y[Y == 2] = 1

# Select 10,000 samples for training and 10,000 for testing.
# To reproduce the results in the original paper, select 100,000.
# Tensor Sketch paper (see chbrown.github.io/kdd-2013-usb/kdd/p239.pdf)
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, train_size=10000,
                                                    test_size=10000,
                                                    random_state=42)

# Scale features to the range [0, 1] to match the format of the dataset in the
# LIBSVM webpage, and then normalize to unit lenght as done in the original
# Tensor Sketch paper (see chbrown.github.io/kdd-2013-usb/kdd/p239.pdf)
mm = MinMaxScaler().fit(X_train)
X_train = normalize(mm.transform(X_train))
X_test = normalize(mm.transform(X_test))

# Train a linear SVM on the original features and print accuracy
lsvm = LinearSVC()
lsvm.fit(X_train, Y_train)
print("Linear SVM score on raw features: %.2f %%"
      % (100*lsvm.score(X_test, Y_test)))

# Train linear SVMs on various numbers of PolynomialSampler features
for n_components in [200, 500, 1000, 1500]:

    ps = PolynomialSampler(n_components=n_components,
                           degree=4).fit(X_train[0:1])
    X_train_ps = ps.transform(X_train)
    X_test_ps = ps.transform(X_test)

    lsvm = LinearSVC()
    lsvm.fit(X_train_ps, Y_train)
    print("Linear SVM score on %d PolynomialSampler " % n_components +
          "features: %.2f %%" % (100*lsvm.score(X_test_ps, Y_test)))

# Train a kernelized SVM and see how well is
# PolynomialSampler approximating the performance of the kernel
# (may take a while, as SVC has a relatively poor scalability).
# This should result in an accuracy of about 84% if 100,000 training
# samples are used.

from sklearn.svm import SVC
ksvm = SVC(C=500., kernel="poly", degree=4, coef0=0,
           gamma=1.).fit(X_train, Y_train)
print(ksvm.score(X_test, Y_test))
