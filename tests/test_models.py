from iscc_generator import models


def test_Iscc_code_get_metadata():
    obj = models.IsccCode()
    assert obj.get_metadata() == {}
    obj = models.IsccCode(source_url="http://example.com/file.txt")
    assert obj.get_metadata() == {}
    obj = models.IsccCode(name="Some asset name")
    assert obj.get_metadata() == {"name": "Some asset name"}
