
from oarepo_vocabularies.authorities.clients import RORClientV2

def test_authority_ror_client(ror_client):
    test_id_short = '04k0tth05'
    test_id_long = 'https://ror.org/04k0tth05'

    short_result = ror_client.get_record(test_id_short)
    long_result = ror_client.get_record(test_id_long)

    assert short_result == long_result

    display_name = ''.join([name['value'] for name in long_result['names'] if 'ror_display' in name['types']])
    assert display_name == 'Air Force Test Center'