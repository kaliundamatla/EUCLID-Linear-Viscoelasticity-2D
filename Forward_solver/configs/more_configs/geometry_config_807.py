"""
Geometry configuration for Experiment 806: Single ellipsoid hole

This configuration defines a rectangular specimen with a single
elliptical hole at the center, providing a true ellipse (not circular approximation).
"""

EXPERIMENT_CONFIG = {
    'id': 807,
    'name': 'Ellipsoid_Hole',
    'description': 'Single ellipsoid hole at center',

    'domain': {
        'width': 23.0,   # mm
        'height': 59,  # mm
    },

    'mesh_params': {
        'mesh_size_outer': 2.0,      # Outer boundary element size [mm]
        'mesh_size_hole': 2.0,       # Hole boundary element size [mm]
        'algorithm': 'delaunay'      # Meshing algorithm
    },

    'holes': [
        {
            'type': 'ellipse',
            'center': (11.5, 29.5),  # Center of domain
            'semi_major': 7.0,       # Horizontal semi-axis [mm]
            'semi_minor': 3.6,       # Vertical semi-axis [mm]
            'rotation': 46.20,         # Rotation angle [degrees]
            'name': 'central_ellipse'
        }
    ],

    'simulation_params': {
        'dt': 1.0,           # Time step [s]
        'n_timesteps': 600,  # Number of timesteps
        'load': 50.0,        # Load magnitude [N/mm]
    }
}
