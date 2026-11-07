"""Display the standard-library Riccati solver through the calculator catalog."""

from engine import field, register, latex_for_input
from riccati import solve_autonomous, solve_linear, solve_coupled

TAB = ("ode", "Differential equations", "sigma")


@register(
    *TAB,
    "linear_second_order",
    "Second-order linear ODE",
    "Enter A y″ + B y′ + C y = 0 with rational coefficients in x.",
    [
        field("a", "A(x), coefficient of y″", "(1+x)^2"),
        field("b", "B(x), coefficient of y′", "1+x"),
        field("c", "C(x), coefficient of y", "-2"),
    ],
)
def linear_second_order(values):
    result = solve_linear(values["a"], values["b"], values["c"])
    lines = [result["family"] + " — " + result["status"]]
    if result["basis"]:
        first, second = result["basis"]
        lines.append(f"y = C1*({first}) + C2*({second})")
    lines.extend(
        [
            "dz/dx = " + result["slope_rhs"],
            result["reason"],
            "Coefficient domain: "
            + (", ".join(result["coefficient_guards"]) or "all real x"),
            result["chart"],
            result["recovery"],
        ]
    )
    try:
        if result["basis"]:
            first, second = (latex_for_input(f) for f in result["basis"])
            latex = (
                r"y(x)=C_1\left(" + first + r"\right)+C_2\left(" + second + r"\right)"
            )
        else:
            latex = r"\frac{dz}{dx}=" + latex_for_input(result["slope_rhs"])
    except ValueError:
        latex = ""
    return {"lines": lines, "latex": latex, "extras": result}


@register(
    *TAB,
    "autonomous_riccati",
    "First-order Riccati ODE",
    "Solve dz/dx = a z² + b z + c with rational constants.",
    [field("a", "a", "1"), field("b", "b", "0"), field("c", "c", "1")],
)
def autonomous_riccati(values):
    result = solve_autonomous(values["a"], values["b"], values["c"])
    return {
        "lines": ["z(x) = " + result["solution"], result["domain"], result["licence"]],
        "extras": result,
    }


@register(
    *TAB,
    "coupled_modes",
    "Coupled-coordinate modes",
    "Solve the paper's cone equation after its phase shift, on 1+x > 0.",
    [field("ell", "Fourier index ℓ", "1"), field("m", "Coupling m", "1")],
)
def coupled_modes(values):
    result = solve_coupled(values["ell"], values["m"])
    first, second = result["basis"]
    return {
        "lines": [
            f"y = C1*({first}) + C2*({second})",
            result["domain"],
            result["licence"],
        ],
        "extras": result,
    }
