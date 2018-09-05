import io
import re
from argparse import ArgumentParser
from collections import namedtuple


def split_file(f, delimiter, buffer_size=1024):
    buffer = []
    while True:
        s = f.read(buffer_size)
        if not s:
            break
        fragments = s.split(delimiter)
        buffer.append(fragments[0])
        if len(fragments) > 1:
            yield str.join('', buffer)
            for fragment in fragments[1:-1]:
                yield fragment
            buffer = [fragments[-1]]
    if buffer:
        yield str.join('', buffer)


class GlobPlotParser:
    SequenceFeatures = namedtuple('Features', 'domains, disorder')
    SequenceAnnotations = namedtuple('Annotations', 'dydx')

    def __init__(self, input_file):
        self.sequence_features = {}
        self.sequence_annotations = {}
        sequences_iterator = split_file(input_file, '>')
        assert next(sequences_iterator) == ''
        for seq in sequences_iterator:
            buffer = io.StringIO(seq.rstrip('\r\n'))
            seq_id = buffer.readline().rstrip()
            self.sequence_features[seq_id] = self.parse_features(buffer)
            self.sequence_annotations[seq_id] = self.parse_annotations(buffer)
            buffer.close()

    @staticmethod
    def parse_features(input_file):
        line = input_file.readline()
        assert line.startswith('# GlobDoms')
        domains = parse_ranges(line[len('# GlobDoms'):])
        line = input_file.readline()
        assert line.startswith('# Disorder')
        disorder = parse_ranges(line[len('# Disorder'):])
        return GlobPlotParser.SequenceFeatures(domains, disorder)

    @staticmethod
    def parse_annotations(input_file):
        assert re.match(r'#\sRESIDUE\tDYDX\tRAW\tSMOOTHED',
                        input_file.readline())
        dydx = [float(line.split('\t')[1]) for line in input_file]
        return GlobPlotParser.SequenceAnnotations(dydx)

    def write_jalview_features(self, output_file):
        output_file.write('Protein Disorder\tc5b938\n'
                          'Globular Domain\t876d2a\n\n'
                          'STARTGROUP\tGlobPlotWS\n')
        for sequence_id, features in self.sequence_features.items():
            for gd in features.domains:
                output_file.write(
                    'Predicted globular domain\t{id}\t'
                    '-1\t{gd[0]}\t{gd[1]}\tGlobular Domain\n'
                    .format(id=sequence_id, gd=gd)
                )
            for pd in features.disorder:
                output_file.write(
                    'Probable unstructured peptide region\t{id}\t'
                    '-1\t{pd[0]}\t{pd[1]}\tProtein Disorder\n'
                    .format(id=sequence_id, pd=pd)
                )
        output_file.write('ENDGROUP\tGlobPlotWS\n')

    def write_jalview_annotations(self, output_file):
        output_file.write('JALVIEW_ANNOTATION\n\n')
        for sequence_id, annotations in self.sequence_annotations.items():
            output_file.write(
                'SEQUENCE_REF\t{id}\n'
                'LINE_GRAPH\tGlobPlotWS (Dydx)\t'
                '<html>Protein Disorder with GlobPlotWS - raw scores<br/>'
                'Above 0.0 indicates disorder</html>\t{annot}\n'
                'GRAPHLINE\tGlobPlotWS (Dydx)\t0.0\t'
                'Above 0.0 indicates disorder\tff0000\n\n'
                .format(
                    id=sequence_id,
                    annot='|'.join(map('{:.4f}'.format, annotations.dydx))
                )
            )
        output_file.write('COLOUR\tGlobPlotWS (Dydx)\t8123cc\n')


class DisemblParser:
    SequenceFeatures = namedtuple('Features', 'coils, rem465, hotloops')
    SequenceAnnotations = namedtuple('Annotations', 'rem465')

    def __init__(self, input_file):
        self.sequence_features = {}
        self.sequence_annotations = {}
        sequences_iterator = split_file(input_file, '>')
        assert next(sequences_iterator) == ''
        for seq in sequences_iterator:
            buffer = io.StringIO(seq.rstrip('\r\n'))
            seq_id = buffer.readline().strip()
            self.sequence_features[seq_id] = self.parse_features(buffer)
            self.sequence_annotations[seq_id] = self.parse_annotations(buffer)
            buffer.close()

    @staticmethod
    def parse_features(input_file):
        line = input_file.readline()
        assert line.startswith('# COILS')
        coils = parse_ranges(line[len('# COILS'):])
        line = input_file.readline()
        assert line.startswith('# REM465')
        rem465 = parse_ranges(line[len('# REM465'):])
        line = input_file.readline()
        assert line.startswith('# HOTLOOPS')
        hotloops = parse_ranges(line[len('# HOTLOOPS'):])
        return DisemblParser.SequenceFeatures(coils, rem465, hotloops)

    @staticmethod
    def parse_annotations(input_file):
        assert re.match(r'#\sRESIDUE\tCOILS\tREM465\tHOTLOOPS',
                        input_file.readline())
        rem465 = [float(line.split('\t')[2]) for line in input_file]
        return DisemblParser.SequenceAnnotations(rem465)

    def write_jalview_features(self, output_file):
        output_file.write(
            'HOTLOOPS\t511e29\n'
            'REM465\t1e5146\n'
            'COILS\tcfdb48\n\n'
            'STARTGROUP\tDisemblWS\n'
        )
        for seq_id, features in self.sequence_features.items():
            for rc in features.coils:
                output_file.write(
                    'Random coil\t{id}\t-1\t{start}\t{end}\tCOILS\n'
                    .format(id=seq_id, start=rc[0], end=rc[1])
                )
            for md in features.rem465:
                output_file.write(
                    'Missing density\t{id}\t-1\t{start}\t{end}\tREM465\n'
                    .format(id=seq_id, start=md[0], end=md[1])
                )
            for fl in features.hotloops:
                output_file.write(
                    'Flexible loops\t{id}\t-1\t{start}\t{end}\tHOTLOOPS\n'
                    .format(id=seq_id, start=fl[0], end=fl[1])
                )
        output_file.write('ENDGROUP\tDisemblWS\n')

    def write_jalview_annotations(self, output_file):
        output_file.write('JALVIEW_ANNOTATION\n\n')
        for seq_id, annotations in self.sequence_annotations.items():
            output_file.write(
                'SEQUENCE_REF\t{id}\n'
                'LINE_GRAPH\tDisemblWS (REM465)\t'
                '<html>Protein Disorder with DisemblWS - raw scores<br/>'
                'Above 0.1204 indicates disorder</html>\t{annot}\n'
                'GRAPHLINE\tDisemblWS (REM465)\t0.1204\t'
                'Above 0.1204 indicates disorder\tff0000\n\n'
                .format(
                    id=seq_id,
                    annot='|'.join(map('{:.5f}'.format, annotations.rem465))
                )
            )
        output_file.write('COLOUR\tDisemblWS (REM465)\t2385b0\n')


class IUPredParser:
    def __init__(self, short_file=None, long_file=None, glob_file=None):
        self.seq_id = None
        self.short_annotations = None
        self.long_annotations = None
        self.globular_domains = None
        if short_file:
            self.seq_id, self.short_annotations = (
                self.parse_annotations(short_file)
            )
        if long_file:
            seq_id, self.long_annotations = self.parse_annotations(long_file)
            if self.seq_id is None:
                self.seq_id = seq_id
            else:
                assert self.seq_id == seq_id
        if glob_file:
            seq_id, self.globular_domains = self.parse_features(glob_file)
            if self.seq_id is None:
                self.seq_id = seq_id
            else:
                assert self.seq_id == seq_id

    @staticmethod
    def parse_annotations(input_file):
        prev_line = None
        seq_id = None
        annotations = []
        for line in input_file:
            if line.startswith('#'):
                prev_line = line
                continue
            if seq_id is None and prev_line is not None:
                seq_id = prev_line[1:].strip()
            annotations.append(float(line.split()[2]))
        return seq_id, annotations

    @staticmethod
    def parse_features(input_file):
        line = input_file.readline()
        n = None
        while line:
            line = line.strip()
            if line and not line.startswith('#'):
                match = re.match(r'Number of globular domains:\s+(\d+)', line)
                if match:
                    n = int(match.group(1))
                    break
            line = input_file.readline()
        assert n is not None, 'Invalid iupred glob file'
        i = 0
        features = []
        while i < n:
            line = input_file.readline().strip()
            match = re.match(
                r'globular domain\s+\d+\.\s+(\d+) ?- ?(\d+)', line
            )
            assert match
            features.append((int(match.group(1)), int(match.group(2))))
            i += 1
        line = input_file.readline()
        seq_id = None
        while line:
            if line.startswith('>'):
                seq_id = line[1:].strip()
                break
            line = input_file.readline()
        assert seq_id, 'Invalid iupred glob file'
        return seq_id, features

    def write_jalview_features(self, output_file):
        if not self.globular_domains:
            return
        output_file.write(
            'Globular Domain\t876d2a\n\n'
            'STARTGROUP\tIUPredWS\n'
        )
        for feat in self.globular_domains:
            output_file.write(
                'Predicted globular domain\t{id}\t-1\t{start}\t{end}\t'
                'Globular Domain\n'
                .format(id=self.seq_id, start=feat[0], end=feat[1])
            )
        output_file.write('ENDGROUP\tIUPredWS\n')

    def write_jalview_annotations(self, output_file):
        if not (self.long_annotations or self.short_annotations):
            return
        output_file.write(
            'JALVIEW_ANNOTATION\n\n'
            'SEQUENCE_REF\t{id}\n'
            .format(id=self.seq_id)
        )
        annotations = [
            (self.long_annotations, 'Long'),
            (self.short_annotations, 'Short')
        ]
        for annot, annot_type in annotations:
            if annot:
                output_file.write(
                    'LINE_GRAPH\tIUPredWS ({type})\t'
                    '<html>Protein Disorder with IUPredWS - raw scores<br/>'
                    'Above 0.5 indicates disorder</html>\t{annot}\n'
                    'GRAPHLINE\tIUPredWS ({type})\t0.5\t'
                    'Above 0.5 indicates disorder\tff0000\n'
                    .format(
                        type=annot_type,
                        annot='|'.join('{:.4f}'.format(x) for x in annot)
                    )
                )
        output_file.write('\n')
        if self.long_annotations:
            output_file.write('COLOUR\tIUPredWS (Long)\t72144e\n')
        if self.short_annotations:
            output_file.write('COLOUR\tIUPredWS (Short)\t329440\n')
        if self.short_annotations and self.long_annotations:
            output_file.write('COMBINE\tIUPredWS (Long)\tIUPredWS (Short)')


class JRonnParser:
    def __init__(self, input_file):
        self.sequence_annotations = {}
        sequences_iterator = split_file(input_file, '>')
        assert next(sequences_iterator) == ''
        for seq in sequences_iterator:
            buffer = io.StringIO(seq.rstrip('\r\n'))
            seq_id = buffer.readline().split()[0]
            self.sequence_annotations[seq_id] = self.parse_annotations(buffer)
            buffer.close()

    @staticmethod
    def parse_annotations(input_file):
        input_file.readline()
        return [float(f) for f in input_file.readline().split() if f]

    def write_jalview_annotations(self, output_file):
        output_file.write('JALVIEW_ANNOTATION\n\n')
        for seq_id, annotations in self.sequence_annotations.items():
            output_file.write(
                'SEQUENCE_REF\t{id}\n'
                'LINE_GRAPH\tJronnWS (JRonn)\t'
                '<html>Protein Disorder with JronnWS - raw scores<br/>'
                'Above 0.5 indicates disorder</html>\t{annot}\n'
                'GRAPHLINE\tJronnWS (JRonn)\t0.5\t'
                'Above 0.5 indicates disorder\tff0000\n\n'
                .format(
                    id=seq_id,
                    annot='|'.join(map('{:.2f}'.format, annotations))
                )
            )
        output_file.write('COLOUR\tJronnWS (JRonn)\t23855a\n')


class AAConParser:
    def __init__(self, input_file):
        self.annotations = {}
        for line in input_file:
            line = line.rstrip()
            if not line:
                continue
            assert line.startswith('#')
            tokens = line[1:].split()
            self.annotations[tokens[0]] = list(map(float, tokens[1:]))

    def write_jalview_annotations(self, output_file):
        output_file.write('JALVIEW_ANNOTATION\n\n')
        for method, annotations in self.annotations.items():
            output_file.write(
                'BAR_GRAPH\t{method}\t{method}\t{annot}\n'
                .format(
                    method=method,
                    annot='|'.join(map('{:.4f}'.format, annotations))
                )
            )


def parse_ranges(text):
    """
    Parses comma separated list of ranges into a list of tuples.
    """
    return [
        tuple(int(x) for x in dom.split('-'))
        for dom in map(str.strip, text.split(',')) if dom
    ]


def parse_globplot(args):
    with open(args.input) as infile:
        parser = GlobPlotParser(infile)
    if args.feat:
        with open(args.feat, 'w') as outfile:
            parser.write_jalview_features(outfile)
    if args.annot:
        with open(args.annot, 'w') as outfile:
            parser.write_jalview_annotations(outfile)


def parse_disembl(args):
    with open(args.input) as infile:
        parser = DisemblParser(infile)
    if args.annot:
        with open(args.annot, 'w') as outfile:
            parser.write_jalview_annotations(outfile)
    if args.feat:
        with open(args.feat, 'w') as outfile:
            parser.write_jalview_features(outfile)


def parse_iupred(args):
    long_file = args.long and open(args.long)
    short_file = args.short and open(args.short)
    glob_file = args.glob and open(args.glob)
    parser = IUPredParser(short_file=short_file,
                          long_file=long_file, glob_file=glob_file)
    if args.annot:
        with open(args.annot, 'w') as outfile:
            parser.write_jalview_annotations(outfile)
    if args.feat:
        with open(args.feat, 'w') as outfile:
            parser.write_jalview_features(outfile)


def parse_jronn(args):
    with open(args.input) as infile:
        parser = JRonnParser(infile)
    if args.annot:
        with open(args.annot, 'w') as outfile:
            parser.write_jalview_annotations(outfile)


def parse_aacon(args):
    with open(args.input) as infile:
        parser = AAConParser(infile)
    if args.annot:
        with open(args.annot, 'w') as outfile:
            parser.write_jalview_annotations(outfile)


if __name__ == '__main__':
    parent_parser = ArgumentParser()
    subparsers = parent_parser.add_subparsers(dest='type')
    subparsers.required = True

    globplot_parser = subparsers.add_parser('globplot')
    globplot_parser.add_argument('--input', '-i', required=True)
    globplot_parser.add_argument('--annot', '-a')
    globplot_parser.add_argument('--feat', '-f')
    globplot_parser.set_defaults(func=parse_globplot)

    disembl_parser = subparsers.add_parser('disembl')
    disembl_parser.add_argument('--input', '-i', required=True)
    disembl_parser.add_argument('--annot', '-a')
    disembl_parser.add_argument('--feat', '-f')
    disembl_parser.set_defaults(func=parse_disembl)

    iupred_parser = subparsers.add_parser('iupred')
    iupred_parser.add_argument('--long', '-l')
    iupred_parser.add_argument('--short', '-s')
    iupred_parser.add_argument('--glob', '-g')
    iupred_parser.add_argument('--annot', '-a')
    iupred_parser.add_argument('--feat', '-f')
    iupred_parser.set_defaults(func=parse_iupred)

    jronn_parser = subparsers.add_parser('jronn')
    jronn_parser.add_argument('--input', '-i', required=True)
    jronn_parser.add_argument('--annot', '-a')
    jronn_parser.set_defaults(func=parse_jronn)

    aacon_parser = subparsers.add_parser('aacon')
    aacon_parser.add_argument('--input', '-i', required=True)
    aacon_parser.add_argument('--annot', '-a')
    aacon_parser.set_defaults(func=parse_aacon)

    args = parent_parser.parse_args()
    args.func(args)
