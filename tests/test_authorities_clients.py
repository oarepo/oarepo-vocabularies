
from oarepo_vocabularies.authorities.clients import RORClientV2

def test_authority_ror_client_get(ror_client):
    # Given a ROR id, should resolve both formats to same record.
    test_id_short = '04k0tth05'
    test_id_long = 'https://ror.org/04k0tth05'

    short_result = ror_client.get_record(test_id_short)
    long_result = ror_client.get_record(test_id_long)

    assert short_result == long_result

    display_name = ''.join([name['value'] for name in long_result['names'] if 'ror_display' in name['types']])
    assert display_name == 'Air Force Test Center'

def test_authority_ror_client_search(ror_client):
    # 1. Returns nothing on empty query
    query = ''
    results = ror_client.quick_search({'q': query})
    assert results['number_of_results'] == 0
    assert len(results['items']) == 0

    # 2. Finds a result by its name
    query = 'cesnet'
    cesnet_id = 'https://ror.org/050dkka69'

    results = ror_client.quick_search({'q': query})
    assert results['number_of_results'] >= 1
    assert cesnet_id in [result['id'] for result in results['items']]

    # 3. Returns the requested page if there is more records
    query = 'a'

    results = ror_client.quick_search({'q': query})
    assert results['number_of_results'] > 20
    assert len(results['items']) == 20

    page2_results = ror_client.quick_search({'q': query, 'page': 2})
    assert page2_results['number_of_results'] > 20
    assert len(page2_results['items']) == 20

    for item in results['items']:
        assert item['id'] not in [it['id'] for it in page2_results['items']]
