import pickle
from abc import ABC, abstractmethod, abstractproperty
from pathlib import Path
from typing import Optional, Union, Dict, Any

import joblib
import luigi.format
import pandas as pd
import luigi.task
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
    def __init__(
        self,
        targets: Union[TargetBase, Dict[Any, TargetBase]],
        folder: Union[str, Path] = "data",
    ) -> None:
        self._validate_targets(targets)

        self.targets = targets
        self.folder = folder if isinstance(folder, Path) else Path(folder)

    def _validate_targets(self, targets):
        try:
            assert (
                isinstance(targets, dict)
                and all(issubclass(v, TargetBase) for v in targets.values())
            ) or issubclass(targets, TargetBase)
        except TypeError:
            # TODO: Improve this error message to be more informative
            raise AssertionError("Probably no class was passed")

    def __call__(self, task):
        def _create_file_name(task_id: str, target: TargetBase) -> str:
            return task_id + "." + target.default_file_extension.replace(".", "")

        def output(_self):
            if isinstance(self.targets, dict):
                prepared_targets = {}
                for name, target in self.targets.items():
                    file_name = _create_file_name(_self.task_id + "_" + name, target)
                    prepared_targets[name] = target(self.folder / file_name)
                return prepared_targets
            else:
                file_name = _create_file_name(_self.task_id, self.targets)
                return self.targets(self.folder / file_name)

        task.output = output
        return task


def remove_targets(task):
    outputs = luigi.task.flatten(task.output())
    for out in outputs:
        if out.exists():
            out.remove()
        assert not out.exists()
