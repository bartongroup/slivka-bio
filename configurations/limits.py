from slivka import LimitsBase


class PydummyLimits(LimitsBase):

    configurations = ['gridengine', 'local']

    def limit_gridengine(self, values):
        return True

    def limit_local(self, values):
        return False


MuscleLimits = PydummyLimits
ClustaloLimits = PydummyLimits
ClustalLimits = PydummyLimits
TCoffeeLimits = PydummyLimits
AAConLimits = PydummyLimits
