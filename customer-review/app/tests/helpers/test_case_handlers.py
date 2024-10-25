from copy import deepcopy

import numpy as np
import pytest

from app.tests.helpers.case_handlers import compare_outputs_and_expected_outputs

_DEFAULT_OUTPUTS = {"a": 1, "b": "foo", "c": [1, 2], "d": {"da": 1, "db": "foo"}}


def test_compare_outputs_and_expected_outputs():
    compare_outputs_and_expected_outputs(
        outputs=_DEFAULT_OUTPUTS,
        expected_outputs=_DEFAULT_OUTPUTS,
        compare_only_keys_in_expected_outputs=False,
    )

    expected_outputs_with_one_modified_value = _DEFAULT_OUTPUTS.copy()
    expected_outputs_with_one_modified_value["a"] = 9999
    with pytest.raises(AssertionError):
        compare_outputs_and_expected_outputs(
            outputs=_DEFAULT_OUTPUTS,
            expected_outputs=expected_outputs_with_one_modified_value,
            compare_only_keys_in_expected_outputs=True,
            ignore_keys_order=False,
        )

    expected_outputs_with_one_modified_value_on_decimals = _DEFAULT_OUTPUTS.copy()
    significant_digits_to_test = 3
    expected_outputs_with_one_modified_value_on_decimals["a"] = _DEFAULT_OUTPUTS[
        "a"
    ] + 1 * 10 ** (-significant_digits_to_test)
    with pytest.raises(AssertionError):
        compare_outputs_and_expected_outputs(
            outputs=_DEFAULT_OUTPUTS,
            expected_outputs=expected_outputs_with_one_modified_value_on_decimals,
            compare_only_keys_in_expected_outputs=True,
            ignore_keys_order=False,
            significant_digits=significant_digits_to_test,
        )

    compare_outputs_and_expected_outputs(
        outputs=_DEFAULT_OUTPUTS,
        expected_outputs=expected_outputs_with_one_modified_value_on_decimals,
        compare_only_keys_in_expected_outputs=True,
        ignore_keys_order=False,
        significant_digits=significant_digits_to_test - 1,
    ), "problem with expected_outputs_with_one_modified_value_on_decimals"

    with pytest.raises(AssertionError):
        expected_outputs_with_one_added_key = _DEFAULT_OUTPUTS.copy()
        expected_outputs_with_one_added_key["new_key"] = 1
        compare_outputs_and_expected_outputs(
            outputs=_DEFAULT_OUTPUTS,
            expected_outputs=expected_outputs_with_one_added_key,
            compare_only_keys_in_expected_outputs=True,
            ignore_keys_order=False,
        )

    expected_outputs_with_only_one_key = {
        key: value
        for key, value in _DEFAULT_OUTPUTS.items()
        if key == list(_DEFAULT_OUTPUTS.keys())[0]
    }
    compare_outputs_and_expected_outputs(
        outputs=_DEFAULT_OUTPUTS,
        expected_outputs=expected_outputs_with_only_one_key,
        compare_only_keys_in_expected_outputs=True,
    ), "problem with outputs_with_one_missing_key"

    outputs_with_one_missing_key = expected_outputs_with_only_one_key
    with pytest.raises(AssertionError):
        compare_outputs_and_expected_outputs(
            outputs=outputs_with_one_missing_key,
            expected_outputs=_DEFAULT_OUTPUTS,
            compare_only_keys_in_expected_outputs=True,
        )

    outputs_with_keys_set_to_null = deepcopy(_DEFAULT_OUTPUTS)
    outputs_with_keys_set_to_null["a"] = None
    outputs_with_keys_set_to_null["b"] = np.nan
    with pytest.raises(AssertionError):
        compare_outputs_and_expected_outputs(
            outputs=outputs_with_keys_set_to_null,
            expected_outputs=_DEFAULT_OUTPUTS,
            compare_only_keys_in_expected_outputs=True,
        )


if __name__ == "__main__":
    test_compare_outputs_and_expected_outputs()
