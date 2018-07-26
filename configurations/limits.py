from slivka import LimitsBase


class PydummyLimits(LimitsBase):

    configurations = ['local']

    def limit_local(self, values):
        return True


MuscleLimits = PydummyLimits
ClustaloLimits = PydummyLimits
ClustalLimits = PydummyLimits
TCoffeeLimits = PydummyLimits
AAConLimits = PydummyLimits
