import abc
from copy import deepcopy
from typeguard import typechecked
from typing import List, Any

class BaseTransformer(abc.ABC):
    """The base transformer class from which all other transformers should inherit.
    The interface is analogous to the sklearn Transformer interface."""

    @abc.abstractclassmethod
    def fit(self, slide, target=None):
        raise NotImplementedError

    @abc.abstractmethod
    def transform(self, slide, target=None):
        raise NotImplementedError

    def fit_transform(self, slide, target=None):
        return self.fit(slide, target).transform(slide)


class StaticTransformer(BaseTransformer):
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

    def __init__(self, transformers: List[Any]):
        """


        Args:
            transformers: Transf
        """
        self.transformers = transformers

    def __len__(self):
        return len(self.steps)

    def __getitem__(self, ind):
        if type(ind) is int:
            return self.transformers[ind]
        else:
            return Pipeline(self.transformers[ind])

    def fit(self, slide):
        self.fit_transform(slide)
        return self

    def transform(self, slide):
        slide_output = slide
        for transformer in self.transformers:
            slide_output = transformer.transform(slide_output)
        return slide_output

    def fit_transform(self, slide):
        slide_output = slide
        for transformer in self.transformers:
            slide_output = transformer.fit_transform(slide=slide_output)
        return slide_output

