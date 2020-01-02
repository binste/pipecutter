from pipecutter.deps_tree import print_tree

from tests import MockTask


def test_print_tree():
    print_tree(MockTask())
