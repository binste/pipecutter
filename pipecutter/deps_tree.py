import luigi
from luigi.tools.deps_tree import print_tree as luigi_print_tree


def print_tree(task: luigi.Task) -> None:
    print(luigi_print_tree(task))
