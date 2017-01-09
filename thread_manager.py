from threading import current_thread


def set(key, value):
    setattr(current_thread, key, value)


def get(key, default=None):
    return getattr(current_thread, key, default)
