#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 10:54:57 2020

@author: ckielasjensen
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
from scipy.spatial import ConvexHull

from constants import DEG_ELEV
from polynomial.bernstein import Bernstein
from polynomial.rationalbernstein import RationalBernstein


SAVE_FIG = True         # Set to True to save figures
FIG_FORMAT = 'svg'      # Used for the output format when saving figures
FIG_DIR = 'Figures/3_5'     # Directory in which to save the figures
XLIM = [-0.5, 12.5]
YLIM = [-0.5, 12.5]


def setRCParams():
    # Run this to make sure that the matplotlib plots have the correct font type
    # for an IEEE publication. Also sets font sizes and line widths for easier
    # viewing.
    plt.rcParams.update({
                'font.size': 24,
                'figure.titlesize': 40,
                'pdf.fonttype': 42,
                'ps.fonttype': 42,
                'xtick.labelsize': 40,
                'ytick.labelsize': 40,
                'lines.linewidth': 4,
                'lines.markersize': 18,
                'figure.figsize': [13.333, 10]
                })
    # plt.tight_layout()


def resetRCParams():
    # Reset the matplotlib parameters
    plt.rcParams.update(plt.rcParamsDefault)


def initialPlot(c1, c2, obs):
    fig, ax = plt.subplots()

    c1.plot(ax, color='C0', label='c1')
    c2.plot(ax, color='C1', label='c2')
    ax.add_patch(obs)

    ax.set_title('Initial Figure')
    ax.set_xlabel('X Position (m)')
    ax.set_ylabel('Y Position (m)')
    ax.set_xlim(XLIM)
    ax.set_ylim(YLIM)
    ax.legend()


def endPoints(c1, c2, obs):
    fig, ax = plt.subplots()

    c1.plot(ax, showCpts=False, color='C0')
    c2.plot(ax, showCpts=False, color='C1')
    ax.add_patch(obs)

    for i, pt in enumerate(np.concatenate([c1.cpts[:, (0, -1)].T, c2.cpts[:, (0, -1)].T])):
        ax.plot(pt[0], pt[1], 'k.')

        # This if statement is purely for modifying the position of the drawn coordinates
        if i % 2:
            ax.text(pt[0]-3.5, pt[1]-1, f'({pt[0]}, {pt[1]})')
        else:
            ax.text(pt[0], pt[1], f'({pt[0]}, {pt[1]})')

    ax.set_title('End Points')
    ax.set_xlabel('X Position (m)')
    ax.set_ylabel('Y Position (m)')
    ax.set_xlim(XLIM)
    ax.set_ylim(YLIM)


def convexHull(c1, c2, obs):
    fig, ax = plt.subplots()

    for cpts in [c1.cpts, c2.cpts]:
        plotCvxHull(cpts, ax)

    c1.plot(ax, color='C0')
    c2.plot(ax, color='C1')
    ax.add_patch(obs)

    ax.set_title('Convex Hull')
    ax.set_xlabel('X Position (m)')
    ax.set_ylabel('Y Position (m)')
    ax.set_xlim(XLIM)
    ax.set_ylim(YLIM)


def convexHullSplit(c1, c2, obs):
    fig, ax = plt.subplots()

    c1L, c1R = c1.split(0.5*(c1.tf-c1.t0)+c1.t0)
    c2L, c2R = c2.split(0.5*(c2.tf-c2.t0)+c2.t0)

    c1L.plot(ax, color='C0')
    c1R.plot(ax, color='C2')
    c2L.plot(ax, color='C1')
    c2R.plot(ax, color='C3')

    for cpts in [c1L.cpts, c1R.cpts, c2L.cpts, c2R.cpts]:
        plotCvxHull(cpts, ax)

    ax.add_patch(obs)
    ax.set_title('Split Convex Hull')
    ax.set_xlabel('X Position (m)')
    ax.set_ylabel('Y Position (m)')
    ax.set_xlim(XLIM)
    ax.set_ylim(YLIM)


def convexHullElev(c1, c2, obs):
    fig, ax = plt.subplots()

    c1E = c1.elev(10)
    c2E = c2.elev(10)

    c1E.plot(ax, color='C0')
    c2E.plot(ax, color='C1')

    for cpts in [c1E.cpts, c2E.cpts]:
        plotCvxHull(cpts, ax)

    ax.add_patch(obs)
    ax.set_title('Elevated Convex Hull')
    ax.set_xlabel('X Position (m)')
    ax.set_ylabel('Y Position (m)')
    ax.set_xlim(XLIM)
    ax.set_ylim(YLIM)


def speedSquared(c1, c2):
    fig, ax = plt.subplots()

    c1speed = c1.diff().normSquare()
    c2speed = c2.diff().normSquare()

    c1speed.plot(ax, showCpts=False, color='C0', label='c1 speed')
    c2speed.plot(ax, showCpts=False, color='C1', label='c2 speed')

    ax.plot([c1speed.t0, c1speed.tf], [c1speed.min()]*2, 'r--', label='c1 minimum speed')
    ax.plot([c2speed.t0, c2speed.tf], [c2speed.min()]*2, 'b--', label='c2 minimum speed')

    ax.set_title('Speed Squared')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel(r'Squared Speed $\left( \frac{m}{s} \right)^2$')
    ax.legend()


def headingAngle(c1, c2):
    fig, ax = plt.subplots()

    c1dot = c1.diff()
    c2dot = c2.diff()

    c1tan = c1dot.y / c1dot.x
    c2tan = c2dot.y / c2dot.x

    c1tan.plot(ax, showCpts=False, color='C0', label='c1 tangent')
    c2tan.plot(ax, showCpts=False, color='C1', label='c2 tangent')

    ax.plot([c1tan.t0, c1tan.tf], [c1tan.min()]*2, 'r--', label='c1 minimum tangent')
    ax.plot([c2tan.t0, c1tan.tf], [c2tan.min()]*2, 'b--', label='c2 minimum tangent')

    ax.set_title('Tangent of Heading Angle')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel(r'$\tan (\psi)$')
    ax.legend()


def angularRate(c1, c2):
    fig, ax = plt.subplots()

    angrate1 = _angularRate(c1)
    angrate2 = _angularRate(c2)


    cpts1 = np.concatenate([[np.linspace(angrate1.t0, angrate1.tf, angrate1.deg+1)], angrate1.cpts])
    cpts2 = np.concatenate([[np.linspace(angrate2.t0, angrate2.tf, angrate2.deg+1)], angrate2.cpts])

    angrate1.plot(ax, showCpts=False, color='C0', label='c1 angular rate')
    angrate2.plot(ax, showCpts=False, color='C1', label='c2 angular rate')

    ax.plot([angrate1.t0, angrate1.tf], [angrate1.min()]*2, 'r--', label='c1 minimum angular rate')
    ax.plot([angrate2.t0, angrate2.tf], [angrate2.min()]*2, 'b--', label='c2 minimum angular rate')

    ax.set_title('Angular Rate')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel(r'Angular Rate $\left( \frac{rad}{s^2} \right)$')
    ax.legend()


def distSqr(c1, c2, obs):
    fig, ax = plt.subplots()

    obsPoly = Bernstein(np.atleast_2d(obs.center).T*np.ones((2, c1.deg+1)), min(c1.t0, c2.t0), max(c1.tf, c2.tf))

    c1c2 = c1 - c2
    c1obs = c1 - obsPoly
    c2obs = c2 - obsPoly

    c1c2.normSquare().plot(ax, label='c1 to c2')
    c1obs.normSquare().plot(ax, label='c1 to obstacle')
    c2obs.normSquare().plot(ax, label='c2 to obstacle')

    ax.set_title('Squared Distance Between Trajectories and Obstacle', wrap=True)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel(r'Squared Distance $(m^2)$')
    ax.legend()


def minDist(c1, c2, obs):
    fig, ax = plt.subplots()

    c1.plot(ax, showCpts=False, color='C0', label='c1')
    c2.plot(ax, showCpts=False, color='C1', label='c2')

    dist, t1, t2 = c1.minDist(c2)

    pt1 = c1(t1)
    pt2 = c2(t2)

    ax.plot([pt1[0], pt2[0]], [pt1[1], pt2[1]], 'k-', label='Minimum distance line')
    mid = pt1 + 0.5*(pt2-pt1)
    ax.text(mid[0]+0.3, mid[1], f'Dist: {dist}')

    ax.set_title('Minimum Spatial Distance')
    ax.set_xlabel('X Position (m)')
    ax.set_ylabel('Y Position (m)')
    ax.legend()


def _angularRate(bp):
    bpdot = bp.diff()
    bpddot = bpdot.diff()

    xdot = bpdot.x
    ydot = bpdot.y
    xddot = bpddot.x
    yddot = bpddot.y

    num = yddot*xdot - xddot*ydot
    den = xdot*xdot + ydot*ydot

    cpts = num.elev(DEG_ELEV).cpts / den.elev(DEG_ELEV).cpts
    wgts = den.elev(DEG_ELEV).cpts
    # cpts = num.cpts / den.cpts
    # wgts = den.cpts

    return RationalBernstein(cpts, wgts, bp.t0, bp.tf)


def plotCvxHull(cpts, ax):
    hull = ConvexHull(cpts.T)
    for simplex in hull.simplices:
        ax.plot(cpts[0, simplex], cpts[1, simplex], 'k:')


def saveFigs():
    import os
    # Create a Figures directory if it doesn't already exist
    if not os.path.isdir(FIG_DIR):
        os.mkdir(FIG_DIR)

    for i in plt.get_fignums():
        fig = plt.figure(i)
        ax = fig.get_axes()[0]
        title = ax.get_title()
        print(f'Saving figure {i} - {title}')

        ax.set_title('')
        plt.tight_layout()
        plt.draw()
        saveName = os.path.join(FIG_DIR, title.replace(' ', '_') + '.' + FIG_FORMAT)
        fig.savefig(saveName, format=FIG_FORMAT)
        ax.set_title(title)
        plt.draw()

    print('Done saving figures')


if __name__ == '__main__':
    plt.close('all')
    setRCParams()

    # Rectangle obstacle
    def obs(): return Circle((3, 4), 1, ec='k', lw=4)
    # Control points
    cpts1 = np.array([[0, 2, 4, 6, 8, 10],
                      [5, 0, 2, 3, 10, 3]], dtype=float)
    cpts2 = np.array([[1, 3, 6, 8, 10, 12],
                      [6, 9, 10, 11, 8, 8]], dtype=float)
    # Bernstein polynomials
    c1 = Bernstein(cpts1, t0=10, tf=20)
    c2 = Bernstein(cpts2, t0=10, tf=20)

    # initialPlot(c1, c2, obs())
    # endPoints(c1, c2, obs())
    # convexHull(c1, c2, obs())
    # convexHullSplit(c1, c2, obs())
    # convexHullElev(c1, c2, obs())
    speedSquared(c1, c2)
    headingAngle(c1, c2)
    angularRate(c1, c2)
    minDist(c1, c2, obs())
    # distSqr(c1, c2, obs())

    plt.show()

    if SAVE_FIG:
        saveFigs()

    resetRCParams()