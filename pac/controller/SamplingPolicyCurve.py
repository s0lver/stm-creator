class SamplingPolicyCurve(object):
    def __init__(self, domain_start, domain_end, fun, **kwargs):
        self.function_domain_start = domain_start
        self.function_domain_end = domain_end
        self.fun = fun
        self.kwargs = kwargs

    def evaluate(self, x):
        return self.fun(x, **self.kwargs)
