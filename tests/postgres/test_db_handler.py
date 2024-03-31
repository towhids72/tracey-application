from sqlalchemy import select

from app.db.models import UserModel
from tests.conftest import postgres, user_model_instance


def test_health_check(postgres):
    result = postgres.health_check()
    assert result is True


def test_create_tables(postgres):
    with postgres.create_session() as session:
        with session.bind.connect() as connection:
            table_names = session.bind.dialect.get_table_names(connection)
            assert table_names == ['users']


def test_user_create(postgres, user_model_instance):
    with postgres.create_session() as session:
        session.add(user_model_instance)
        session.commit()

        query_all = session.execute(select(UserModel)).scalars().all()
        assert len(query_all) == 1


def test_drop_tables(postgres):
    postgres.drop_tables()

    with postgres.create_session() as session:
        with session.bind.connect() as connection:
            table_names = session.bind.dialect.get_table_names(connection)
            assert table_names == []

    postgres.initialize()
