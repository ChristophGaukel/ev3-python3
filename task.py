#!/usr/bin/env python3

# Copyright (C) 2016 Christoph Gaukel <christoph.gaukel@gmx.de>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import typing, numbers, threading, time, datetime, sys

STATE_INIT = 'INIT'
STATE_TO_START = 'TO_START'
STATE_STARTED = 'STARTED'
STATE_TO_STOP = 'TO_STOP'
STATE_STOPPED = 'STOPPED'
STATE_TO_CONTINUE = 'TO_CONTINUE'
STATE_FINISHED = 'FINISHED'

ACTIVITY_NONE = 'NONE'
ACTIVITY_BUSY = 'BUSY'
ACTIVITY_SLEEP = 'SLEEP'
ACTIVITY_JOIN = 'JOIN'

class ExceptionHandler:
    """
    Handles Exceptions of task objects
    If anywhere an exceptions occured and was put to the ExceptionHandler,
    any thread that uses the same instance of ExceptionHandler exits,
    when it calls its method fire 
    """
    def __init__(self):
        self._exc = False

    def put(self, exc: Exception):
        """
        informs, that an exception occured

        Arguments:
        exc: Exception, ignored, but subclasses may distinguish
        """
        self._exc = True

    def fire(self, lock: threading.Lock=None):
        """
        fires sys.exit(1) if an exception occured, else does nothing
        """
        if self._exc:
            if lock and lock.locked():
                lock.release()
            sys.exit(1)

def concat(*tasks) -> 'Task':
    """
    concats a number of tasks and returns a chain of tasks
    """
    chain = None
    for task in tasks:
        assert isinstance(task, Task), 'tasks must be instances of class Task'
        if not chain:
            chain = task
        else:
            chain.append(task)
    return chain

class Task:
    """
    Uses multithreading for tasks or chains of tasks.
    In standard case it's an action, which is executed by a single callable.
    Subsequent tasks or chains of tasks can be added with method append().
    """
    _exc_default = ExceptionHandler()
    _contained_register = {}
    
    def __init__(self, action: typing.Callable, **kwargs):
        """
        Construct a new 'Task' object

        Arguments:
        action: callable object (f.i. a function).

        Keyword Arguments:
        args: tuple=() -- argument list of action
        kwargs: dict={} -- keyword arguments of action
        action_stop: typing.Callable=None -- object (f.i. a function), which is called when task is stopped.
        args_stop: tuple=() -- argument list of action_stop
        kwargs_stop: dict={} -- keyword arguments of action_stop
        action_cont: typing.Callable=None -- object (f.i. a function), which is called when task is continued.
        args_cont: tuple=() -- argument list of action_cont
        kwargs_cont: dict={} -- keyword arguments of action_cont
        join: bool=False -- flag if contained task will be joined
        duration: float=None -- duration of task (if action returns earlier, task will wait)
        exc: ExceptionHandler=None -- exception handler to coordinate exceptions

        example:
        def a1():
            print("action 1 - started")
        def a2(text: str):
            print(text, "- started")
        def a3(txt: str="something"):
            print(txt, "- started")
        task.cont(
            Task(a1),
            Task(a2, args=("action 2",)),
            Task(a3, kwargs={"txt": "action 3"})
        ).start()
        """
        self._action = action
        self._args = kwargs.pop('args', ())
        self._kwargs = kwargs.pop('kwargs', {})
        self._join = kwargs.pop('join', False)
        self._duration = kwargs.pop('duration', None)
        self._num = kwargs.pop('num', 0)
        self._next = None
        self._root = self
        self._time_end = None
        self._netto_time = False
        self._cnt = 0
        # the following are root only attributes
        self._state = STATE_INIT
        self._thread = None
        self._thread_start = None
        self._restart = False
        self._thread_cont = None
        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)
        self._actual = None
        self._last = None
        self._activity = ACTIVITY_NONE
        self._time_action = None
        self._time_called_stop = None
        self._contained = []
        self._cont_join = None
        self._action_stop = kwargs.pop('action_stop', None)
        self._args_stop = kwargs.pop('args_stop', ())
        self._kwargs_stop = kwargs.pop('kwargs_stop', {})
        self._action_cont = kwargs.pop('action_cont', None)
        self._args_cont = kwargs.pop('args_cont', ())
        self._kwargs_cont = kwargs.pop('kwargs_cont', {})
        self._exc = kwargs.pop('exc', self._exc_default)
        self._exc.fire()
        assert not kwargs, 'unknown keyword arguments: ' + str(kwargs.keys())
        assert isinstance(self._action, typing.Callable), \
            "action needs to be a callable"
        assert isinstance(self._args, tuple), 'args needs to be a tuple'
        assert isinstance(self._kwargs, dict), 'kwargs needs to be a dictionary'
        assert self._action_stop is None or isinstance(self._action_stop, typing.Callable), \
            "action_stop needs to be a callable"
        assert isinstance(self._args_stop, tuple), 'args_stop needs to be a tuple'
        assert isinstance(self._kwargs_stop, dict), 'kwargs_stop needs to be a dictionary'
        assert self._action_cont is None or isinstance(self._action_cont, typing.Callable), \
            "action_cont needs to be a callable"
        assert isinstance(self._args_cont, tuple), 'args_cont needs to be a tuple'
        assert isinstance(self._kwargs_cont, dict), 'kwargs_cont needs to be a dictionary'
        assert isinstance (self._join, bool), 'join needs to be a bool value'
        assert not self._join or hasattr(self._action, '__self__'), 'only bounded methods can be joined'
        assert not self._join or isinstance(self._action.__self__, Task), 'only instances of Task can be joined'
        assert not self._join or self._action.__name__ in ["start", "cont"], 'only methods start or cont can be joined'
        assert self._duration is None or isinstance(self._duration, numbers.Number), \
            'duration needs to be a number'
        assert self._duration is None or self._duration >= 0, \
            'duration needs to be positive'
        assert isinstance(self._num, int), 'num must be an integer'
        assert self._num >= 0, 'num must be positive'
        assert self._exc is None or isinstance(self._exc, ExceptionHandler), \
            'exc needs to be an ExceptionHandler instance'

    def append(self, task) -> 'Task':
        """
        appends a task or a chain of tasks (both must be root tasks)
        """
        try:
            assert self._root is self, 'appending to root tasks only'
            assert task._root is task, 'both tasks need to be root tasks'
            assert self._state in [
                STATE_INIT,
                STATE_FINISHED,
                STATE_STOPPED
            ], 'root task is actually executed'
            assert task._state in [
                STATE_INIT,
                STATE_FINISHED,
                STATE_STOPPED
            ], 'appended task is actually executed'
            assert not (self is task and self._last is self), 'is already self-contained'
        except Exception as exc:
            self._root._exc.put(exc)
            raise
        self._exc.fire()
        if self._last is None and task._last is None:
            self._last = task
            self._next = task
        elif self._last is None:
            self._last = task._last
            self._next = task
        elif task._last is None:
            self._last._next = task
            self._last = task
        elif self is task:
            self._last._next = self
            self._last = self
        else:
            self._last._next = task
            self._last = task._last
        if not self is task:
            task.root = self
        return self

    def start(self, gap: float=0) -> 'Task':
        """
        starts execution of task (finished or stopped tasks may be started again)

        Keyword Arguments:
        gap: sets the waiting time, before start occurs (in seconds)
        """
        self._root._exc.fire()
        self._root._lock.acquire()
        try:
            assert isinstance(gap, numbers.Number), 'gap needs to be a number'
            assert gap >= 0, 'gap needs to be positive'
            assert self._root is self, 'only root tasks can be started'
            assert self._state in [
                STATE_INIT,
                STATE_TO_STOP,
                STATE_STOPPED,
                STATE_FINISHED
            ], "can't start from state " + self._state
            assert self._thread_start is None, "starting is already in progress"
            assert self._thread_cont is None, "continuation is already in progress"
        except Exception as exc:
            self._root._exc.put(exc)
            self._root._lock.release()
            raise
        if self._state == STATE_TO_STOP or gap > 0:
            if self._state == STATE_TO_STOP:
                self._restart = True
            else:
                self._state = STATE_TO_START
            if gap:
                self._thread_start = threading.Thread(
                    target=self._start2,
                    args=(time.time() + gap,)
                )
            else:
                self._thread_start = threading.Thread(target=self._start2)
            self._thread_start.start()
        else:
            self._start3()
            self._thread = threading.Thread(target=self._execute)
            self._thread.start()
        return self

    def _start2(self, time_action: float=None) -> None:
        if self._state == STATE_TO_STOP:
            self._lock.release()
            self._thread.join()
            self._exc.fire()
            self._lock.acquire()
        if not threading.current_thread() is self._thread_start:
            self._lock.release()
            return
        if time_action:
            gap = time_action - time.time()
            if gap > 0:
                self._activity = ACTIVITY_SLEEP
                self._cond.wait(gap)
                self._activity = ACTIVITY_NONE
                self._exc.fire(self._lock)
                if not threading.current_thread() is self._thread_start:
                    self._lock.release()
                    return
        self._thread = self._thread_start
        self._thread_start = None
        self._start3()
        self._execute()

    def _start3(self) -> None:
        self._state = STATE_STARTED
        self._restart = False
        self._time_called_stop = None
        self._actual = self
        self._cnt = 0
        self._time_action = time.time()
        if self._duration != None:
            self._time_end = self._time_action + self._duration

    def join(self) -> None:
        """
        joins the thread of the task 
        """
        try:
            assert self._root is self, "only root tasks can be joined"
            assert self._state != STATE_INIT, "can't join tasks in state " + str(self._state)
        except Exception as exc:
            self._root._exc.put(exc)
            raise
        self._exc.fire()
        try: self._thread_start.join()
        except Exception: pass
        try: self._thread_cont.join()
        except Exception: pass
        try: self._thread.join()
        except Exception: pass

    def stop(self) -> None:
        """
        stops execution as fast as possible
            allows to continue with method cont or restart with method start
            already finished tasks silently do nothing
        """
        self._root._exc.fire()
        self._root._lock.acquire()
        try:
            assert self is self._root, 'only root tasks can be stopped'
            assert self._state in [
                STATE_TO_START,
                STATE_STARTED,
                STATE_TO_STOP,
                STATE_TO_CONTINUE,
                STATE_FINISHED
            ], "can't stop from state: " + self._state
            assert self._state != STATE_TO_STOP or self._thread_start or self._thread_cont, \
                "stopping is already in progress"
        except Exception as exc:
            self._root._exc.put(exc)
            self._root._lock.release()
            raise
        if self._state == STATE_FINISHED:
            self._lock.release()
            return
        if self._time_called_stop is None:
            self._time_called_stop = time.time()
        if self._activity is ACTIVITY_SLEEP:
            self._cond.notify()
        not_stopped = []
        for task in self._contained:
            if not task in self._contained_register or \
               not self._contained_register[task] is self:
                continue
            task.lock.acquire()
            if task._state in [STATE_STARTED, STATE_TO_START, STATE_TO_CONTINUE]:
                not_stopped.append(task)
            elif task._state == STATE_TO_STOP and (task._thread_start or task._thread_cont):
                not_stopped.append(task)
            task.lock.release()
        for task in not_stopped:
            task.stop()
        if self._state == STATE_STARTED:
            self._state = STATE_TO_STOP
        elif self._thread_start:
            self._thread_start = None
            if self._state == STATE_TO_START:
                self._state = STATE_STOPPED
        else:
            self._thread_cont = None
            if self._state == STATE_TO_CONTINUE:
                self._state = STATE_STOPPED
        self._lock.release()

    def cont(self, gap: float=None) -> 'Task':
        """
        continues a stopped task (must be a root task)

        Keyword Arguments:
        gap: sets the waiting time before the next action occurs (in seconds)
        """
        self._exc.fire()
        self._lock.acquire()
        try:
            assert self is self._root, 'only root tasks can be continued'
            assert gap is None or isinstance(gap, numbers.Number), 'gap needs to be a number'
            assert gap is None or gap >= 0, 'gap needs to be positive'
            assert self._state in [
                STATE_STOPPED,
                STATE_TO_STOP,
                STATE_FINISHED
            ], "can't continue from state: {} (task: {})".format(
                self._state,
                self
            )
            assert self._thread_start is None, "starting is already in progress"
            assert self._thread_cont is None, "continuation is already in progress"
        except Exception as exc:
            self._root._exc.put(exc)
            self._root._lock.release()
            raise
        if self._state == STATE_FINISHED:
            self._lock.release()
            return self
        if gap is None:
            self._thread_cont = threading.Thread(target=self._cont2)
        else:
            self._thread_cont = threading.Thread(
                target=self._cont2,
                kwargs={"time_cont": time.time() + gap}
            )
        self._thread_cont.start()
        return self

    def _cont2(self, time_cont: float=None, time_delta: float=None) -> None:
        if self._state == STATE_STOPPED:
            self._state = STATE_TO_CONTINUE
        elif self._state == STATE_TO_STOP:
            self._lock.release()
            self._thread.join()
            self._exc.fire()
            self._lock.acquire()
        if not threading.current_thread() is self._thread_cont:
            self._lock.release()
            return
        if time_cont:
            gap = time_cont - time.time()
            if gap > 0:
                self._activity = ACTIVITY_SLEEP
                self._cond.wait(gap)
                self._activity = ACTIVITY_NONE
                self._exc.fire(self._lock)
                if not threading.current_thread() is self._thread_cont:
                    self._lock.release()
                    return
        if self._restart:
            self._restart = False
            self._actual = self
            self._contained = []
            self._time_action = time.time()
            if self._duration:
                self._time_end = self._time_action + self._duration
            else:
                self._time_end = None
        else:
            if self._action_cont:
                self._action_cont(*self._args_cont, **self._kwargs_cont)
            if not time_cont and not time_delta:
                time_delta = time.time() - self._time_called_stop
            elif not time_delta:
                next_time_action = self.time_action_no_lock
                if next_time_action:
                    time_delta = time.time() - next_time_action
                elif self._time_end:
                    time_delta = time.time() - self._time_called_stop
                else:
                    time_delta = -1
            if self._actual:
                if self._time_action:
                    self._time_action += time_delta
                if self._actual._time_end:
                    self._actual._time_end += time_delta
            elif self._time_end:
                self._time_end += time_delta
        self._state = STATE_STARTED
        self._time_called_stop = None
        self._thread = self._thread_cont
        self._thread_cont = None
        if self._contained:
            for task in self._contained:
                if task._state is STATE_FINISHED:
                    continue
                if not task in self._contained_register or \
                   self._contained_register[task] != self:
                    continue
                task._lock.acquire()
                task._thread_cont = threading.Thread(
                    target=task._cont2,
                    kwargs={'time_cont': time_cont, 'time_delta': time_delta}
                )
                task._thread_cont.start()
            if self._cont_join:
                self._activity = ACTIVITY_JOIN
                self._lock.release()
                self._cont_join.join()
                self._exc.fire()
                self._lock.acquire()
                self._activity = ACTIVITY_NONE
                if self._state != STATE_STARTED:
                    self._final()
                    return
        if self._actual:
            if self._time_action:
                gap = self._time_action - time.time()
                if gap > 0:
                    self._activity = ACTIVITY_SLEEP
                    self._cond.wait(gap)
                    self._activity = ACTIVITY_NONE
                    self._exc.fire(self._lock)
                    if self._state != STATE_STARTED:
                        self._final()
                        return
            self._actual._execute()
        else:
            if self._time_end:
                gap = self._time_end  - time.time()
                if gap > 0:
                    self._activity = ACTIVITY_SLEEP
                    self._cond.wait(gap)
                    self._activity = ACTIVITY_NONE
                    self._exc.fire(self._lock)
                    if self._state != STATE_STARTED:
                        self._final()
                        return
            self._time_end = None
            self._final()

    def _execute(self) -> None:
        while True:
            if self._root._state != STATE_STARTED:
                self._final(outstand=True)
                return
            try:
                gap = self._wrapper()
            except Exception as exc:
                self._exc.put(exc)
                raise
            self._cnt += 1
            if gap == -1 or self._num > 0 and self._cnt >= self._num:
                self._root._time_action = time.time()
                break
            if gap == 0:
                self._root._time_action = time.time()
                continue
            if self._netto_time:
                self._root._time_action = time.time() + gap
                real_gap = gap
            else:
                self._root._time_action += gap
                real_gap = self._root._time_action - time.time()
            if real_gap > 0:
                if self._root._state != STATE_STARTED:
                    self._final(outstand=True)
                    return
                self._root._activity = ACTIVITY_SLEEP
                self._root._cond.wait(real_gap)
                self._root._activity = ACTIVITY_NONE
                self._root._exc.fire(self._root._lock)
        if self._time_end:
            self._root._time_action = self._time_end
            gap = self._root._time_action - time.time()
            if self._root._state == STATE_STARTED and gap > 0:
                self._root._activity = ACTIVITY_SLEEP
                self._root._cond.wait(gap)
                self._root._activity = ACTIVITY_NONE
                self._root._exc.fire(self._root._lock)
            if self._root._state == STATE_STARTED:
                self._time_end = None
            elif not self is self._root:
                self._root._time_end = self._time_end
                self._time_end = None
        else:
            self._root._time_action = time.time()
        if self._next:
            self._root._actual = self._next
            self._next._cnt = 0
            self._root._time_end = None
            if self._next._duration != None:
                self._next._time_end = self._root._time_action + self._next._duration
            self._next._execute()
        else:
            self._final()

    def _wrapper(self) -> int:
        self._wrapper1()
        self._action(*self._args, **self._kwargs)
        self._wrapper2()
        return -1
    
    def _wrapper1(self) -> None:
        if hasattr(self._action, '__self__') and \
           isinstance(self._action.__self__, Task) and \
           self._action.__name__ in ["start", "cont", "join"]:
            task = self._action.__self__
            name = self._action.__name__
            if (self._join or name is "join"):
                self._root._cont_join = task
            if name in ["start", "cont"]:
                if not task in self._root._contained:
                    self._root._contained.append(task)
                self._contained_register.update({task: self._root})
        if not hasattr(self._action, '__self__') or \
           not isinstance(self._action.__self__, Task) or \
           not self._action.__name__ in ["start", "cont"] or \
           self._action.__name__ == "start" and self._join:
            self._root._activity = ACTIVITY_BUSY
            self._root._lock.release()
            self._root._exc.fire()

    def _wrapper2(self) -> None:
        if self._join:
            self._action.__self__._thread.join()
        if not hasattr(self._action, '__self__') or \
           not isinstance(self._action.__self__, Task) or \
           not self._action.__name__ in ["start", "cont"] or \
           self._action.__name__ == "start" and self._join:
            self._root._exc.fire()
            self._root._lock.acquire()
            self._root._activity = ACTIVITY_NONE
        if hasattr(self._action, '__self__') and \
           isinstance(self._action.__self__, Task) and \
           self._action.__name__ in ["start", "stop", "cont", "join"]:
            task = self._action.__self__
            name = self._action.__name__
            state = task.state
            if self._root._cont_join and \
               (self._root._state == STATE_STARTED or \
                state == STATE_FINISHED):
                self._root._cont_join = None
            if (state == STATE_FINISHED or name == "stop") and \
               task in self._root._contained:
                self._root._contained.remove(task)
            if name == "stop" and \
               task in self._contained_register:
                self._contained_register.pop(task)

    def _final(self, outstand=False) -> None:
        self._root._contained = self._join_contained()
        if self._root._state == STATE_STARTED:
            self._root._state = STATE_FINISHED
        elif self._root._state == STATE_TO_STOP:
            if not self._next and \
               not self._root._contained and \
               not self._root._time_end and \
               not outstand:
                self._root._state = STATE_FINISHED
            elif self._root._action_stop:
                self._root._action_stop(
                    *self._root._args_stop,
                    **self._root._kwargs_stop
                )
        if self._root._state == STATE_FINISHED:
            if self._root in self._contained_register:
                self._contained_register.pop(self._root)
            self._root._thread_cont = None
            self._root._actual = None
            self._root._time_action = None
        else:
            if not self._next and not outstand:
                self._root._actual = None
                self._root._time_action = None
            if self._root._thread_start:
                self._root._actual = None
                self._root._time_action = None
                self._root._state = STATE_TO_START
            elif self._root._thread_cont:
                self._root._state = STATE_TO_CONTINUE
            else:
                self._root._state = STATE_STOPPED
        if self._root._time_action and self._root._time_action < time.time():
            self._root._time_action = None
        self._root._lock.release()

    def _join_contained(self) -> list:
        contained = self._root._contained
        self._root._activity = ACTIVITY_JOIN
        self._root._lock.release()
        not_finished = []
        for task in contained:
            if not task in self._contained_register or \
               not self._contained_register[task] is self._root:
                continue
            task.join()
            if task.state != STATE_FINISHED:
                not_finished.append(task)
        self._root._exc.fire()
        self._root._lock.acquire()
        self._root._activity = ACTIVITY_NONE
        return not_finished

    @property
    def lock(self) -> threading.Lock:
        """
        the tasks lock
        """
        try:
            assert self._root is self, "only root tasks can be asked about their lock"
        except Exception as exc:
            self._root._exc.put(exc)
            raise
        self._exc.fire()
        return self._lock

    @property
    def state(self, lock: bool=True) -> str:
        """
        actual state of the task (or chain of tasks)
        """
        with self._lock:
            value = self.state_no_lock
        return value

    @property
    def state_no_lock(self) -> str:
        """
        actual state of the task (or chain of tasks)
        """
        try:
            assert self._root is self, "only root tasks can be asked about their state"
        except Exception as exc:
            self._root._exc.put(exc)
            raise
        self._exc.fire()
        return self._state

    @property
    def root(self):
        """
        root task of the chain
            a root task returns itself
        """
        self._exc.fire()
        return self._root
    @root.setter
    def root(self, task):
        try:
            assert isinstance(task, Task), 'root needs to be a Task'
            assert task._state in [
                STATE_INIT,
                STATE_STOPPED,
                STATE_FINISHED
            ], 'task is actually executed'
        except Exception as exc:
            self._root._exc.put(exc)
            raise
        self._exc.fire()
        self._root = task
        if self._next:
            self._next.root = task

    @property
    def time_action(self) -> float:
        """
        time of actual (activity is ACTIVITY_BUSY) or next action 
        is in the format of time.time()
        """
        self._exc.fire()
        self._root._lock.acquire()
        try:
            assert self._root is self, 'only root tasks can be asked about their time_action'
        except Exception as exc:
            self._root._exc.put(exc)
            self._root._lock.release()
            raise
        value = self.time_action_no_lock
        self._root._lock.release()
        return value

    @property
    def time_action_no_lock(self) -> float:
        """
        time of actual (activity is ACTIVITY_BUSY) or next action 
        is in the format of time.time()
        """
        min = self._time_action
        for task in self._contained:
            if not task in self._contained_register or \
               self._contained_register[task] != self:
                continue
            act = task.time_action
            if min is None or \
               act != None and act < min:
                min = act
        return min

    @property
    def activity(self) -> str:
        """
        actual activity
        """
        self._exc.fire()
        self._root._lock.acquire()
        try:
            assert self._root is self, 'only root tasks can be asked about their activity'
        except Exception as exc:
            self._root._exc.put(exc)
            self._root._lock.release()
            raise
        value = self.activity_no_lock
        self._root._lock.release()
        return value

    @property
    def activity_no_lock(self) -> str:
        """
        actual activity
        """
        return self._activity

    @property
    def exc(self) -> ExceptionHandler:
        """
        Exception object
        """
        try:
            assert self._root is self, 'only root tasks can be asked'
        except Exception as exc:
            self._root._exc.put(exc)
            raise
        self._exc.fire()
        return self._exc

    @property
    def action_stop(self):
        """
        callable, which is called in case of stopping the task
        """
        self._exc.fire()
        return self._action_stop
    @action_stop.setter
    def action_stop(self, value: typing.Callable):
        self._root._lock.acquire()
        try:
            assert value is None or isinstance(value, typing.Callable), 'action_stop needs to be None or a callable'
            assert self._state in [
                STATE_INIT,
                STATE_STOPPED,
                STATE_FINISHED
            ], 'task is actually executed'
        except Exception as exc:
            self._root._exc.put(exc)
            self._root._lock.release()
            raise
        self._exc.fire()
        self._action_stop = value
        self._root._lock.release()

    @property
    def action_cont(self):
        """
        callable, which is called in case of continuing the task
        """
        try:
            assert self._root is self, 'only root tasks can be asked about their action_cont'
        except Exception as exc:
            self._root._exc.put(exc)
            raise
        self._exc.fire()
        return self._action_cont
    @action_cont.setter
    def action_cont(self, value: typing.Callable):
        self._root._lock.acquire()
        try:
            assert value is None or isinstance(value, typing.Callable), 'action_cont needs to be None or a callable'
            assert self._state in [
                STATE_INIT,
                STATE_STOPPED,
                STATE_FINISHED
            ], 'task is actually executed'
        except Exception as exc:
            self._root._exc.put(exc)
            self._root._lock.release()
            raise
        self._exc.fire()
        self._action_cont = value
        self._root._lock.release()

    @property
    def args_stop(self):
        """
        arguments of action_stop, which is called in case of stopping the task
        """
        self._exc.fire()
        return self._args_stop
    @args_stop.setter
    def args_stop(self, value: tuple):
        self._root._lock.acquire()
        try:
            assert isinstance(value, tuple), 'args_stop needs to be a tuple'
            assert self._root._state in [
                STATE_INIT,
                STATE_STOPPED,
                STATE_FINISHED
            ], 'task is actually executed'
        except Exception as exc:
            self._root._exc.put(exc)
            self._root._lock.release()
            raise
        self._exc.fire()
        self._args_stop = value
        self._root._lock.release()

    @property
    def args_cont(self):
        """
        arguments of action_cont, which is called in case of continuing the task
        """
        self._exc.fire()
        return self._args_cont
    @args_cont.setter
    def args_cont(self, value: tuple):
        self._root._lock.acquire()
        try:
            assert isinstance(value, tuple), 'args_cont needs to be a tuple'
            assert self._root._state in [
                STATE_INIT,
                STATE_STOPPED,
                STATE_FINISHED
            ], 'task is actually executed'
        except Exception as exc:
            self._root._exc.put(exc)
            self._root._lock.release()
            raise
        self._exc.fire()
        self._args_cont = value
        self._root._lock.release()

    @property
    def kwargs_stop(self):
        """
        keyword arguments of action_stop, which is called in case of stopping the task
        """
        self._exc.fire()
        return self._kwargs_stop
    @kwargs_stop.setter
    def kwargs_stop(self, value: dict):
        self._root._lock.acquire()
        try:
            assert isinstance(value, dict), 'kwargs_stop needs to be a dictionary'
            assert self._root._state in [
                STATE_INIT,
                STATE_STOPPED,
                STATE_FINISHED
            ], 'task is actually executed'
        except Exception as exc:
            self._root._exc.put(exc)
            self._root._lock.release()
            raise
        self._exc.fire()
        self._kwargs_stop = value
        self._root._lock.release()

    @property
    def kwargs_cont(self):
        """
        keyword arguments of action_cont, which is called in case of continuing the task
        """
        self._exc.fire()
        return self._kwargs_cont
    @kwargs_cont.setter
    def kwargs_cont(self, value: dict):
        self._root._lock.acquire()
        try:
            assert isinstance(value, dict), 'kwargs_cont needs to be a dictionary'
            assert self._root._state in [
                STATE_INIT,
                STATE_STOPPED,
                STATE_FINISHED
            ], 'task is actually executed'
        except Exception as exc:
            self._root._exc.put(exc)
            self._root._lock.release()
            raise
        self._exc.fire()
        self._kwargs_cont = value
        self._root._lock.release()

    @property
    def exc_default(self):
        """
        default exception
        """
        return self._exc_default

class Periodic(Task):
    """
    Uses multithreading for periodic actions (control comes back immediately).
    think of task as:
        while not action(*args, **kwargs):
            time.sleep(intervall)
    """
    def __init__(self, intervall: float, action: typing.Callable, **kwargs):
        """
        Construct a new 'Periodic' object

        Arguments:
        intervall: intervall between two calls of action (in seconds)
        action: object, which is repeatedly called (f.i. a function)
                Must return a bool or None:
                True: ends the loop
                False, None: next call will follow (if not reached limit of num)
                (method start of a Task object returns the Task object)

        Keyword Arguments:
        args: tuple=() -- argument list of action
        kwargs: dict={} -- keyword arguments of action
        action_stop: typing.Callable=None -- object (f.i. a function), which is called when task is stopped.
        args_stop: tuple=() -- argument list of action_stop
        kwargs_stop: dict={} -- keyword arguments of action_stop
        action_cont: typing.Callable=None -- object (f.i. a function), which is called when task is continued.
        args_cont: tuple=() -- argument list of action_cont
        kwargs_cont: dict={} -- keyword arguments of action_cont
        duration: float=None -- duration of task (if action returns earlier, task will wait)
        netto_time: bool=False -- flag, that waiting is netto (execution of action counts extra)
        exc: ExceptionHandler=None -- exception handler to coordinate exceptions

        example:
        def do_something():
            print("inside")
        task.Periodic(1, do_something, num=3).start()
        """
        self._intervall = intervall
        self._netto_time = kwargs.pop('netto_time', False)
        assert not 'join' in kwargs, \
            "no keyword argument 'join' for instances of class Periodic"
        if hasattr(action, '__self__') and \
           isinstance(action.__self__, Task) and \
           action.__name__ == "start":
            kwargs.update({'join': True})
        else:
            kwargs.update({'join': False})
        super().__init__(action, **kwargs)
        assert isinstance(self._intervall, numbers.Number), \
            'intervall must be a number' + intervall
        assert self._intervall >= 0, 'intervall must be positive'
        assert isinstance(self._netto_time, bool), \
            'netto_time must be a bool value'

    def _wrapper(self):
        self._wrapper1()
        value = self._action(*self._args, **self._kwargs)
        assert isinstance(value, Task) or isinstance(value, bool) or value is None, \
            'action needs to return a Task, a boolean or None'
        if value is True:
            rc = -1
        else:
            rc = self._intervall
        self._wrapper2()
        return rc

class Repeated(Task):
    """
    Organizes repeated actions with multithreading (control comes back immediately).
    think of task as:
        while True:
            gap = action(*args, **kwargs)
            if gap is False or gap is None:
                pass
            elif gap is True or gap == -1:
                break
            else:
                time.sleep(gap)
    """
    def __init__(self, action: typing.Callable, **kwargs):
        """
        Construct a new 'Repeated' object

        Arguments:
        action: callable object, which is repeatedly called (f.i. a function)
                Must return a number, a bool or None:
                True, -1: end the loop
                False, None: next call directly follows (if not reached limit of num)
                positive number: time gap between the actual and the next call
                (method start of a Task object returns a Task object)

        Keyword Arguments:
        args: tuple=() -- argument list of action
        kwargs: dict={} -- keyword arguments of action
        action_stop: typing.Callable=None -- object (f.i. a function), which is called when task is stopped.
        args_stop: tuple=() -- argument list of action_stop
        kwargs_stop: dict={} -- keyword arguments of action_stop
        action_cont: typing.Callable=None -- object (f.i. a function), which is called when task is continued.
        args_cont: tuple=() -- argument list of action_cont
        kwargs_cont: dict={} -- keyword arguments of action_cont
        duration: float=None -- duration of task (if action returns earlier, task will wait)
        netto_time: bool=False -- flag, that waiting is netto (execution of action counts extra)
        exc: ExceptionHandler=None -- exception handler to coordinate exceptions

        example:
        def do_something():
            print("sleep for a sec.")
            time.sleep(1)
        task.Repeated(do_something, num=3).start()
        """
        self._netto_time = kwargs.pop('netto_time', False)
        assert not 'join' in kwargs, \
            "no keyword argument 'join' for instances of class Periodic"
        if hasattr(action, '__self__') and \
           isinstance(action.__self__, Task) and \
           action.__name__ == "start":
            kwargs.update({'join': True})
        else:
            kwargs.update({'join': False})
        super().__init__(action, **kwargs)
        assert isinstance(self._netto_time, bool), \
            'netto_time must be a bool value'

    def _wrapper(self):
        self._wrapper1()
        value = self._action(*self._args, **self._kwargs)
        assert isinstance(value, Task) or \
            isinstance(value, numbers.Number) or \
            isinstance(value, bool) or \
            value is None, \
            'action needs to return a number, a boolean or None'
        assert not isinstance(value, numbers.Number) or \
            value == -1 or \
            value >= 0, \
            'if action returns a number, it must be positive or -1 ' + str(value)
        if value is True:
            rc = -1
        elif isinstance(value, Task) or value is False or value is None:
            rc = 0
        else:
            rc = value
        self._wrapper2()
        return rc

class Sleep(Task):
    """
    Sleeps and can be stopped
    """
    def __init__(self, seconds: float, exc: ExceptionHandler=None):
        """
        Construct a new 'Sleep' object

        Arguments:
        seconds: duration of sleeping

        Keyword Arguments:
        exc: ExceptionHandler=None -- exception handler to coordinate exceptions
        """
        if not exc:
            exc = self._exc_default
        super().__init__(self._do_nothing, duration=seconds, exc=exc)

    def _do_nothing(self): return -1

if __name__ == "__main__":
    def creative(txt: str):
        now = datetime.datetime.now().strftime('%H:%M:%S.%f')
        print(now, "creative: start")
        time.sleep(1)
        now = datetime.datetime.now().strftime('%H:%M:%S.%f')
        print(now, "creative:", txt)

    def gimmick(txt: str="wow"):
        now = datetime.datetime.now().strftime('%H:%M:%S.%f')
        print(now, "gimmick: start")
        time.sleep(3)
        now = datetime.datetime.now().strftime('%H:%M:%S.%f')
        print(now, "gimmick:",  txt)

    def administration():
        now = datetime.datetime.now().strftime('%H:%M:%S.%f')
        print(now, "administration: start")
        time.sleep(5)
        now = datetime.datetime.now().strftime('%H:%M:%S.%f')
        print(now, "administration: task and me, both done")

    t1 = Task(
        creative,
        args=("heureka!",)
    )
    t2 = Task(
        gimmick,
        kwargs={"txt": "my great application"}
    )
    t3 = Task(
        administration
    )

    concat(
        Task(t1.start),
        Task(t2.start),
        Task(t3.start)
    ).start().join()
    print("*** done (parallel) ***")

    t = concat(
        t1,
        Sleep(3),
        t2,
        Sleep(3),
        t3
    )
    t.start().join()
    print("*** done (sequential) ***")

    t.start()
    time.sleep(5)
    t.stop()
    print("*** stopped ***")
    time.sleep(5)
    t.cont()
    print("*** continued ***")
    t.join()
    print("*** done (after continuing) ***")

    Repeated(t.start, num=2).start().join()
    print("*** done (two times) ***")
    
    
