import pickle
from abc import ABC, abstractmethod, abstractproperty
from pathlib import Path
from typing import Optional, Union

import joblib
import luigi.format
import pandas as pd
from luigi import LocalTarget


class TargetBase(LocalTarget, ABC):
    @abstractproperty
    def default_file_extension(self):
        return

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
    default_file_extension = "pkl"

    def _load_func(self, file):
        return pickle.load(file)

    def _dump_func(self, obj, file):
        pickle.dump(obj, file)


class ParquetTarget(BinaryTargetBase):
    default_file_extension = "parquet"

    def _load_func(self, file) -> pd.DataFrame:
        return pd.read_parquet(file)

    def _dump_func(self, obj: pd.DataFrame, file):
        obj.to_parquet(file)


class JoblibTarget(BinaryTargetBase):
    default_file_extension = "joblib"

    def _load_func(self, file):
        return joblib.load(file)

    def _dump_func(self, obj, file):
        joblib.dump(obj, file)


class outputs:
    def __init__(self, target: TargetBase, folder: Union[str, Path] = "data") -> None:
        self.target = target
        self.folder = folder if isinstance(folder, Path) else Path(folder)

    def __call__(self, task):
        def output(_self):
            file_name = (
                _self.task_id
                + "."
                + self.target.default_file_extension.replace(".", "")
            )
            return self.target(self.folder / file_name)

        task.output = output
        return task
