from collections import namedtuple

import Bio.SeqIO
from slivka.scheduler import Limiter


SequencesData = namedtuple('SequencesData', 'number, length')


def analyse_sequences_file(filename, file_format):
    num = 0
    total_length = 0
    for record in Bio.SeqIO.parse(filename, file_format):
        num += 1
        total_length += len(record.seq)
    return SequencesData(num, total_length // num)


class AAConLimits(Limiter):
    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 200 and
            self.sequences_data.length <= 400
        )

    def limit_default(self, values):
        return (
            self.sequences_data.number <= 5000 and
            self.sequences_data.length <= 1000
        )


class ClustalLimits(Limiter):
    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 30 and
            self.sequences_data.length <= 500
        )

    def limit_default(self, values):
        return (
            self.sequences_data.number <= 1000 and
            self.sequences_data.length <= 1000
        )


class ClustaloLimits(Limiter):
    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 30 and
            self.sequences_data.length <= 500
        )

    def limit_default(self, values):
        return (
            self.sequences_data.number <= 2000 and
            self.sequences_data.length <= 1000
        )


class IUPredLimits(Limiter):
    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 50 and
            self.sequences_data.length <= 400
        )

    def limit_default(self, values):
        return (
            self.sequences_data.number <= 5000 and
            self.sequences_data.length <= 1000
        )


class MafftLimits(Limiter):
    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 20 and
            self.sequences_data.length <= 500
        )

    def limit_default(self, values):
        return (
            self.sequences_data.number <= 1000 and
            self.sequences_data.length <= 1000
        )


class MuscleLimits(Limiter):
    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 20 and
            self.sequences_data.length <= 500
        )

    def limit_default(self, values):
        return (
            self.sequences_data.number <= 1000 and
            self.sequences_data.length <= 1000
        )


class ProbconsLimits(Limiter):
    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 20 and
            self.sequences_data.length <= 500
        )

    def limit_default(self, values):
        return (
            self.sequences_data.number <= 1000 and
            self.sequences_data.length <= 1000
        )


class TCoffeeLimits(Limiter):
    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 15 and
            self.sequences_data.length <= 400
        )

    def limit_default(self, values):
        return (
            self.sequences_data.number <= 1000 and
            self.sequences_data.length <= 1000
        )


class GlobPlotLimits(Limiter):
    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 200 and
            self.sequences_data.length <= 400
        )

    def limit_default(self, values):
        return (
            self.sequences_data.number <= 5000 and
            self.sequences_data.length <= 1000
        )


class DisemblLimits(Limiter):
    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 200 and
            self.sequences_data.length <= 400
        )

    def limit_default(self, values):
        return (
            self.sequences_data.number <= 5000 and
            self.sequences_data.length <= 1000
        )


class JronnLimits(Limiter):
    def setup(self, values):
        self.sequences_data = analyse_sequences_file(values['input'], 'fasta')

    def limit_local(self, values):
        return (
            self.sequences_data.number <= 5 and
            self.sequences_data.length <= 50
        )

    def limit_default(self, values):
        return (
            self.sequences_data.number <= 2000 and
            self.sequences_data.length <= 2000
        )
