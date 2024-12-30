import dataclasses
import multiprocessing
import threading
import typing
from concurrent.futures import ThreadPoolExecutor


def _t_initialize_pool():
    global t_pool
    t_pool = ThreadPoolExecutor(max_workers=10)


def _initialize_pool():
    global pool
    pool = multiprocessing.Pool(processes=10)


@dataclasses.dataclass
class ThreadResult:
    return_value: typing.Any = None
    exception: Exception = None

    def was_successful(self) -> bool:
        return self.exception is None


class ThreadWithResult(threading.Thread):
    """Extension of Thread that keeps track of the thread's result.

    This class is useful for executing a function in a thread and storing
    the result (i.e., the return value and exception raised).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = ThreadResult()

    def run(self):
        """Method to be run in thread."""
        try:
            if self._target:
                self.result.return_value = self._target(*self._args, **self._kwargs)
        except Exception as e:
            self.result.exception = e
            raise


@dataclasses.dataclass
class ProcessResult:
    return_value: typing.Any = None
    exception: Exception = None

    def was_successful(self) -> bool:
        return self.exception is None


class ProcessWithResult(multiprocessing.Process):
    """Extension of Process that Keeps track of the child process' result.

    This class is useful for executing a function in a child process and storing
    the result (i.e., the return value and exception raised).

    Inspired by:
    https://stackoverflow.com/a/33599967/3769045
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create the Connection objects used for communication between the
        # parent and child processes.
        self.parent_conn, self.child_conn = multiprocessing.Pipe()

    def run(self):
        """Method to be run in sub-process."""
        result = ProcessResult()
        try:
            if self._target:
                result.return_value = self._target(*self._args, **self._kwargs)
        except Exception as e:
            result.exception = e
            raise
        finally:
            self.child_conn.send(result)

    def result(self):
        """Get the result from the child process.

        Returns:
            If the child process has completed, a ProcessResult object.
            Otherwise, a None object.
        """
        return self.parent_conn.recv() if self.parent_conn.poll() else None


def with_timeout(function, *, args=None, timeout_in_seconds):
    """Executes a function in a child process with a specified timeout.

    Usage example:

        with_timeout(save_contact,
                     args=(first_name, last_name),
                     timeout_in_seconds=0.5)

    Args:
        function: The function to be executed in a child process.
        args: Optional `function` arguments as a tuple.
        timeout_in_seconds: The execution time limit in seconds.

    Returns:
        The return value of the `function`.

    Raises:
        TimeoutError: If the execution time of the `function` exceeds the
            timeout `seconds`.
    """
    if 'pool' not in globals():
        _initialize_pool()

    result = pool.apply_async(function, args=args or ())
    try:
        return result.get(timeout=timeout_in_seconds)
    except multiprocessing.TimeoutError:
        pass


def with_timeout_t(function, *, args=None, timeout_in_seconds):
    """Executes a function in a thread with a specified timeout.

    Usage example:

        with_timeout(save_contact,
                     args=(first_name, last_name),
                     timeout_in_seconds=0.5)

    Args:
        function: The function to be executed in a thread.
        args: Optional `function` arguments as a tuple.
        timeout_in_seconds: The execution time limit in seconds.

    Returns:
        The return value of the `function`.

    Raises:
        TimeoutError: If the execution time of the `function` exceeds the
            timeout `seconds`.
    """
    if 't_pool' not in globals():
        _t_initialize_pool()

    future = t_pool.submit(function, *(args or ()))
    try:
        return future.result(timeout=timeout_in_seconds)
    except TimeoutError:
        raise TimeoutError('Function execution exceeded the timeout')


def _wait_for_thread_exit(target_thread):
    max_attempts = 3
    for _ in range(max_attempts):
        target_thread.join(timeout=0.1)


def _wait_for_process_exit(target_process):
    max_attempts = 3
    for _ in range(max_attempts):
        target_process.join(timeout=0.1)


def background_thread(function, args=None):
    """Runs the given function in a background thread.

    Note: The function is executed in a "fire and forget" manner.

    Args:
        function: The function to be executed in a thread.
        args: Optional `function` arguments as a tuple.
    """
    thread = threading.Thread(target=function, args=args or ())
    thread.start()
