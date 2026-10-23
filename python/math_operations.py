"""Shared symbolic implementations used by legacy tabs AND the typed workspace.

This module knows nothing about form field names, node identifiers, charts or UI.
Callers validate mathematical context and adapt their native symbolic operands.
In particular, results are passed as SymPy objects, never rendered/re-parsed text.
"""
import sympy as sp


def transform(operation, expression, variable, frequency):
    if operation == 'fourier':
        return sp.fourier_transform(expression, variable, frequency)
    if operation == 'inverse_fourier':
        return sp.inverse_fourier_transform(expression, variable, frequency)
    if operation == 'laplace':
        return sp.laplace_transform(expression, variable, frequency, noconds=True)
    if operation == 'inverse_laplace':
        return sp.inverse_laplace_transform(expression, variable, frequency)
    raise ValueError(f'Unsupported transform: {operation}.')


def limit(expression, variable, point, direction='+-'):
    if direction not in ('+', '-', '+-'):
        raise ValueError('Direction must be +, -, or +-.')
    return sp.limit(expression, variable, point, dir=direction)


def series(expression, variable, point, order):
    if type(order) is not int or not 1 <= order <= 18:
        raise ValueError('Series order must be an integer from 1 to 18.')
    return sp.series(expression, variable, point, order)


def matrix_inverse(matrix):
    if matrix.rows != matrix.cols:
        raise ValueError('Matrix inverse requires a square matrix.')
    return matrix.inv()


def matrix_transpose(matrix):
    return matrix.T


def matrix_multiply(left, right):
    if left.cols != right.rows:
        raise ValueError('Matrix multiplication requires compatible dimensions.')
    return left * right
