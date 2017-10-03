import CCDLUtil.DataManagement.DataParser as CCDLDataParser
import CCDLUtil.DataManagement.FileParser as CCDLFileParser
import CCDLUtil.Utility.AssertVal as CCDLAssert
import CCDLUtil.SignalProcessing.Fourier as CCDLFourier
import scipy.signal as scisig
import numpy as np
import matplotlib
import itertools
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import LeaveOneOut


def run_leave_one_out_cv(features, labels, classifier=LinearDiscriminantAnalysis()):
    """
    Runs leave one out CV.
    :param features: Features shape(epoch, feature)
    :param labels: list of lables of length num epochs
    :param classifier: Sklearn classifier (Defaults to LDA)
    :return: A list of cross validation scores.  Use np.average on the result to find the average score.
    """
    loo = LeaveOneOut()
    scores = []
    for train_indexes, test_indexes in loo.split(features, labels):

        # Assert our split maintains the same number of features
        CCDLAssert.assert_equal(len(train_indexes) + len(test_indexes), features.shape[0])

        # Assert we have the same number of features

        X_train, X_test = features[train_indexes, :], features[test_indexes, :]
        Y_train, Y_test = np.asarray(labels)[train_indexes], np.asarray(labels)[test_indexes]

        # Assert our X_train and X_test have the same number of features
        CCDLAssert.assert_equal(X_train.shape[1], X_test.shape[1])

        # Fit our classifier to our
        classifier.fit(X_train, Y_train)

        score = classifier.score(X_test, Y_test)
        scores.append(score)

    return scores
