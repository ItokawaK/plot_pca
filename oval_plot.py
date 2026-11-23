#!/usr/bin/env python3
"""
pca_oval_plot.py
================

Create an adegenet / ade4 ``s.class``-style "oval plot" for PCA in population
genetics: a scatter of PC1 vs PC2 (or any two PCs) with points colored by
population and a concentration ellipse (oval) drawn around each group.

Ellipse details
---------------
For each population group with 2D coordinate matrix X (n x 2):
    centroid mu = mean(X)
    covariance S = cov(X)   (unbiased, ddof=1)
The concentration ellipse is the set of points x such that
    (x - mu)^T S^{-1} (x - mu) = c
where c = chi2.ppf(confidence, 2).  Semi-axes and orientation come from the
eigendecomposition of S = V Lambda V^T:
    a = sqrt(lambda1 * c),  b = sqrt(lambda2 * c),  angle = atan2(v1y, v1x)

This matches the ade4 ``s.class`` concentration ellipse (a population/cluster
scatter ellipse, not a confidence interval of the mean).  Use
--ellipse-type mean for a confidence interval of the mean instead.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np
import matplotlib
matplotlib.use("Agg")  # non-interactive backend; safe for scripts/servers
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from scipy.stats import chi2
import pandas as pd

@dataclass
class EllipseSpec:
    centroid: Tuple[float, float]
    width: float      # full major axis length
    height: float     # full minor axis length
    angle_deg: float  # rotation in degrees

def concentration_ellipse(
    x: np.ndarray, y: np.ndarray, confidence: float, mean_type: bool
) -> Optional[EllipseSpec]:
    """Compute the concentration ellipse for a 2D point cloud.

    Returns None if the ellipse cannot be computed (too few points or a
    rank-deficient covariance matrix).
    """
    pts = np.column_stack([x, y])
    n = pts.shape[0]
    if n < 3:
        return None
    mu = pts.mean(axis=0)
    cov = np.cov(pts, rowvar=False)
    # Guard against singular / non-finite covariance.
    if not np.all(np.isfinite(cov)):
        return None
    try:
        eigvals, eigvecs = np.linalg.eigh(cov)
    except np.linalg.LinAlgError:
        return None
    if not np.all(np.isfinite(eigvals)) or np.any(eigvals <= 0):
        return None

    c = chi2.ppf(confidence, df=2)
    # For a confidence interval of the mean, shrink by sqrt(n).
    scale = np.sqrt(n) if mean_type else 1.0
    a = np.sqrt(eigvals[1] * c) / scale  # larger eigenvalue -> major axis
    b = np.sqrt(eigvals[0] * c) / scale
    # eigenvector for the larger eigenvalue gives the major-axis direction.
    v = eigvecs[:, 1]
    angle = np.degrees(np.arctan2(v[1], v[0]))
    return EllipseSpec(
        centroid=(mu[0], mu[1]),
        width=2 * a,
        height=2 * b,
        angle_deg=angle,
    )

# plotting function
def plot_ovals(
    ax:plt.Axes,
    result: pd.DataFrame,
    confidence: float = 0.95,
    mean_type: bool = True,
    show_centroids: bool = True,
    show_labels: bool = True,
    alpha_fill: float = 0.18,
    ) -> None:

    pops = set(result.pops)


    # Concentration ellipses per population.
    for pop in pops:
        mask = np.array([p == pop for p in result.pops])
        spec = concentration_ellipse(
            result.x[mask], result.y[mask], confidence, mean_type
        )
        if spec is None:
            print(
                f"Warning: skipping ellipse for '{pop}' "
                f"(n={int(mask.sum())} < 3 or singular covariance).",
                file=sys.stderr,
            )
        else:
            ell = Ellipse(
                xy=spec.centroid,
                width=spec.width,
                height=spec.height,
                angle=spec.angle_deg,
                # facecolor= colors[pop],
                facecolor= 'none',
                # edgecolor= colors[pop],
                edgecolor= 'k',
                alpha=alpha_fill,
                linewidth=0.9,
                ls = '--',
                zorder=2,
            )

            ax.add_patch(ell)

            if show_centroids:
                ax.scatter(
                    [spec.centroid[0]],
                    [spec.centroid[1]],
                    marker="+",
                    color= 'k',
                    s=70,
                    alpha=alpha_fill,
                    linewidths=1.6,
                    zorder=4,
                )

            if show_labels:
                ax.annotate(
                    pop, 
                    xy=spec.centroid,
                    xytext=(8, 8), 
                    textcoords="offset points",
                    color='k',
                    fontsize=9,
                    alpha= 0.7,
                    fontweight="bold",
                    zorder=5,
                )
