import math
from chainer import optimizers
from chainer.optimizer_hooks import GradientClipping


class Optimizer:
    def __init__(
            self,
            model_parameters,
            # Learning rate at training step s with annealing
            mu_i=3.0 * 1e-3,
            mu_f=1.0 * 1e-4,
            n=10000,
            # Learning rate as used by the Adam algorithm
            beta_1=0.9,
            beta_2=0.99,
            # Adam regularisation parameter
            eps=1e-8):
        self.mu_i = mu_i
        self.mu_f = mu_f
        self.n = n
        self.beta_1 = beta_1
        self.beta_2 = beta_2
        self.eps = eps

        lr = self.mu_s(0)
        self.optimizer = optimizers.Adam(
            lr, beta1=beta_1, beta2=beta_2, eps=eps)
        self.optimizer.setup(model_parameters)

    @property
    def learning_rate(self):
        return self.optimizer.alpha

    def mu_s(self, training_step):
        # Cyclical Learning Rate
        step_in_cycle_num = training_step % self.n
        if step_in_cycle_num < self.n / 2:
            # Increase LR
            return self.mu_f + (self.mu_i - self.mu_f) * 2.0 * (step_in_cycle_num / self.n)
        else:
            # Decrease LR
            return self.mu_f + (self.mu_i - self.mu_f) * 2.0 * (1.0 - step_in_cycle_num / self.n)

    def anneal_learning_rate(self, training_step):
        self.optimizer.hyperparam.alpha = self.mu_s(training_step)

    def update(self, training_step):
        self.optimizer.update()
        self.anneal_learning_rate(training_step)
