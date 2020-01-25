import luigi
from luigi.mock import MockTarget


class MockTask(luigi.Task):
    def output(self):
        return MockTarget("mock")


class MockTaskWhichFails(MockTask):
    def run(self):
        raise Exception("Exception in task")


class MockTaskProcess:
    worker_id = 1
    task = MockTask()


class CompleteDownstreamTask(MockTask):
    def complete(self):
        return True

    def requires(self):
        return MockTask()
