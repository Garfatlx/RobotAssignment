from abc import ABC, abstractmethod
import numpy as np

class BaseFilter(ABC):
    @abstractmethod
    def update(self, vl, vr, angle, z):
        pass

    @abstractmethod
    def get_pose(self) -> np.ndarray:
        pass

    @abstractmethod
    def get_path(self) -> list:
        pass
