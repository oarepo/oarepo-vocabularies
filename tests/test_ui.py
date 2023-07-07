def test_whatever(
    app,
    client,
    db,
    identity,
    vocab_cf,
    lang_data_many,
    empty_licences,
    search_clear,
):
    resp = client.get('/vocabularies/').text
    
    assert 'Hello, world!' in resp
