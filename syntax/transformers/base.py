import abc
from copy import deepcopy
from typeguard import typechecked
from typing import List

class BaseTransformer(abc.ABC):
    """The base transformer class from which all other transformers should inherit.
    The interface is analogous to the sklearn Transformer interface."""

    @abc.abstractclassmethod
    def fit(self, Slide, target=None):
        raise NotImplementedError

    @abc.abstractmethod
    def transform(self, Slide, target=None):
        raise NotImplementedError

    def fit_transform(self, Slide, target=None):
        return self.fit(Slide, target).transform(Slide)


class StaticTransformer(BaseTransformer, abc.ABC):
    """A transformer that doesn't require fitting (i.e. is stateless). Inheriting from this
    class saves you having to specify the 'empty' fit method every time."""

    def fit(self, *args, **kwargs):

        return self

@typechecked
class Pipeline(BaseTransformer):
    """A collection of transformers that inherits the same interface as the BaseTransformer
    class. Calling fit on a Pipeline sequentially fits the transformers in the pipeline,
    each time using the output of the previous transformers `transform` method as the
    `fit` input. Calling transform sequentially sequentially transforms the passed input,
    using the output of the previous `transform` as the input to the current `transform`.

    e.g. given BaseTransformer instances T_1, T_2, T_3
    p = Pipeline([T_1, T_2, T_3]) chains these transformers as T_1 -> T_2 -> T_3

    So p.fit(Slide) does
        X_tmp = T_1.fit(Slide).transform(Slide)
        X_tmp = T_2.fit(X_tmp).transform(X_tmp)
        X_tmp = T_2.fit(X_tmp).transform(X_tmp)
    and then returns p
    p.transform(Slide) does
        X_tmp = T_1.transform(Slide)
        X_tmp = T_2.transform(X_tmp)
        X_tmp = T_3.transform(X_tmp)
    and then returns X_tmp
    and p.fit_transform(Slide) does
        X_tmp = T_1.fit(Slide).transform(Slide)
        X_tmp = T_2.fit(X_tmp).transform(X_tmp)
        X_tmp = T_2.fit(X_tmp).transform(X_tmp)
    and then returns X_tmp
    """

    def __init__(self, transformers: List[BaseTransformer, StaticTransformer]):
        """


        Args:
            transformers: Transf
        """
        self.steps = transformers

    def __len__(self):
        return len(self.steps)

    def __getitem__(self, ind):
        if type(ind) is int:
            return self.steps[ind]
        else:
            return Pipeline(self.steps[ind])

    def fit(self, Slide):
        self.fit_transform(Slide)
        return self

    def transform(self, Slide):
        X_output = deepcopy(Slide)
        for transformer in self.steps:
            X_output = transformer.transform(X_output)
        return X_output

    def fit_transform(self, Slide):
        X_output = deepcopy(Slide)
        for transformer in self.steps:
            X_output = transformer.fit_transform(X_output)
        return X_output

