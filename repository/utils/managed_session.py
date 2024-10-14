import logging
from contextlib import contextmanager


@contextmanager
def managed_session(session_factory):
    session = session_factory()
    try:
        yield session
    except Exception as e:
        session.rollback()
        logging.error("Session rollback due to exception: %s", e)
        raise
    finally:
        session.close()
