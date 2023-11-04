import numpy as np
import pandas as pd
import xgboost as xgb
from datetime import datetime
from sklearn.preprocessing import OneHotEncoder

from typing import Tuple, Union, List


class DelayModel:
    def __init__(self):
        self._model = xgb.XGBClassifier(random_state=1, learning_rate=0.01)
        self._encoder = None
        self.top_10_features = [
            "OPERA_Latin American Wings",
            "MES_7",
            "MES_10",
            "OPERA_Grupo LATAM",
            "MES_12",
            "TIPOVUELO_I",
            "MES_4",
            "MES_11",
            "OPERA_Sky Airline",
            "OPERA_Copa Air",
        ]

    def preprocess(
        self, data: pd.DataFrame, target_column: str = None
    ) -> Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]:
        """
        Prepare raw data for training or predict.

        Args:
            data (pd.DataFrame): raw data.
            target_column (str, optional): if set, the target is returned.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: features and target.
            or
            pd.DataFrame: features.
        """

        # create the encoded features from dataframe using OneHotEncoder
        x_data = self._preprocess_model_input_data(data)

        # set label data and balancing if we are in training context
        if target_column:
            y_data = self._set_label_data(data, target_column)

            # calculate scale for target balancing
            n_y0 = len(y_data[y_data[target_column] == 0])
            n_y1 = len(y_data[y_data[target_column] == 1])
            scale = n_y0 / n_y1

            # set xgb models 'scale_pos_weight' attribute accordingly
            self._model.scale_pos_weight = scale

            return (x_data, y_data)

        return x_data

    def fit(self, features: pd.DataFrame, target: pd.DataFrame) -> None:
        """
        Fit model with preprocessed data.

        Args:
            features (pd.DataFrame): preprocessed data.
            target (pd.DataFrame): target.
        """

        # train the XGBClassifier model
        self._model.fit(features, target)

    def predict(self, features: pd.DataFrame) -> List[int]:
        """
        Predict delays for new flights.

        Args:
            features (pd.DataFrame): preprocessed data.

        Returns:
            (List[int]): predicted targets.
        """

        # convert all prediction values to 'int', default return typ is numpy.int32
        return list(map(int, self._model.predict(features)))

    def _set_label_data(
        self, data: pd.DataFrame, target_column_name: str, threshold_for_delay: int = 15
    ) -> pd.DataFrame:
        """Calculates the labels from input data

        Args:
            data (pd.DataFrame): _description_
            threshold_for_delay (int, optional): _description_. Defaults to 15.

        Returns:
            list[int]: _description_
        """

        def get_min_diff(data):
            fecha_o = datetime.strptime(data["Fecha-O"], "%Y-%m-%d %H:%M:%S")
            fecha_i = datetime.strptime(data["Fecha-I"], "%Y-%m-%d %H:%M:%S")
            return ((fecha_o - fecha_i).total_seconds()) / 60

        data["min_diff"] = data.apply(get_min_diff, axis=1)

        return pd.DataFrame(
            columns=[target_column_name],
            data=np.where(data["min_diff"] > threshold_for_delay, 1, 0),
        )

    def _preprocess_model_input_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preprocesses the data used for model prediction. We use a OneHotEncoder and only return the top 10 features the DS told us to use

        Args:
            data (pd.DataFrame): the input data

        Returns:
            pd.DataFrame: the preprocessed dataframe only contained the top 10 feature columns
        """

        # if encoder not yet fitted
        if not self._encoder:
            self._encoder = OneHotEncoder(sparse=False)

            features = pd.DataFrame(
                data=self._encoder.fit_transform(data[["OPERA", "TIPOVUELO", "MES"]]),
                columns=self._encoder.get_feature_names_out(
                    ["OPERA", "TIPOVUELO", "MES"]
                ),
            )

        # encoder was already fitted
        else:
            features = pd.DataFrame(
                data=self._encoder.transform(data[["OPERA", "TIPOVUELO", "MES"]]),
                columns=self._encoder.get_feature_names_out(
                    ["OPERA", "TIPOVUELO", "MES"]
                ),
            )

        # Top 10 features to use according to DS
        return features[self.top_10_features]
