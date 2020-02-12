import pandas as pd
import numpy as np
import alsDataManager

from bayesianLogisticRegression import BayesianLogisticRegression  # my custom model
from sklearn.linear_model import LogisticRegression
from xgboost.sklearn import XGBClassifier


def get_model_accuracy(m, data):
    """
    :param m: model to measure accuracy of
    :param data: data to predict labels of
    :return: percentage correctly labeled points
    """
    X, y = alsDataManager.get_X_y(data)
    y_pred = m.predict(X)
    return sum(y_pred == y) / len(y)


class AlsModelManager:

    def __init__(self, als):
        self.als = als

    def fit_model(self):
        """
        :return: model fitted on labeled data
        """
        labeled = self.als.dataManager.get_labeled_data()
        X, y = alsDataManager.get_X_y(labeled)

        if self.als.model_type == 'xgboost':
            xgboost_heart_params = {'base_score': 0.5,
                                    'booster': 'gbtree',
                                    'colsample_bylevel': 1,
                                    'colsample_bynode': 1,
                                    'colsample_bytree': 0.5555555555555556,
                                    'gamma': 0.25,
                                    'learning_rate': 0.01,
                                    'max_delta_step': 0,
                                    'max_depth': 4,
                                    'min_child_weight': 5,
                                    'missing': None,
                                    'n_estimators': 75,
                                    'n_jobs': 1,
                                    'nthread': 8,
                                    'objective': 'binary:logistic',
                                    'random_state': 0,
                                    'reg_alpha': 1e-05,
                                    'reg_lambda': 1,
                                    'scale_pos_weight': 1,
                                    'seed': 0,
                                    'silent': None,
                                    'subsample': 1.0,
                                    'verbosity': 1}
            model = XGBClassifier(**xgboost_heart_params)
            model.fit(X, y)

        elif self.als.learning_method == 'bayesian_random':
            model = BayesianLogisticRegression()

            # self.latest_trace = model.fit(X, y, previous_trace = self.latest_trace, cores = self.cores) # returns trace when fitting
            # self.traces.append(self.latest_trace)
            # TODO: verify that the fitting below works
            if self.als.model_initial is not None:
                model.fit(X,
                          y,
                          prior_trace=self.als.model_initial.trace,
                          cores=self.als.cores,
                          prior_index=self.als.model_initial.training_data_index)
            else:
                model.fit(X,
                          y,
                          cores=self.als.cores)
        elif self.als.model_type == 'lr':
            model = LogisticRegression(
                solver='liblinear', max_iter=1000
            )  # can add random state here, can also change parameters
            model.fit(X, y)
        else:
            model = None
            print('Error in fit_model(): model_type or learning_learning no supported')

        return model

    def get_model_consistency(self, m):
        """
        :param m: model
        :return: consistency between model m and initial model
        """
        X, y = alsDataManager.get_X_y(self.als.data['unknown'])
        y_pred_initial = self.als.model_initial.predict(X)
        y_pred_current = m.predict(X)

        return sum(y_pred_initial == y_pred_current) / len(y_pred_initial)

    def get_point_certainty(self, rows):
        """
        :param rows: current_model predicts P(Y=1) for each row in rows
        :return: certainty per row
        """
        X, y = alsDataManager.get_X_y(rows)
        proba_class_1 = self.als.model_current.predict_proba(X)[:, 1]
        class_certainty = np.abs(proba_class_1 - 0.5)[0] / 0.5  # NOTE: assumes only one element in rows
        return class_certainty

    def get_certainties(self):
        """
        :return: df with columns = [min_certainty, min_certainty_of_similar]
                used to get certainty ratios per step in als
        """
        df = pd.DataFrame()
        df.insert(0, 'min_certainty', self.als.max_uncertainties)
        df.insert(0, 'min_certainty_of_similar', self.als.similiar_uncertainties)

        return df
