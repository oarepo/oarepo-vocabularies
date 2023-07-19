def test_authority_resource(client, affiliations_pids, mock_auth_getter_affilliations, search_clear):
    # Arrange.
    internal_uuid = "{12345678-1234-5678-1234-567812345678}"
    affiliations_pids(internal_uuid)
    
    # Act.
    params = "q=affiliation&page=1&size=2"
    resp = client.get(f'/api/vocabularies/affiliations/authoritative?{params}').json
    
    # Assert.
    results = resp['hits']['hits']
    mock_auth_getter_affilliations.assert_called_once()
    
    external_result = [res for res in results if res["props"]["external"]]
    assert len(external_result) == 1
    assert not hasattr(external_result[0]["props"], "uuid")
    
    internal_result = [res for res in results if not res["props"]["external"]]
    assert len(internal_result) == 1
    assert internal_result[0]["props"]["uuid"] == internal_uuid[1:-1]