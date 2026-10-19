"""Coordinate-basis differential geometry, R^a_{bcd} = d_c Γ^a_{db} - d_d Γ^a_{cb} + ΓΓ - ΓΓ."""
import sympy as sp
from engine import register,field,metric_data,math_symbol,math_int,parse_math
TAB=('geometry','Differential geometry','globe')
def reg(op,label,desc,fields):return register(*TAB,op,label,desc,fields)
C=field('coordinates','Coordinates (comma-separated)','r,theta')
M=field('metric','Metric g_ij','[[1,0],[0,r^2]]',kind='textarea',hint='Up to 4 dimensions; symbolic curvature can be computationally expensive.')
BASE=[C,M]

def geometry(v):
    coords,g=metric_data(v)
    n=len(coords); inv=g.inv().applyfunc(sp.simplify)
    gamma=[[[sp.simplify(sp.Rational(1,2)*sum(inv[a,l]*(sp.diff(g[l,c],coords[b])+sp.diff(g[l,b],coords[c])-sp.diff(g[b,c],coords[l])) for l in range(n))) for c in range(n)] for b in range(n)] for a in range(n)]
    return coords,g,inv,gamma

def curvature(gamma,coords):
    n=len(coords)
    return [[[[sp.simplify(sp.diff(gamma[a][d][b],coords[c])-sp.diff(gamma[a][c][b],coords[d])+
             sum(gamma[a][c][m]*gamma[m][d][b]-gamma[a][d][m]*gamma[m][c][b] for m in range(n)))
              for d in range(n)] for c in range(n)] for b in range(n)] for a in range(n)]

def ricci_tensor(gamma,coords):
    n=len(coords)
    # Ricci_{bd} = R^a_{bad}, with derivative expansion applied directly.
    return sp.Matrix(n,n,lambda b,d:sp.simplify(sum(
        sp.diff(gamma[a][d][b],coords[a])-sp.diff(gamma[a][a][b],coords[d])+
        sum(gamma[a][a][m]*gamma[m][d][b]-gamma[a][d][m]*gamma[m][a][b] for m in range(n))
        for a in range(n))))

@reg('inverse_metric','Inverse metric','Compute g^{ij}.',BASE)
def inverse_metric(v):return geometry(v)[2]
@reg('determinant','Metric determinant','Compute det(g).',BASE)
def determinant(v):return sp.factor(metric_data(v)[1].det())
@reg('christoffel','Christoffel symbols','Nonzero Γ^a_bc for Levi-Civita connection.',BASE)
def christoffel(v):
    coords,g,inv,ga=geometry(v); n=len(coords); lines=[]
    for a in range(n):
        for b in range(n):
            for c in range(b,n):
                if ga[a][b][c]!=0:
                    lines.append(f'Gamma^{coords[a]}_{{{coords[b]} {coords[c]}}} = {sp.sstr(ga[a][b][c])}')
    return {'lines':lines or ['All Christoffel symbols vanish.']}
@reg('ricci','Ricci tensor','Compute R_ij using R^a_bcd = ∂cΓ^a_db − ∂dΓ^a_cb + ...',BASE)
def ricci(v):
    co,g,inv,ga=geometry(v)
    return ricci_tensor(ga,co).applyfunc(lambda z:sp.trigsimp(sp.expand_trig(z),method="fu"))
@reg('scalar_curvature','Scalar curvature','Compute R = g^{ij}R_ij.',BASE)
def scalar_curvature(v):
    co,g,inv,ga=geometry(v); R=ricci_tensor(ga,co); n=len(co)
    return sp.simplify(sum(inv[i,j]*R[i,j] for i in range(n) for j in range(n)))
@reg('einstein','Einstein tensor','Compute G_ij = R_ij − (R/2) g_ij.',BASE)
def einstein(v):
    co,g,inv,ga=geometry(v); r=ricci_tensor(ga,co); n=len(co)
    scalar=sp.simplify(sum(inv[i,j]*r[i,j] for i in range(n) for j in range(n)))
    return (r-sp.Rational(1,2)*scalar*g).applyfunc(sp.simplify)
@reg('riemann_component','Riemann component','Compute R^a_{bcd} for 0-based index values.',BASE+[field('a','Upper index a (0-based)','0'),field('b','Index b','1'),field('c','Index c','0'),field('d','Index d','1')])
def riemann_component(v):
    co,g,inv,ga=geometry(v); n=len(co)
    a,b,c,d=[math_int(v,k,0,n-1) for k in ('a','b','c','d')]
    return sp.trigsimp(sp.expand_trig(curvature(ga,co)[a][b][c][d]),method='fu')
@reg('covariant_derivative','Covariant derivative','Compute ∇_k V^i for a contravariant vector.',BASE+[field('vector','Components V^i','[0,1]'),field('direction','Differentiate along','r')])
def covariant_derivative(v):
    co,g,inv,ga=geometry(v)
    raw=parse_math(v.get('vector',''))
    if not isinstance(raw,list) or len(raw)!=len(co) or any(isinstance(item,list) for item in raw):
        raise ValueError('Enter one vector component per coordinate, e.g. [0,1].')
    k=math_symbol(v,'direction')
    if k not in co:raise ValueError('Direction must be one of the coordinates.')
    j=co.index(k)
    return sp.Matrix([sp.simplify(sp.diff(raw[a],k)+sum(ga[a][j][i]*raw[i] for i in range(len(co)))) for a in range(len(co))])
@reg('geodesic','Geodesic equations','Display the equations d²xᵃ/dλ² + Γᵃ_bc dxᵇ/dλ dxᶜ/dλ = 0.',BASE)
def geodesic(v):
    co,g,inv,ga=geometry(v); n=len(co)
    vel=sp.symbols('v0:'+str(n))
    lines=[]
    for a in range(n):
        expr=sp.simplify(sum(ga[a][b][c]*vel[b]*vel[c] for b in range(n) for c in range(n)))
        velmap={vel[k]:sp.Symbol('d_'+str(co[k])) for k in range(n)}
        expr=sp.simplify(expr.subs(velmap))
        lines.append(f'd2_{co[a]}/dλ² = {sp.sstr(-expr)}')
    return {'lines':lines}
