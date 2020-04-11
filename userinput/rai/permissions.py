from rai.permissions.permissions import BasePermission

class MovePermission(BasePermission):
    key= 'move'
    value = 5
    description = 'Verschieben von Instanzen zu einer anderen Arbeitsgruppe'

class InactivatePermission(BasePermission):
    key='inactivate'
    value = 7
    description = 'Inaktivieren von Instanzen'
