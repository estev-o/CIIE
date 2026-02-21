from abc import ABC, abstractmethod

"""
Definicion de clase abstracta que se le pasa a la clase Interaction
"""

class Interactuable(ABC):
    
    @abstractmethod
    def interact(self):
        pass

    @abstractmethod
    def is_active(self):
        pass