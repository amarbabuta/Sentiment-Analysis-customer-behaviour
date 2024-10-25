import json

import pandas as pd
from deepdiff import DeepDiff
from pydantic import BaseModel


def get_inputs_and_expected_outputs(
    inputs_and_expected_results_file_path: str,
) -> [dict, dict]:
    with open(inputs_and_expected_results_file_path) as json_file:
        data = json.load(json_file)

    return data["inputs"], data["expected_outputs"]


def _dump_pydantic_basemodel_as_json(obj: BaseModel, output_file_path: str) -> None:
    with open(output_file_path, "w") as output_file:
        s1 = json.dumps(obj.dict(), default=str)
        s2 = json.loads(s1)
        json.dump(s2, output_file)


def compare_outputs_and_expected_outputs(
    outputs: dict,
    expected_outputs: dict,
    compare_only_keys_in_expected_outputs: bool = False,
    ignore_keys_order: bool = True,
    significant_digits: int = 8,
) -> None:
    diff = DeepDiff(
        outputs,
        expected_outputs,
        ignore_order=ignore_keys_order,
        significant_digits=significant_digits,
        ignore_numeric_type_changes=True,
    )

    if compare_only_keys_in_expected_outputs is False:
        assert not diff, "diff : " + diff.__str__()
    else:
        diff_on_keys_in_expected_outputs = diff.get("values_changed", {})
        assert not diff_on_keys_in_expected_outputs, (
            "please check the following differences between "
            "expected_outputs ('new_value') "
            "and outputs produced by code ('old_value') : "
            + diff_on_keys_in_expected_outputs.__str__()
        )

        types_changes = diff.get("type_changes", {})
        diff_on_keys_in_expected_outputs_due_to_nonetype_in_outputs = {
            key: value
            for key, value in types_changes.items()
            if pd.isnull(value["old_value"])
        }
        assert not diff_on_keys_in_expected_outputs_due_to_nonetype_in_outputs, (
            "please check the following differences between"
            " expected_outputs ('new_value') "
            "and outputs produced by code ('old_value') : "
            + diff_on_keys_in_expected_outputs_due_to_nonetype_in_outputs.__str__()
        )

        missing_expected_keys = diff.get("dictionary_item_added", {})
        assert not missing_expected_keys, (
            "please check the missing_expected_keys : "
            + missing_expected_keys.__str__()
        )
