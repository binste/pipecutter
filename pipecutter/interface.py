from typing import Union, List
from contextlib import contextmanager

import luigi
from luigi import worker


def _raise_run_exception(self, ex) -> None:
    raise ex


@contextmanager
def debug_mode():
    original_handle_run_exception = worker.TaskProcess._handle_run_exception
    try:
        worker.TaskProcess._handle_run_exception = _raise_run_exception
        yield
    finally:
        worker.TaskProcess._handle_run_exception = original_handle_run_exception


def run(
    tasks: Union[luigi.Task, List[luigi.Task]],
    local_scheduler: bool = True,
    print_detailed_summary: bool = True,
    log_level: str = "WARNING",
    **kwargs,
) -> None:
    tasks = [tasks] if isinstance(tasks, luigi.Task) else tasks

    with debug_mode():
        r = luigi.build(
            tasks,
            local_scheduler=local_scheduler,
            log_level=log_level,
            detailed_summary=print_detailed_summary,
            **kwargs,
        )
    if print_detailed_summary:
        print(r.summary_text)
    return
