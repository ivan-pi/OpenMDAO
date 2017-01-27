"""Define a `Group` with two interconnected `ImplicitComponent`s for testing"""

from __future__ import division, print_function

from openmdao.api import Group, ImplicitComponent
from openmdao.api import LinearBlockGS, NonlinearBlockGS


class Comp(ImplicitComponent):

    def __init__(self, use_varsets=True):
        super(Comp, self).__init__()
        self._use_var_sets = use_varsets

    def initialize_variables(self):
        if self._use_var_sets:
            self.add_input('a', var_set=1)
            self.add_input('b', var_set=0)
            self.add_input('c', var_set=1)
            self.add_input('d', var_set=2)

            self.add_output('w', var_set=5)
            self.add_output('x', var_set=1)
            self.add_output('y', var_set=1)
            self.add_output('z', var_set=5)
        else:
            self.add_input('a')
            self.add_input('b')
            self.add_input('c')
            self.add_input('d')

            self.add_output('w')
            self.add_output('x')
            self.add_output('y')
            self.add_output('z')

    def apply_nonlinear(self, inputs, outputs, residuals):
        residuals['w'] = outputs['w'] + 2 * inputs['a']
        residuals['x'] = outputs['x'] + 3 * inputs['b']
        residuals['y'] = outputs['y'] + 4 * inputs['c']
        residuals['z'] = outputs['z'] + 5 * inputs['d']

    def apply_linear(self, inputs, outputs,
                     d_inputs, d_outputs, d_residuals, mode):
        if mode == 'fwd':
            if 'w' in d_outputs:
                d_residuals['w'] += d_outputs['w']
                if 'a' in d_inputs:
                    d_residuals['w'] += 2 * d_inputs['a']
            if 'x' in d_outputs:
                d_residuals['x'] += d_outputs['x']
                if 'b' in d_inputs:
                    d_residuals['x'] += 3 * d_inputs['b']
            if 'y' in d_outputs:
                d_residuals['y'] += d_outputs['y']
                if 'c' in d_inputs:
                    d_residuals['y'] += 4 * d_inputs['c']
            if 'z' in d_outputs:
                d_residuals['z'] += d_outputs['z']
                if 'd' in d_inputs:
                    d_residuals['z'] += 5 * d_inputs['d']
        else:
            if 'w' in d_outputs:
                d_outputs['w'] += d_residuals['w']
                if 'a' in d_inputs:
                    d_inputs['a'] += 2 * d_residuals['w']
            if 'x' in d_outputs:
                d_outputs['x'] += d_residuals['x']
                if 'b' in d_inputs:
                    d_inputs['b'] += 3 * d_residuals['x']
            if 'y' in d_outputs:
                d_outputs['y'] += d_residuals['y']
                if 'c' in d_inputs:
                    d_inputs['c'] += 4 * d_residuals['y']
            if 'z' in d_outputs:
                d_outputs['z'] += d_residuals['z']
                if 'd' in d_inputs:
                    d_inputs['d'] += 5 * d_residuals['z']

    def solve_linear(self, d_outputs, d_residuals, mode):
        if mode == 'fwd':
            out_vec = d_outputs
            in_vec = d_residuals
        elif mode == 'rev':
            in_vec = d_outputs
            out_vec = d_residuals

        for var in ['w', 'x', 'y', 'z']:
            out_vec[var] = in_vec[var]


class TestImplicitGroup(Group):
    """A `Group` with two interconnected `ImplicitComponent`s."""

    def __init__(self, lnSolverClass=LinearBlockGS,
                       nlSolverClass=NonlinearBlockGS,
                       use_varsets=True):

        super(TestImplicitGroup, self).__init__()

        self.add_subsystem("C1", Comp(use_varsets))
        self.add_subsystem("C2", Comp(use_varsets))

        self.connect("C1.w", "C2.a")
        self.connect("C1.x", "C2.b")
        self.connect("C1.y", "C2.c")
        self.connect("C1.z", "C2.d")

        self.connect("C2.w", "C1.a")
        self.connect("C2.x", "C1.b")
        self.connect("C2.y", "C1.c")
        self.connect("C2.z", "C1.d")

        self.ln_solver = lnSolverClass()
        self.nl_solver = nlSolverClass()

        if use_varsets:
            self.expected_solution = [
                [1./4., 1./5., 1./4., 1./5.],
                [1./3., 1./6., 1./3., 1./6.]
            ]
        else:
            self.expected_solution = [
                [1./3., 1./4., 1./5., 1./6.,
                 1./3., 1./4., 1./5., 1./6.]
            ]
