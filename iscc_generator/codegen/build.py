# -*- coding: utf-8 -*-
"""Build Pydantic models from OpenAPI spec"""
import pathlib
from datamodel_code_generator import (
    InputFileType,
    generate,
    OpenAPIScope,
    PythonVersion,
)

ROOT = pathlib.Path(__file__).parent
CODE = ROOT / "iscc_schema"


def build_spec():
    infile = ROOT / "spec.yaml"
    outfile = ROOT / "spec.py"
    generate(
        infile,
        input_file_type=InputFileType.OpenAPI,
        output=outfile,
        encoding="UTF-8",
        disable_timestamp=True,
        use_schema_description=True,
        openapi_scopes=[OpenAPIScope.Schemas, OpenAPIScope.Paths],
        reuse_model=True,
        disable_appending_item_suffix=True,
        target_python_version=PythonVersion.PY_39,
        field_constraints=True,  # This does not allow format-uri with maxLength constraint
    )

    # Patch BaseModel & AnyUrl
    marker = "from pydantic import AnyUrl, BaseModel, Field\n"
    replace = (
        "from pydantic import Field\n"
        "from iscc_generator.codegen.fields import AnyUrl\n"
        "from iscc_generator.codegen.base import BaseModel\n"
    )
    with outfile.open("rt", encoding="utf-8") as infile:
        text = infile.read()
        text = text.replace(marker, replace)
    with outfile.open("wt", encoding="utf-8", newline="\n") as patched:
        patched.write(text)


if __name__ == "__main__":
    build_spec()
