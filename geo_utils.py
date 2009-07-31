#!/usr/bin/python  
from numpy import pi,cos,sin,linspace,zeros,where,interp,sqrt,hstack,dot
import string 

def rotxM(theta):
    '''Return x rotation matrix'''
    theta = theta*pi/180
    M = [[1,0,0],[0,cos(theta),-sin(theta)],[0,sin(theta),cos(theta)]]
    return M

def rotyM(theta):
    ''' Return y rotation matrix'''
    theta = theta*pi/180
    M = [[cos(theta),0,sin(theta)],[0,1,0],[-sin(theta),0,cos(theta)]]
    return M

def rotzM(theta):
    ''' Return z rotation matrix'''
    theta = theta*pi/180
    M = [[cos(theta),-sin(theta),0],[sin(theta),cos(theta),0],[0,0,1]]
    return M

def rotxV(x,theta):
    ''' Rotate a coordinate in the local x frame'''
    M = [[1,0,0],[0,cos(theta),-sin(theta)],[0,sin(theta),cos(theta)]]
    return dot(M,x)

def rotyV(x,theta):
    '''Rotate a coordinate in the local y frame'''
    M = [[cos(theta),0,sin(theta)],[0,1,0],[-sin(theta),0,cos(theta)]]
    return dot(M,x)

def rotzV(x,theta):
    '''Roate a coordinate in the local z frame'''
    'rotatez:'
    M = [[cos(theta),-sin(theta),0],[sin(theta),cos(theta),0],[0,0,1]]
    return dot(M,x)

def e_dist(x1,x2):
    '''Get the eculidean distance between two points'''
    return sqrt((x1[0]-x2[0])**2 + (x1[1]-x2[1])**2 + (x1[2]-x2[2])**2)
def read_af(filename,N=35):
    ''' Load the airfoil file from precomp format'''

    # Interpolation Format
    s_interp = 0.5*(1-cos(linspace(0,pi,N)))

    f = open(filename,'r')

    aux = string.split(f.readline())
    npts = int(aux[0]) 

    xnodes = zeros(npts)
    ynodes = zeros(npts)

    f.readline()
    f.readline()
    f.readline()

    for i in xrange(npts):
        aux = string.split(f.readline())
        xnodes[i] = float(aux[0])
        ynodes[i] = float(aux[1])
    # end for
    f.close()

    # -------------
    # Upper Surfce
    # -------------

    # Find the trailing edge point
    index = where(xnodes == 1)
    te_index = index[0]
    n_upper = te_index+1   # number of nodes on upper surface
    n_lower = int(npts-te_index)+1 # nodes on lower surface

    # upper Surface Nodes
    x_u = xnodes[0:n_upper]
    y_u = ynodes[0:n_upper]

    # Now determine the upper surface 's' parameter

    s = zeros(n_upper)
    for j in xrange(n_upper-1):
        s[j+1] = s[j] + sqrt((x_u[j+1]-x_u[j])**2 + (y_u[j+1]-y_u[j])**2)
    # end for
    s = s/s[-1] #Normalize s

    # linearly interpolate to find the points at the positions we want
    X_u = interp(s_interp,s,x_u)
    Y_u = interp(s_interp,s,y_u)

    # -------------
    # Lower Surface
    # -------------
    x_l = xnodes[te_index:npts]
    y_l = ynodes[te_index:npts]
    x_l = hstack([x_l,0])
    y_l = hstack([y_l,0])

    # Now determine the lower surface 's' parameter

    s = zeros(n_lower)
    for j in xrange(n_lower-1):
        s[j+1] = s[j] + sqrt((x_l[j+1]-x_l[j])**2 + (y_l[j+1]-y_l[j])**2)
    # end for
    s = s/s[-1] #Normalize s

    # linearly interpolate to find the points at the positions we want
    X_l = interp(s_interp,s,x_l)
    Y_l = interp(s_interp,s,y_l)

    return X_u,Y_u,X_l,Y_l


def test_edge(surf1,surf2,i,j,edge_tol):

    '''Test edge i on surf1 with edge j on surf2'''

    val1_beg = surf1.getValueEdge(i,0)
    val1_end = surf1.getValueEdge(i,1)

    val2_beg = surf2.getValueEdge(j,0)
    val2_end = surf2.getValueEdge(j,1)

    #Three things can happen:
    coinc = False
    dir_flag = 1
    # Beginning and End match (same sense)
    if e_dist(val1_beg,val2_beg) < edge_tol and \
           e_dist(val1_end,val2_end) < edge_tol:
        # End points are the same, now check the midpoint
        mid1 = surf1.getValueEdge(i,0.5)
        mid2 = surf2.getValueEdge(j,0.5)
        if e_dist(mid1,mid2) < edge_tol:
            coinc = True
        else:
            coinc = False

        dir_flag = 1

    # Beginning and End match (opposite sense)
    elif e_dist(val1_beg,val2_end) < edge_tol and \
           e_dist(val1_end,val2_beg) < edge_tol:

        mid1 = surf1.getValueEdge(i,0.5)
        mid2 = surf2.getValueEdge(j,0.5)
        if e_dist(mid1,mid2) < edge_tol:
            coinc = True
        else:
            coinc = False

        dir_flag = -1
    # If nothing else
    else:
        coinc = False

    return coinc,dir_flag

def flipEdge(edge):
    if edge == 0: return 1
    if edge == 1: return 0
    if edge == 2: return 3
    if edge == 3: return 2
    else:
        return None
   

def getNodesFromEdge(edge):
    '''Get the index of the two nodes coorsponding to edge edge'''
    if edge == 0:
        n1 = 0
        n2 = 1
    elif edge == 1:
        n1 = 2
        n2 = 3
    elif edge == 2:
        n1 = 0
        n2 = 2
    else:
        n1 = 1
        n2 = 3
        
    return n1,n2