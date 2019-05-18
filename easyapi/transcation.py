class Transaction():

    def __init__(self, db):
        self._db = db
        self._transaction = None
        self._connect = None

    def __enter__(self):
        self._connect = self._db._engine.connect()
        self._transaction = self._connect.begin()
        return self._connect

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None and exc is None and tb is None:
            try:
                self._transaction.commit()
            except Exception as e:
                self._transaction.rollback()
                raise e
            finally:
                self._connect.close()
        else:
            try:
                self._transaction.rollback()
            except Exception as e:
                raise e
            finally:
                self._connect.close()


def get_tx(db):
    return Transaction(db)
