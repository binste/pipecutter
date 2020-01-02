import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union

import joblib
import luigi.format
import pandas as pd
from luigi import LocalTarget


class TargetBase(LocalTarget, ABC):
    def load(self):
        return self._load()

    def _load(self):
        with self.open("r") as f:
            obj = self._load_func(f)
        return obj

    @abstractmethod
    def _load_func(self, file):
        return

    def dump(self, obj):
        self.makedirs()
        self._dump(obj)

    def _dump(self, obj):
        with self.open("w") as f:
            self._dump_func(obj, f)

    @abstractmethod
    def _dump_func(self, obj, file):
        pass


class BinaryTargetBase(TargetBase):
    def __init__(self, path: Optional[Union[Path, str]] = None, **kwargs):
        super().__init__(path, format=luigi.format.Nop, **kwargs)


class PickleTarget(BinaryTargetBase):
    def _load_func(self, file):
        return pickle.load(file)

    def _dump_func(self, obj, file):
        pickle.dump(obj, file)


class ParquetTarget(BinaryTargetBase):
    def _load_func(self, file) -> pd.DataFrame:
        return pd.read_parquet(file)

    def _dump_func(self, obj: pd.DataFrame, file):
        obj.to_parquet(file)


class JoblibTarget(BinaryTargetBase):
    def _load_func(self, file):
        return joblib.load(file)

    def _dump_func(self, obj, file):
        joblib.dump(obj, file)
