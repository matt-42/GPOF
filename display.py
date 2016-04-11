import numpy as np
import matplotlib.tri as mtri
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def display_2d_curve(runset, c1, c2):
    fig = plt.figure(figsize=(6,6), facecolor='white')
    plt.plot(runset.col(c1), runset.col(c2), '-')
    plt.show()

def display_2d_points(view):

    fig = plt.figure(figsize=(6,6), facecolor='white')
    sp = plt.subplot(111)

    A,B = zip(*view.data)

    sp.set_xlabel(view.col_names[0])
    sp.set_ylabel(view.col_names[1])
    
    im = sp.plot(A, B, '+')
    fig.show()
 
def display_2d_colorpoints(view, s=100):
    fig = plt.figure(figsize=(6,6), facecolor='white')
    sp = plt.subplot(111)

    A,B,C = zip(*view.data)

    sp.set_xlabel(view.col_names[0])
    sp.set_ylabel(view.col_names[1])
    
    im = sp.scatter(A, B, c=C, s=s, cmap=plt.cm.rainbow, marker='o', edgecolor='none')
    fig.show()
    bar = fig.colorbar(im)
    bar.ax.set_ylabel(view.col_names[2])
   
def display_2d_heatmap(view):
    fig = plt.figure(figsize=(6,6), facecolor='white')
    sp = plt.subplot(111)

    A,B,C = zip(*view.data)
    triang = mtri.Triangulation(A, B);
    #interp_cubic_geom = mtri.CubicTriInterpolator(triang, C, kind='geom')
    interp_cubic_geom = mtri.LinearTriInterpolator(triang, C)
    #interp_cubic_geom = mtri.CubicTriInterpolator(triang, C)

    X, Y = np.meshgrid(np.linspace(min(A), max(A), 100), np.linspace(min(B), max(B), 100))

    #X = np.arange(min(A), max(A), (max(A) - min(A)) / 10.)
    #Y = np.arange(min(B), max(B), (max(B) - min(B)) / 10.)
    Z = interp_cubic_geom(X, Y)
    #print(len(X), len(Y), len(Z))
    #im =sp.contourf(X, Y, Z, shading='flat', edgecolor='none',
    #                   cmap=plt.cm.rainbow, levels=sorted(set(C)))
    im =sp.pcolor(X, Y, Z, shading='flat', edgecolor='none',
                 cmap=plt.cm.rainbow)
    sp.set_xlabel(view.col_names[0])
    sp.set_ylabel(view.col_names[1])
    fig.show()
    bar = fig.colorbar(im)
    bar.ax.set_ylabel(view.col_names[2])

    

def display_3d_wireframe(view):
    fig = plt.figure(figsize=(6,6), facecolor='white')
    sp = plt.subplot(111, projection='3d')

    A,B,C = zip(*view.data)
    sp.set_xlabel(view.col_names[0])
    sp.set_ylabel(view.col_names[1])
    sp.set_title(view.col_names[2])
    
    sp.plot_wireframe(A, B, C, rstride=100, cstride=100)
    fig.show()

def display_3d_surface(view):
    fig = plt.figure(figsize=(6,6), facecolor='white')
    sp = plt.gca(projection='3d')

    A,B,C = zip(*view.data)
    sp.set_xlabel(view.col_names[0])
    sp.set_ylabel(view.col_names[1])
    sp.set_title(view.col_names[2])
    
    surf = sp.plot_trisurf(A, B, C, cmap=plt.cm.jet, linewidth=0.)
    fig.colorbar(surf, shrink=0.5, aspect=5)
    fig.show()

def display_3d_points(view):
    fig = plt.figure(figsize=(6,6), facecolor='white')
    sp = plt.gca(projection='3d')

    A,B,C = zip(*view.data)
    sp.set_xlabel(view.col_names[0])
    sp.set_ylabel(view.col_names[1])
    sp.set_title(view.col_names[2])
    
    surf = sp.scatter(A, B, C, marker='.')
    fig.show()
    
