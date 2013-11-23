import time
import cProfile


def timefunc(f):
    def f_timer(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        print f.__name__, 'took', end - start, 'time'
        return result
    return f_timer


class timewith():
    def __init__(self, name=''):
        self.name = name
        self.start = time.time()

    @property
    def elapsed(self):
        return time.time() - self.start

    def checkpoint(self, name=''):
        print '{timer} {checkpoint} took {elapsed} seconds'.format(
            timer=self.name,
            checkpoint=name,
            elapsed=self.elapsed,
        ).strip()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.checkpoint('finished')
        pass

def do_cprofile(func):
    def profiled_func(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            return result
        finally:
            profile.print_stats()
    return profiled_func

try:
    from line_profiler import LineProfiler

    def do_profile(follow=[]):
        """
        Simply decorate an expensive function and optionally
        pass other functions to follow. For example:

            def get_number():
                for x in xrange(5000000):
                    yield x

            @do_profile(follow=[get_number])
            def expensive_function():
                for x in get_number(5000000):
                    i = x ^ x ^ x
                return 'some result!'

        """
        def inner(func):
            def profiled_func(*args, **kwargs):
                try:
                    profiler = LineProfiler()
                    profiler.add_function(func)
                    for f in follow:
                        profiler.add_function(f)
                    profiler.enable_by_count()
                    return func(*args, **kwargs)
                finally:
                    profiler.print_stats()
            return profiled_func
        return inner

except ImportError:
    def do_profile(follow=[]):
        "Helpful if you accidentally leave in production!"
        def inner(func):
            def nothing(*args, **kwargs):
                return func(*args, **kwargs)
            return nothing
        return inner

def get_number():
    for x in xrange(5000000):
        yield x

def expensive_function():
    for x in get_number():
        i = x ^ x ^ x
    return 'some result!'


if __name__ == '__main__':
    # the same as...
    # @timefunc
    # def expensive_function(): ...
    result = timefunc(expensive_function)()

    # as a context manager
    with timewith('fancy thing') as timer:
        expensive_function()
        timer.checkpoint('done with something')
        expensive_function()
        expensive_function()
        timer.checkpoint('done with something else')

    # or directly
    timer = timewith('fancy thing')
    expensive_function()
    timer.checkpoint('done with something')

    # built in profiler
    result = do_cprofile(expensive_function)()

    # prints a nice output of line-by-line execution times
    result = do_profile(follow=[get_number])(expensive_function)()
