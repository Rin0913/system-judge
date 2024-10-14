from contextlib import contextmanager


@contextmanager
def managed_session(session_factory, logger):
    session = session_factory()
    try:
        yield session
    except Exception as e:
        session.rollback()
        logger.error("Session rollback due to exception: %s", e)
        raise
    finally:
        session.close()
