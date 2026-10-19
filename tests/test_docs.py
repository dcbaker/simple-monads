from pathlib import Path

import pytest
from pytest_examples import CodeExample, EvalExample, find_examples


@pytest.mark.parametrize('example', list(find_examples('README.md')))
def test_readme_examples(example: CodeExample, eval_example: EvalExample) -> None:
    if eval_example.update_examples:
        eval_example.format(example)
        eval_example.run_print_update(example)
    else:
        eval_example.lint(example)
        eval_example.run_print_check(example)
