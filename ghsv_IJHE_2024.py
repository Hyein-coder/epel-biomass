import math


def ghsv(
    m_dot_nh3: float = 3.45e-5,   # kg/s, NH3 mass flow
    d_tube: float = 0.0,          # m, cracking tube INNER diameter (from paper)
    h_packed: float = 0.0,        # m, packed bed height (from paper)
    cat_frac: float = 0.3,        # catalyst:total = 3:7 -> 30% of tube volume
    M_nh3: float = 0.017,         # kg/mol
    Vm_stp: float = 22.4,         # L/mol at STP (0 C, 1 atm)
) -> float:
    """GHSV [1/h] = feed volumetric flow at STP / bulk catalyst bed volume."""
    v_feed = (m_dot_nh3 / M_nh3) * Vm_stp * 3600.0                        # L/hr at STP
    v_cat = cat_frac * (math.pi * d_tube**2 / 4.0 * h_packed) * 1000.0    # m^3 -> L
    return v_feed / v_cat


if __name__ == "__main__":
    # numerator sanity vs spec: 0.1636 Nm3/hr = 163.6 L/hr
    assert abs((3.45e-5 / 0.017) * 22.4 * 3600 - 163.6) < 0.5
    # Paper IJHE 2024 Cho's
    print(round(ghsv(d_tube=0.05, h_packed=0.575), 1))
