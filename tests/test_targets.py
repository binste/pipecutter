import luigi
import pytest
import pandas as pd
from luigi.mock import MockTarget

import pipecutter
from pipecutter.targets import (
    JoblibTarget,
    ParquetTarget,
    PickleTarget,
    outputs,
    remove_targets,
)

targets_and_ext_to_test = [
    (ParquetTarget, ".parquet"),
    (PickleTarget, ".pkl"),
    (JoblibTarget, ".joblib"),
]


@pytest.fixture()
def example_dataframe():
    return pd.DataFrame([[1, 2], [3, 4]], columns=["A", "B"]).set_index("A")


@pytest.mark.parametrize("Target,file_extension", targets_and_ext_to_test)
def test_dataframe_compatible_targets(
    Target, file_extension, tmp_path, example_dataframe
):
    file_path = tmp_path / f"test{file_extension}"
    pt = Target(file_path)
    pt.dump(example_dataframe)

    assert file_path.is_file()
    loaded_data = pt.load()
    assert loaded_data.equals(example_dataframe)


@pytest.mark.parametrize("Target,file_extension", targets_and_ext_to_test)
def test_output(Target, file_extension, tmp_path, example_dataframe):
    @outputs(Target, folder=tmp_path)
    class MockOutputTask(luigi.Task):
        def run(self):
            self.output().dump(example_dataframe)

    class DownstreamTask(luigi.Task):
        def requires(self):
            return MockOutputTask()

        def output(self):
            return MockTarget("mock")

        def run(self):
            assert self.input().load().equals(example_dataframe)
            assert str(self.input().path).endswith(file_extension)

    pipecutter.run(DownstreamTask())


def test_output_default_folder():
    @outputs(JoblibTarget)
    class MockOutputTask(luigi.Task):
        def run(self):
            pass

    t = MockOutputTask()

    assert str(t.output().path) == f"data/{t.task_id}.joblib"


@pytest.mark.parametrize("Target,file_extension", targets_and_ext_to_test)
def test_remove_targets(Target, file_extension, tmp_path, example_dataframe):
    @outputs(Target, folder=tmp_path)
    class MockOutputTask(luigi.Task):
        def run(self):
            self.output().dump(example_dataframe)

    task = MockOutputTask()
    pipecutter.run(task)
    output = task.output()
    assert output.exists()

    remove_targets(task)
    assert not output.exists()


@pytest.mark.parametrize(
    "targets", ["string_target", [ParquetTarget], {"target_name": "string_target"}]
)
def test_outputs_raises_on_wrong_targets(targets):
    with pytest.raises(AssertionError):

        @outputs(targets)
        class MockTask(luigi.Task):
            pass


def test_multiple_outputs(tmp_path, example_dataframe):
    @outputs({"X_train": ParquetTarget, "X_test": ParquetTarget}, folder=tmp_path)
    class MockOutputTask(luigi.Task):
        def run(self):
            outputs = self.output()
            outputs["X_train"].dump(example_dataframe)
            outputs["X_test"].dump(example_dataframe)

    task = MockOutputTask()
    pipecutter.run(task)
    all_outputs = task.output()
    for name, out in all_outputs.items():
        assert out.exists()
        assert name in out.path
