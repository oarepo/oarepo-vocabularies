import pytest
from werkzeug.exceptions import BadRequest


def test_authority_ror_client_get(ror_client):
    # 1. Given a ROR id, should resolve both formats to same record.
    test_id_short = "04ttjf776"
    test_id_long = "https://ror.org/04ttjf776"

    short_result = ror_client.get_record(test_id_short)
    long_result = ror_client.get_record(test_id_long)

    assert short_result == long_result

    display_name = "".join(
        [
            name["value"]
            for name in long_result["names"]
            if "ror_display" in name["types"]
        ]
    )
    assert display_name == "RMIT University"

    # 2. Returns none for non-existent ROR ID
    bad_id = "l33tr0r1d"
    with pytest.raises(BadRequest):
        ror_client.get_record(bad_id) is None


def test_authority_ror_client_search(ror_client):
    # 1. Returns nothing on empty query
    query = ""
    results = ror_client.quick_search(query=query)
    assert results["number_of_results"] == 0
    assert len(results["items"]) == 0

    # 2. Finds a result by its name
    query = "RMIT"
    result_id = "https://ror.org/04ttjf776"

    results = ror_client.quick_search(query=query)
    assert results["number_of_results"] >= 1
    assert result_id in [result["id"] for result in results["items"]]

    # 3. Returns the requested page if there is more records
    query = "a"

    results = ror_client.quick_search(query=query)
    assert results["number_of_results"] > 1
