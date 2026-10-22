"""Input-to-output fidelity for the rendered mathematics workspace."""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
from engine import calculate, latex_for_input


def run(operation, **values):
    return calculate({'tab': 'basic', 'operation': operation, 'values': values})


def test_input_fractions_and_powers_keep_original_structure():
    assert latex_for_input('2/4') == r'\frac{2}{4}'
    assert latex_for_input('x^2') == 'x^{2}'
    assert latex_for_input('sqrt(x^2+1)/(2*pi)') == r'\frac{\sqrt{x^{2} + 1}}{2 \cdot \pi}'


def test_input_parentheses_keep_mathematical_meaning():
    assert latex_for_input('(x+1)^2') == r'\left(x + 1\right)^{2}'
    assert latex_for_input('1/(x+1)') == r'\frac{1}{x + 1}'
    assert latex_for_input('x-(y-z)') == r'x - \left(y - z\right)'
    assert latex_for_input('(-x)^2') == r'\left(-x\right)^{2}'


def test_input_matrix_is_typeset_not_left_as_ascii():
    assert latex_for_input('[[1,2],[3,4]]') == r'\begin{bmatrix}1 & 2 \\ 3 & 4\end{bmatrix}'


def test_result_separates_entered_expression_from_simplified_answer():
    result = run('evaluate', expression='2/4')
    assert result['ok'] and result['expr'] == '1/2'
    assert result['inputs'][0]['latex'] == r'\frac{2}{4}'
    assert result['latex'] == r'\frac{1}{2}'
    assert result['reusable'] is True


def test_multi_argument_operations_keep_typeset_input_and_nonreusable_results():
    result = run('solve', expression='x^2-4', variable='x')
    assert result['ok']
    assert result['inputs'][0]['latex'] == 'x^{2} - 4'
    assert result['reusable'] is False


@pytest.mark.parametrize('source', ['x.__class__', '__import__("os")', 'x[0]', '2**1000000'])
def test_cannot_render_disallowed_input(source):
    with pytest.raises(ValueError):
        latex_for_input(source)
