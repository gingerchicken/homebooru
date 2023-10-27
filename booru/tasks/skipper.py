from functools import wraps

# Nicked from https://stackoverflow.com/a/35197449/8736749

def skip_if_running(f):
    task_name = f'{f.__module__}.{f.__name__}'

    @wraps(f)
    def wrapped(self, *args, **kwargs):
        workers = self.app.control.inspect().active()

        for worker, tasks in workers.items():
            for task in tasks:
                if (task_name == task['name'] and
                        tuple(args) == tuple(task['args']) and
                        kwargs == task['kwargs'] and
                        self.request.id != task['id']):
                    print(f'task {task_name} ({args}, {kwargs}) is running on {worker}, skipping')

                    return None

        return f(self, *args, **kwargs)

    return wrapped