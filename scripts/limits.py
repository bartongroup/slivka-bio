from collections import namedtuple

import Bio.SeqIO
from slivka import Limits


SequencesData = namedtuple('SequencesData', 'number, length')


def analyse_sequences_file(filename, file_format):
    num = 0
    total_length = 0
    for record in Bio.SeqIO.parse(filename, file_format):
        num += 1
        total_length += len(record.seq)
    return SequencesData(num, total_length // num)


class PydummyLimits(Limits):

    configurations = ['local']

    def limit_local(self, values):
        return True


class AAConLimits(Limits):

    configurations = ['local', 'gridengine']

    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 200 and
            self.sequences_data.length <= 400
        )

    def limit_gridengine(self, values):
        return (
            self.sequences_data.number <= 5000 and
            self.sequences_data.length <= 1000
        )


class ClustalLimits(Limits):

    configurations = ['local', 'gridengine']

    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 30 and
            self.sequences_data.length <= 500
        )

    def limit_gridengine(self, values):
        return (
            self.sequences_data.number <= 1000 and
            self.sequences_data.length <= 1000
        )


class ClustaloLimits(Limits):

    configurations = ['local', 'gridengine']

    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 30 and
            self.sequences_data.length <= 500
        )

    def limit_gridengine(self, values):
        return (
            self.sequences_data.number <= 2000 and
            self.sequences_data.length <= 1000
        )


class IUPredLimits(Limits):

    configurations = ['local', 'gridengine']

    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 50 and
            self.sequences_data.length <= 400
        )

    def limit_gridengine(self, values):
        return (
            self.sequences_data.number <= 5000 and
            self.sequences_data.length <= 1000
        )


class MafftLimits(Limits):

    configurations = ['local', 'gridengine']

    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 20 and
            self.sequences_data.length <= 500
        )

    def limit_gridengine(self, values):
        return (
            self.sequences_data.number <= 1000 and
            self.sequences_data.length <= 1000
        )


class MuscleLimits(Limits):

    configurations = ['local', 'gridengine']

    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 20 and
            self.sequences_data.length <= 500
        )

    def limit_gridengine(self, values):
        return (
            self.sequences_data.number <= 1000 and
            self.sequences_data.length <= 1000
        )


class ProbconsLimits(Limits):

    configurations = ['local', 'gridengine']

    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 20 and
            self.sequences_data.length <= 500
        )

    def limit_gridengine(self, values):
        return (
            self.sequences_data.number <= 1000 and
            self.sequences_data.length <= 1000
        )


class TCoffeeLimits(Limits):

    configurations = ['local', 'gridengine']

    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 15 and
            self.sequences_data.length <= 400
        )

    def limit_gridengine(self, values):
        return (
            self.sequences_data.number <= 1000 and
            self.sequences_data.length <= 1000
        )


class GlobPlotLimits(Limits):

    configurations = ['local', 'gridengine']

    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 200 and
            self.sequences_data.length <= 400
        )

    def limit_gridengine(self, values):
        return (
            self.sequences_data.number <= 5000 and
            self.sequences_data.length <= 1000
        )


class DisemblLimits(Limits):

    configurations = ['local', 'gridengine']

    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 200 and
            self.sequences_data.length <= 400
        )

    def limit_gridengine(self, values):
        return (
            self.sequences_data.number <= 5000 and
            self.sequences_data.length <= 1000
        )


class JronnLimits(Limits):

    configurations = ['local', 'gridengine']

    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 5 and
            self.sequences_data.length <= 50
        )

    def limit_gridengine(self, values):
        return (
            self.sequences_data.number <= 2000 and
            self.sequences_data.length <= 2000
        )
