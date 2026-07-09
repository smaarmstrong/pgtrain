from sqlalchemy import MetaData, Table, func, select


def revenue_by_region(engine):
    md = MetaData()
    sales = Table("sales", md, autoload_with=engine)
    total = func.sum(sales.c.amount).label("total")
    stmt = (
        select(sales.c.region, total)
        .group_by(sales.c.region)
        .order_by(total.desc(), sales.c.region.asc())
    )
    with engine.connect() as conn:
        return [tuple(row) for row in conn.execute(stmt)]
