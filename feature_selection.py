import json
import pandas as pd
import numpy as np
from sklearn import svm, ensemble, linear_model
from sklearn.model_selection import KFold, cross_val_score
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics.classification import jaccard_similarity_score

# from model_evaluation import plot_confusion_matrix

########################################################################################
#                    Load dataset
########################################################################################
# load the training data
print("Loading data sets...")
DATA_PATH = "data/"
X_train = pd.read_csv("%sX_train.csv" % DATA_PATH).values
Y_train = pd.read_csv("%sY_train.csv" % DATA_PATH).values
X_test = pd.read_csv("%sX_test.csv" % DATA_PATH).values
Y_test = pd.read_csv("%sY_test.csv" % DATA_PATH).values

# transform panda df into arrays
X_train = np.delete(X_train, 0, axis=1)
Y_train = np.delete(Y_train, 0, axis=1).flatten()
X_test = np.delete(X_test, 0, axis=1)
Y_test = np.delete(Y_test, 0, axis=1).flatten()

f = open("%sclass_names.txt" % DATA_PATH)
class_names = json.load(f)
f.close()

print("Dataset loaded.")


########################################################################################
#                     parameter tuning for SVM and RF
########################################################################################
def kfold_model_score(model, X_train, Y_train, numFolds=5):
    k_fold_shuttle = KFold(n_splits=numFolds, random_state=100).get_n_splits(X_train, Y_train)
    return np.mean(cross_val_score(model, X_train, Y_train, cv=k_fold_shuttle))


# # test alpha value in increasing order
# alpha_params = [0.00001, 0.0001, 0.001, 0.01, 0.1, 1, 5, 50, 100, 200, 500, 1000]
#
#
# def tune_alpha(alpha_params, X_train, Y_train, X_test, Y_test):
#     for alpha in alpha_params:
#         model = linear_model.SGDClassifier(random_state=100, alpha=alpha, n_jobs=-1, penalty="l1", tol=1e-3)
#         model = model.fit(X_train, Y_train)
#         model_pred = model.predict(X_test)
#         model_score = jaccard_similarity_score(Y_test, model_pred)
#         print("Linear SVC score with alpha {:5f}: {:5f}".format(alpha, model_score.mean()))
#
#
# tune_alpha(alpha_params, X_train, Y_train, X_test, Y_test)
#
# # test the effect of number of tree on accuracy for random forest
# rf_clf = ensemble.RandomForestClassifier(random_state=100, n_jobs=-1)
# trees = [5, 10, 15, 20, 25, 50, 75, 100]
#
#
# def tune_trees(trees, X_train, Y_train, X_test, Y_test):
#     for tree in trees:
#         model = ensemble.RandomForestClassifier(random_state=100, n_jobs=-1, n_estimators=tree)
#         model = model.fit(X_train, Y_train)
#         model_pred = model.predict(X_test)
#         model_score = jaccard_similarity_score(Y_test, model_pred)
#         print("Random Forest score with {} trees: {:5f}".format(tree, model_score.mean()))
#
#
# tune_trees(trees, X_train, Y_train, X_test, Y_test)

########################################################################################
#                    Feature selection
########################################################################################
print("\nPerforming feature selection using Sparse SVM and RF \n")

# TODO
# use defealt threshold level
# 3 methods to feature selection, svm, rf, logistic regression
# 200 features, -> 20 -> 10
# draw graph to visualize different method for feature selection Y: accuracy, X: num of features

C_params = [1e-13, 1e-12,1e-10, 1e-09, 1e-08, 1e-07, 1e-06, 0.00001, 0.00005, 0.00001, 0.0001, 0.001, 0.01, 0.1, 1, 1000000]
C_params.reverse()
print(C_params)



# perform feature selection using sparse svm
def svm_feature_selection(C_params):
    for C in C_params:
        svm_select= svm.LinearSVC(random_state=100, penalty="l1", C=C, dual=True, tol=1e-4)
        svm_select = SelectFromModel(svm_select).fit(X_train, Y_train)
        svm_features= svm_select.transform(X_train)
        print("\nWith C={}".format(C))
        print("Sparse SVM reduced number of features to {}.".format(svm_features.shape[1]))
        svm_clf_l1 = linear_model.SGDClassifier(random_state=100, penalty="l1", n_jobs=-1, alpha=0.01, tol=1e-4)
        svm_clf_l1_score = kfold_model_score(svm_clf_l1, svm_features, Y_train)
        print("SGD l1 CV score after FEATURE SELECTION: {:5f}".format(svm_clf_l1_score.mean()))


svm_feature_selection(C_params)

# perform feature selection using rf, use mean as threshold
thresholds = [0, 1e-06, 2e-06, 5e-06, 1e-05, 2e-05, 5e-05, 0.00001, 0.00005, 0.0001, 0.0005, 0.001]


def rf_feature_selection(thresholds):
    for threshold in thresholds:
        rf_clf = ensemble.RandomForestClassifier(random_state=100, n_jobs=-1, n_estimators=50)
        rf_select = SelectFromModel(estimator=rf_clf, threshold=threshold)
        rf_select = rf_select.fit(X_train, Y_train)
        rf_features = rf_select.transform(X_train)
        print("\nWith threshold {}".format(threshold))
        print("RF reduced number of features to {}.".format(rf_features.shape[1]))

        rf_clf = ensemble.RandomForestClassifier(random_state=100, n_jobs=-1, n_estimators=50)
        rf_clf_score = kfold_model_score(rf_clf, rf_features, Y_train)
        print("RF CV score after FEATURE SELECTION: {:5f}".format(rf_clf_score.mean()))


rf_feature_selection(thresholds)
