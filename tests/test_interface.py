import pytest
from luigi import worker
from pipecutter.interface import run, debug_mode
from tests import MockTask, MockTaskProcess, MockTaskWhichFails


def test_debug_mode():
    exception_text = "Exception in task"

    assert_original_handle_run_exception_is_set()
    with debug_mode():
        with pytest.raises(Exception, match=exception_text):
            worker.TaskProcess._handle_run_exception(
                MockTaskProcess(), Exception(exception_text)
            )
        with pytest.raises(AssertionError):
            assert_original_handle_run_exception_is_set()
    assert_original_handle_run_exception_is_set()


def assert_original_handle_run_exception_is_set():
    assert worker.TaskProcess._handle_run_exception.__name__ == "_handle_run_exception"
    worker.TaskProcess._handle_run_exception(MockTaskProcess(), Exception)


def test_run():
    run(MockTask())
    run([MockTask()])


def test_run_raises_on_exception():
    with pytest.raises(Exception, match="Exception in task"):
        run(MockTaskWhichFails())
