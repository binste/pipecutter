import pytest
import pandas as pd

from pipecutter.targets import JoblibTarget, ParquetTarget, PickleTarget


@pytest.fixture()
def example_dataframe():
    return pd.DataFrame([[1, 2], [3, 4]], columns=["A", "B"]).set_index("A")


@pytest.mark.parametrize(
    "Target,file_extension",
    [(ParquetTarget, ".parquet"), (PickleTarget, ".pkl"), (JoblibTarget, ".pkl")],
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
