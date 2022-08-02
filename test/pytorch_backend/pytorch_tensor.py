#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import torch
from crypten import CrypTensor, register_cryptensor


@register_cryptensor("ptt")
class PyTorchTensor(CrypTensor):
    """
    CrypTensor class that uses plaintext PyTorch tensors as underlying backend.
    This class should be used for testing purposes.
    """

    def __init__(self, tensor, device=None, *args, **kwargs):
        # take required_grad from kwargs, input tensor, or set to False:
        default = tensor.requires_grad if torch.is_tensor(tensor) else False
        requires_grad = kwargs.pop("requires_grad", default)

        # call CrypTensor constructor:
        super().__init__(requires_grad=requires_grad)

        if device is None:
            device = torch.device("cpu")
        tensor = (
            tensor.detach().to(device=device)
            if torch.is_tensor(tensor)
            else torch.tensor(tensor, device=device)
        )

        tensor.requires_grad = False
        self._tensor = tensor

    def get_plain_text(self):
        return self._tensor

    def shallow_copy(self):
        result = PyTorchTensor([])
        result._tensor = self._tensor
        return result

    def clone(self):
        result = PyTorchTensor([])
        result._tensor = self._tensor.clone()
        return result

    def copy_(self, other):
        """Copies value of other PyTorchTensor into this PyTorchTensor."""
        assert isinstance(other, PyTorchTensor), "other must be PyTorchTensor"
        self._tensor = other._tensor

    def add(self, tensor):
        result = self.clone()
        tensor = tensor._tensor if hasattr(tensor, "_tensor") else tensor
        result._tensor = result._tensor + tensor
        return result

    def neg(self):
        result = self.clone()
        result._tensor.neg_()
        return result

    def mul(self, tensor):
        result = self.clone()
        tensor = tensor._tensor if hasattr(tensor, "_tensor") else tensor
        result._tensor = result._tensor * tensor
        return result

    def div(self, tensor):
        result = self.clone()
        tensor = tensor._tensor if hasattr(tensor, "_tensor") else tensor
        result._tensor = result._tensor / tensor
        return result

    def matmul(self, tensor):
        result = self.clone()
        tensor = tensor._tensor if hasattr(tensor, "_tensor") else tensor
        result._tensor = result._tensor @ tensor
        return result

    def conv1d(self, kernel, *args, **kwargs):
        result = self.clone()
        kernel = kernel._tensor if hasattr(kernel, "_tensor") else kernel
        result._tensor = torch.nn.functional.conv1d(
            result._tensor, kernel, *args, **kwargs
        )
        return result

    def conv2d(self, kernel, *args, **kwargs):
        result = self.clone()
        kernel = kernel._tensor if hasattr(kernel, "_tensor") else kernel
        result._tensor = torch.nn.functional.conv2d(
            result._tensor, kernel, *args, **kwargs
        )
        return result

    def conv_transpose1d(self, kernel, *args, **kwargs):
        result = self.clone()
        kernel = kernel._tensor if hasattr(kernel, "_tensor") else kernel
        result._tensor = torch.nn.functional.conv_transpose1d(
            result._tensor, kernel, *args, **kwargs
        )
        return result

    def conv_transpose2d(self, kernel, *args, **kwargs):
        result = self.clone()
        kernel = kernel._tensor if hasattr(kernel, "_tensor") else kernel
        result._tensor = torch.nn.functional.conv_transpose2d(
            result._tensor, kernel, *args, **kwargs
        )
        return result

    def avg_pool2d(self, kernel_size, stride=None, padding=0):
        result = self.clone()
        result._tensor = torch.nn.functional.avg_pool2d(
            result._tensor, kernel_size, stride=stride, padding=padding
        )
        return result

    @property
    def dtype(self):
        return self._tensor.dtype

    def _ltz(self):
        """Returns 1 for elements that are < 0 and 0 otherwise"""
        result = self.clone()
        result._tensor = result._tensor.lt(0).to(self.dtype)
        return result

    @staticmethod
    def rand(*sizes, device=None):
        """
        Returns a tensor with elements uniformly sampled in [0, 1). The uniform
        random samples are generated by generating random bits using fixed-point
        encoding and converting the result to an ArithmeticSharedTensor.
        """
        if device is None:
            device = torch.device("cpu")
        return PyTorchTensor(torch.rand(*sizes, device=device))
