# pipecutter
[![PyPI version](http://img.shields.io/pypi/v/pipecutter.svg?style=flat-square&color=blue)](https://pypi.python.org/pypi/pipecutter/) [![Python versions](https://img.shields.io/pypi/pyversions/pipecutter.svg?style=flat-square&color=blue)]() [![build status](http://img.shields.io/travis/binste/pipecutter/master.svg?style=flat)](https://travis-ci.org/binste/pipecutter) [![coverage](https://img.shields.io/codecov/c/github/binste/pipecutter/master.svg?style=flat)](https://codecov.io/gh/binste/pipecutter?branch=master)

pipecutter provides a few tools for luigi such that it works better with data science libraries and environments such as pandas, scikit-learn, and Jupyter notebooks.

- [pipecutter](#pipecutter)
- [Installation](#installation)
- [Usage](#usage)
  - [Debug in an interactive environment](#debug-in-an-interactive-environment)
  - [Targets](#targets)
- [Other interesting libraries](#other-interesting-libraries)

# Installation
```bash
pip install pipecutter
```

Python 3.6+ is required. pipecutter follows [semantic versioning](https://semver.org/).

# Usage
pipecutter currently provides

* a more convenient way to run and debug luigi tasks in interactive environments such as Jupyter notebooks
* some luigi targets for saving pandas dataframes to parquet, scikit-learn models with joblib, ...

## Debug in an interactive environment
With luigi, you can already run tasks in a Python script/Jupyter notebook/Python console by using the `luigi.build` function (probably with `local_scheduler=True` as arugment). However, if the tasks throws an exception this will be caught by luigi and you are not able to drop into a post mortem debugging session. `pipecutter.run` is a light wrapper around `luigi.build` which disables this exception handling.

```python
In [1]: import luigi
In [2]: import pipecutter

In [3]: class TaskWhichFails(luigi.Task):
   ...:     def run(self):
   ...:         raise Exception("Something is wrong")

# Traceback below is shortened for readability
In [4]: pipecutter.run(TaskWhichFails())
---------------------------------------------------------------------------
Exception                                 Traceback (most recent call last)
<ipython-input-5-a970d52d810a> in <module>
----> 1 pipecutter.run(TaskWhichFails())

...

<ipython-input-3-4e27674090fa> in run(self)
      1 class TaskWhichFails(luigi.Task):
      2     def run(self):
----> 3         raise Exception

Exception: Something is wrong

# Drop straight into the debugger
In [5]: %debug
> <ipython-input-6-e7528a27d82e>(3)run()
      1 class TaskWhichFails(luigi.Task):
      2     def run(self):
----> 3         raise Exception
      4
ipdb>
```
This should reduce the barrier for already using luigi tasks while developing a model and thereby making it easier to move into production later on.

Additionally, you can print the dependencies of tasks with `pipecutter.print_tree` (wrapper around `luigi.tools.deps_tree.print_tree`).

## Targets
In `pipecutter.targets` you find a few targets which build on luigi's `LocalTarget` but additionally have a `load` and a `dump` method. A convenient way to name the targets is hereby to use the `task_id` in the name, which is unique with respect to the task name and its passed in parameters.

```python
import luigi
import pipecutter
from pipecutter.targets import JoblibTarget
from sklearn.ensemble import RandomForestClassifier

class TrainModel(luigi.Task):
    def output(self):
        return JoblibTarget(self.task_id + ".pkl")

    def run(self):
        model = RandomForestClassifier()
        self.output().dump(model)

pipecutter.run(TrainModel())
# -> Produces a file called TrainModel__99914b932b.pkl
```

# Other interesting libraries
* [d6tflow](https://github.com/d6t/d6tflow)
* [sciluigi](https://github.com/pharmbio/sciluigi)
