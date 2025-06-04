import json
import pandas as pd

from app.utils import convert_response_to_string, process_context_data


def test_convert_response_to_string_with_string():
    assert convert_response_to_string("hello") == "hello"


def test_convert_response_to_string_with_dict():
    data = {"name": "Harry", "house": "Gryffindor"}
    assert convert_response_to_string(data) == json.dumps(data)


def test_convert_response_to_string_with_list():
    data = [{"name": "Harry"}, {"name": "Ron"}]
    assert convert_response_to_string(data) == json.dumps(data)


def test_process_context_data_with_string():
    assert process_context_data("context") == "context"


def test_process_context_data_with_list_of_dataframes():
    df1 = pd.DataFrame({"a": [1, 2]})
    df2 = pd.DataFrame({"b": [3, 4]})
    result = process_context_data([df1, df2])
    assert result == [df1.to_dict(orient="records"), df2.to_dict(orient="records")]


def test_process_context_data_with_dict_of_dataframes():
    df1 = pd.DataFrame({"a": [1]})
    df2 = pd.DataFrame({"b": [2]})
    data = {"df1": df1, "df2": df2}
    result = process_context_data(data)
    expected = {"df1": df1.to_dict(orient="records"), "df2": df2.to_dict(orient="records")}
    assert result == expected


def test_process_context_data_with_invalid():
    assert process_context_data(123) is None
