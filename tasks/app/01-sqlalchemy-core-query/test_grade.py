import pytest
from sqlalchemy import create_engine

from pgtrain_grader import get_attr, load_module, sqlalchemy_url


@pytest.fixture()
def engine():
    eng = create_engine(sqlalchemy_url("psycopg"))
    yield eng
    eng.dispose()


def test_revenue_by_region(engine):
    fn = get_attr(load_module(), "revenue_by_region")
    result = fn(engine)
    assert result is not None, "revenue_by_region returned None"
    normalized = [(region, float(total)) for region, total in result]
    assert normalized == [("east", 200.0), ("north", 135.0), ("south", 125.0)]
