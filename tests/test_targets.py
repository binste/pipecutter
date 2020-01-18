import luigi
import pytest
import pandas as pd
from luigi.mock import MockTarget

import pipecutter
from pipecutter.targets import JoblibTarget, ParquetTarget, PickleTarget, outputs


@pytest.fixture()
def example_dataframe():
    return pd.DataFrame([[1, 2], [3, 4]], columns=["A", "B"]).set_index("A")


@pytest.mark.parametrize(
    "Target,file_extension",
    [(ParquetTarget, ".parquet"), (PickleTarget, ".pkl"), (JoblibTarget, ".joblib")],
)
def test_dataframe_compatible_targets(
    Target, file_extension, tmp_path, example_dataframe
):
    file_path = tmp_path / f"test{file_extension}"
    pt = Target(file_path)
    pt.dump(example_dataframe)

    assert file_path.is_file()
    loaded_data = pt.load()
    assert loaded_data.equals(example_dataframe)


@pytest.mark.parametrize(
    "Target,file_extension",
    [(ParquetTarget, "parquet"), (PickleTarget, "pkl"), (JoblibTarget, "joblib")],
)
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
