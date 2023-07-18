from invenio_pidstore.models import PersistentIdentifier

def test_sqlalchemy(app, db):
    # Arrange
    pid1 = PersistentIdentifier.create(
        pid_type="authvc",
        pid_value="1"
    )
    
    pid2 = PersistentIdentifier.create(
        pid_type="authvc",
        pid_value="2"
    )
    
    db.session.add(pid1)
    db.session.add(pid2)
    db.session.commit()
    
    # Act    
    subquery = db.session.query(
        PersistentIdentifier.pid_type,
        PersistentIdentifier.pid_value
    ).subquery('sub')

    query = db.session.query(
        PersistentIdentifier.object_uuid,
        PersistentIdentifier.pid_type,
        PersistentIdentifier.pid_value
    ).join(
        subquery,
        db.and_(
            PersistentIdentifier.pid_type == subquery.c.pid_type,
            PersistentIdentifier.pid_value == subquery.c.pid_value
        )
    ).all()

    results = [(row.object_uuid, row.pid_type, row.pid_value) for row in query]
    
    print(results)