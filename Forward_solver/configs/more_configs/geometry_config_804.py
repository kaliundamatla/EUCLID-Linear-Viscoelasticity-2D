"""
Geometry configuration for Experiment 804: Single circular hole at center

This configuration defines a simple rectangular specimen with a single
circular hole positioned at the geometric center.
"""

EXPERIMENT_CONFIG = {
    'id': 804,
    'name': 'Single_Central_Hole',
    'description': 'Single circular hole at specimen center',

    'domain': {
        'width': 20.0,   # mm
        'height': 60.0,  # mm
    },

    'mesh_params': {
        'mesh_size_outer': 2.0,      # Outer boundary element size [mm]
        'mesh_size_hole': 0.15,      # Hole boundary element size [mm] (smaller = smoother circle)
        'algorithm': 'delaunay'      # Meshing algorithm
    },

    'holes': [
        {
            'type': 'circle',
            'center': (10.0, 30.0),  # Center of domain (width/2, height/2)
            'radius': 3.0,           # mm
            'name': 'central_hole'
        }
    ],

    'simulation_params': {
        'dt': 1.0,           # Time step [s]
        'n_timesteps': 600,  # Number of timesteps
        'load': 50.0,        # Load magnitude [N/mm]
    }
}
