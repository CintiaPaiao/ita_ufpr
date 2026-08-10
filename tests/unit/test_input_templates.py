from io import BytesIO
from zipfile import ZipFile
import pandas as pd

from src.config.base_registry import list_base_types, get_base_spec
from src.exports.input_templates import build_base_template, build_criteria_workbook_template, build_all_templates_zip
from src.services.import_service import preview_import

def test_every_registered_base_has_downloadable_template():
    for base_type, _ in list_base_types():
        raw = build_base_template(base_type)
        xls = pd.ExcelFile(BytesIO(raw))
        assert {"MODELO","DICIONARIO","INSTRUCOES"}.issubset(set(xls.sheet_names))

def test_every_base_template_is_recognized_by_current_importer():
    for base_type, _ in list_base_types():
        raw = build_base_template(base_type)
        _, _, validation = preview_import(
            filename=f"{base_type}.xlsx",
            raw=raw,
            base_type=base_type,
            sheet_name="MODELO",
        )
        assert validation.valid, f"{base_type}: {validation.errors}"

def test_criteria_workbook_has_expected_sectors():
    raw = build_criteria_workbook_template()
    sheets = set(pd.ExcelFile(BytesIO(raw)).sheet_names)
    assert {"Serviço Social","Psicologia","Pedagogia","CAISE","CPPOVOS","CATRIM","PROAFE-CAS"}.issubset(sheets)

def test_all_templates_zip_contains_all_base_types():
    raw = build_all_templates_zip()
    with ZipFile(BytesIO(raw)) as z:
        names = set(z.namelist())
    for base_type, _ in list_base_types():
        assert f"{base_type}__modelo.xlsx" in names
