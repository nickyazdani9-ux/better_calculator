import sympy as sp
from engine import register,field,parse_matrix
TAB=('linear','Linear algebra','grid')
def reg(op,label,desc,fields):return register(*TAB,op,label,desc,fields)
M=field('matrix','Matrix','[[1,2],[3,4]]',kind='textarea')
@reg('determinant','Determinant','Exact determinant.',[M])
def determinant(v):return parse_matrix(v.get('matrix','')).det()
@reg('inverse','Inverse','Matrix inverse.',[M])
def inverse(v):return parse_matrix(v.get('matrix','')).inv()
@reg('transpose','Transpose','Transpose a matrix.',[M])
def transpose(v):return parse_matrix(v.get('matrix','')).T
@reg('eigenvalues','Eigenvalues','Eigenvalues and multiplicities.',[field('matrix','Matrix','[[2,0],[0,3]]',kind='textarea')])
def eigenvalues(v):
    m=parse_matrix(v.get('matrix',''))
    if m.rows!=m.cols:raise ValueError('Eigenvalues require a square matrix.')
    eigen=m.eigenvals()
    lines=[f'{sp.sstr(k)} (multiplicity {mult})' for k,mult in sorted(eigen.items(),key=lambda pair:sp.default_sort_key(pair[0]))]
    return {'lines':lines,'latex':sp.latex(eigen)}
@reg('eigenvectors','Eigenvectors','Eigenvectors with algebraic multiplicities.',[field('matrix','Matrix','[[2,0],[0,3]]',kind='textarea')])
def eigenvectors(v):
    m=parse_matrix(v.get('matrix',''))
    if m.rows!=m.cols:raise ValueError('Eigenvectors require a square matrix.')
    return {'lines':[f'λ = {val}; multiplicity {mult}; basis {basis}' for val,mult,basis in m.eigenvects()]}
@reg('multiply','Matrix multiplication','Multiply A × B.',[M,field('other','Matrix B','[[5,6],[7,8]]',kind='textarea')])
def multiply(v):return parse_matrix(v.get('matrix',''))*parse_matrix(v.get('other',''))
