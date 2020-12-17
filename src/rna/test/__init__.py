from modules import Base


def init_db(engine):
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from modules.users.model import User
    Base.metadata.create_all(bind=engine)
