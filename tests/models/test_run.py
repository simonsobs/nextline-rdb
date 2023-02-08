import datetime

from sqlalchemy import select

from nextline_rdb import DB
from nextline_rdb.models import Run


def test_one():
    db = DB()
    run_no = 1
    with db.session() as session:
        model = Run(
            run_no=run_no,
            state="running",
            started_at=datetime.datetime.utcnow(),
            ended_at=datetime.datetime.utcnow(),
            script="pass",
        )
        session.add(model)
        session.commit()
        assert model.id

    with db.session() as session:
        stmt = select(Run).filter_by(run_no=run_no)
        model = session.execute(stmt).scalar_one()
