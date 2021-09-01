import enum
import re
import sys
from argparse import ArgumentParser
from collections import defaultdict, namedtuple, OrderedDict
from operator import itemgetter


class GraphType(enum.Enum):
  BAR_GRAPH = 'BAR_GRAPH'
  LINE_GRAPH = 'LINE_GRAPH'
  NO_GRAPH = 'NO_GRAPH'


Graph = namedtuple('graph', 'type, label, description, values')
Graphline = namedtuple('graphline', 'value, label, colour')


def print_annotation_row(graph, graphline=None, colour=None, file=None):
  row = "{type}\t{label}\t{description}\t{values}".format(
    type=graph.type.name,
    label=graph.label,
    description=graph.description,
    values=str.join('|', map('{0},{0}'.format, graph.values))
  )
  print(row, file=file)
  if graph.type == GraphType.LINE_GRAPH:
    if graphline is not None:
      print('GRAPHLINE\t{name}\t{value}\t{label}\t{colour}'.format(
        name=graph.label, value=graphline.value, label=graphline.label,
        colour=graphline.colour
      ), file=file)
    if colour is not None:
      print('COLOUR\t{name}\t{colour}'.format(name=graph.label, colour=colour), file=file)


Feature = namedtuple('feature', 'description, name, index, start, end, feature_type, score')

def print_feature_row(feature, file=None):
  def is_not_none(val): return val is not None
  print(str.join('\t', map(str, filter(is_not_none, feature))), file=file)


class IUPredReader:
  def __init__(self):
    self.glob_pattern = re.compile(
      r'# ([^\n]+)\n'
      r'Number of globular domains:\s*\d+\s*\n'
      r'((?:\s+globular domain\s+(\d)\.\s+(\d+) - (\d+)\s*\n)+)'
      r'> ?\1+\n[A-Za-z \n]+'
    )

  def run(self, args):
    long = args.long and self.read_annotations(open(args.long))
    short = args.short and self.read_annotations(open(args.short))
    glob = args.glob and self.read_domains(open(args.glob))
    if args.annot:
      with open(args.annot, 'w') as fp:
        self.print_annotations_file(short, long, fp)
    if args.feat:
      with open(args.feat, 'w') as fp:
        self.print_features_file(glob, fp)

  def read_annotations(self, file):
    annotations = OrderedDict()
    for line in file:
      if line.startswith('#'):
        annotations[line[1:].strip()] = annot = []
      else:
        annot.append(line.split()[2])
    return annotations

  def read_domains(self, file):
    text = file.read()
    domains = OrderedDict()
    for match in self.glob_pattern.finditer(text):
      sequence = match.group(1)
      domains[sequence] = re.findall(
        r'^\s+globular domain\s+\d+\.\s+(\d+) - (\d+)\s*$',
        match.group(2), re.MULTILINE
      )
    return domains

  def print_annotations_file(self, short=None, long=None, file=None):
    file = file or sys.stdout
    file.write('JALVIEW_ANNOTATION\n\n')
    if short is None and long is None: return
    sequences = (short or long).keys()
    for seq in sequences:
      file.write('SEQUENCE_REF\t{}\n'.format(seq))
      if long:
        graph = Graph(
          type=GraphType.LINE_GRAPH,
          label="IUPredWS (Long)",
          description="<html>Protein Disorder with IUPredWS - raw scores<br/>"
                      "Above 0.5 indicates disorder</html>",
          values=long[seq]
        )
        graphline = Graphline(
          value="0.5", label="Above 0.5 indicates disorder", colour="ff0000"
        )
        print_annotation_row(graph, graphline, '72144e', file=file)
      if short:
        graph = Graph(
          type=GraphType.LINE_GRAPH,
          label="IUPredWS (Short)",
          description="<html>Protein Disorder with IUPredWS - raw scores<br/>"
                      "Above 0.5 indicates disorder</html>",
          values=short[seq]
        )
        graphline = Graphline(
          value="0.5", label="Above 0.5 indicates disorder", colour="ff0000"
        )
        print_annotation_row(graph, graphline, '329440', file=file)
      if short and long:
        file.write('COMBINE\tIUPredWS (Long)\tIUPredWS (Short)\n')
      file.write('\n')

  def print_features_file(self, domains=None, file=None):
    file = file or sys.stdout
    file.write(
      'Globular Domain\t876d2a\n\n'
      'STARTGROUP\tIUPredWS\n'
    )
    if domains is not None:
      for seq, ranges in domains.items():
        for start, end in ranges:
          feature = Feature(
            description="Predicted globular domain",
            name=seq,
            index="-1",
            start=start,
            end=end,
            feature_type="Globular Domain",
            score=None
          )
          print_feature_row(feature, file=file)
    file.write('ENDGROUP\tIUPredWS\n')


class GlobPlotReader:
  def run(self, args):
    result = self.read_file(open(args.input))
    if args.feat:
      with open(args.feat, 'w') as fp:
        self.print_features_file(result, fp)
    if args.annot:
      with open(args.annot, 'w') as fp:
        self.print_annotations_file(result, fp)

  def read_file(self, file):
    result = OrderedDict()
    for line in file:
      if line == '\n':
        continue
      seq = re.match(r'^>\s?(.*\S)\s*$', line).group(1)
      doms = re.match(r'^# GlobDoms\s*((?:\d+-\d+(?:, )?)*)', next(file)).group(1)
      doms = [tuple(r.split('-')) for r in doms.split(', ')] if doms else []
      dis = re.match(r'^# Disorder\s*((?:\d+-\d+(?:, )?)*)', next(file)).group(1)
      dis = [tuple(r.split('-')) for r in dis.split(', ')] if dis else []
      next(file)
      annots = []
      for line in file:
        if line == '\n': break
        residue, dydx, raw, smoothed = line.split()
        annots.append(dydx)
      result[seq] = (doms, dis, annots)
    return result
      
  def print_annotations_file(self, data, file=None):
    file = file or sys.stdout
    file.write('JALVIEW_ANNOTATION\n\n')
    for seq, (doms, dis, annots) in data.items():
      file.write('SEQUENCE_REF\t{}\n'.format(seq))
      graph = Graph(
        type=GraphType.LINE_GRAPH,
        label="GlobPlotWS (Dydx)",
        description="<html>Protein Disorder with GlobPlotWS - raw scores<br/>"
                    "Above 0.0 indicates disorder</html>",
        values=annots
      )
      graphline = Graphline(
        value='0.0', label='Above 0.0 indicates disorder', colour='ff0000'
      )
      print_annotation_row(graph, graphline, '8123cc', file=file)
      file.write('\n')

  def print_features_file(self, data, file=None):
    file = file or sys.stdout
    file.write(
      'Protein Disorder\tc5b938\n'
      'Globular Domain\t876d2a\n\n'
      'STARTGROUP\tGlobPlotWS\n'
    )
    for seq, (doms, dis, annots) in data.items():
      for domain in doms:
        feature = Feature(
          description="Predicted globular domain",
          name=seq,
          index='-1',
          start=domain[0],
          end=domain[1],
          feature_type="Globular Domain",
          score=None
        )
        print_feature_row(feature, file)
      for region in dis:
        feature = Feature(
          description="Probable unstructured peptide region",
          name=seq,
          index='-1',
          start=region[0],
          end=region[1],
          feature_type="Protein Disorder",
          score=None
        )
        print_feature_row(feature, file=file)
    file.write('ENDGROUP\tGlobPlotWS\n')


class DisEMBLReader:
  def run(self, args):
    result = self.read_file(open(args.input))
    if args.annot:
      with open(args.annot, 'w') as fp:
        self.print_annotations_file(result, fp)
    if args.feat:
      with open(args.feat, 'w') as fp:
        self.print_features_file(result, fp)

  def read_file(self, file):
    result = OrderedDict()
    annots = None
    line = file.readline()
    while line:
      if line == '\n':
        line = file.readline()
        continue
      seq = re.match(r'^>\s?(.*\S)\s*$', line).group(1)
      coils = rem465 = hotloops = ()
      while True:
        line = file.readline()
        match = re.match(r'^# (COILS|REM465|HOTLOOPS)\s*((?:\d+-\d+(?:, )?)*)', line)
        if match is None: break
        ranges = [tuple(r.split('-')) for r in match.group(2).split(', ')] if match.group(2) else []
        if match.group(1) == 'COILS': coils = ranges
        elif match.group(1) == 'REM465': rem465 = ranges
        elif match.group(1) == 'HOTLOOPS': hotloops = ranges
      assert line == '# RESIDUE\tCOILS\tREM465\tHOTLOOPS\n'
      line = file.readline()
      annots = []
      while line:
        if not re.match(r'^[A-Za-z](?:\t\d+\.\d+){3}$', line): break
        residue, v_coil, v_rem465, v_hotloop = line.split()
        annots.append(v_rem465)
        line = file.readline()
      result[seq] = (coils, rem465, hotloops, annots)
    return result
      
  def print_annotations_file(self, data, file=None):
    file = file or sys.stdout
    file.write('JALVIEW_ANNOTATION\n\n')
    for seq, (coils, rem465, hotloops, annots) in data.items():
      file.write('SEQUENCE_REF\t{}\n'.format(seq))
      graph = Graph(
        type=GraphType.LINE_GRAPH,
        label="DisemblWS (REM465)",
        description="<html>Protein Disorder with DisemblWS - raw scores<br/>"
                    "Above 0.1204 indicates disorder</html>",
        values=annots
      )
      graphline = Graphline(
        value='0.1204', label='Above 0.1204 indicates disorder', colour='ff0000'
      )
      print_annotation_row(graph, graphline, '2385b0', file=file)
      file.write("\n")

  def print_features_file(self, data, file=None):
    file = file or sys.stdout
    file.write(
      'HOTLOOPS\t511e29\n'
      'REM465\t1e5146\n'
      'COILS\tcfdb48\n\n'
      'STARTGROUP\tDisemblWS\n'
    )
    for seq, (coils, rem465, hotloops, annots) in data.items():
      groups = [coils, rem465, hotloops]
      descs = ["Random coil", "Missing density", "Flexible loops"]
      types = ["COILS", "REM465", "HOTLOOPS"]
      for group, desc, ft_type in zip(groups, descs, types):
        for region in group:
          feature = Feature(
            description=desc,
            name=seq,
            index='-1',
            start=region[0],
            end=region[1],
            feature_type=ft_type,
            score=None
          )
          print_feature_row(feature, file=file)
      file.write('\n')
    file.write('ENDGROUP\tDisemblWS\n')


class JRonnReader:
  def run(self, args):
    annotations = self.read_annotations(open(args.input))
    if args.annot:
      with open(args.annot, 'w') as fp:
        self.print_annotations_file(annotations, fp)

  def read_annotations(self, file):
    line = file.readline()
    annotations = OrderedDict()
    while line:
      seq = re.match(r'^>\s?(.*\S)\s*$', line).group(1)
      residues = file.readline().split()
      values = file.readline().split()
      annotations[seq] = values
      assert file.readline() == '\n'
      line = file.readline()
    return annotations

  def print_annotations_file(self, annotations, file=None):
    file = file or sys.stdout
    file.write('JALVIEW_ANNOTATION\n\n')
    for seq, values in annotations.items():
      file.write('SEQUENCE_REF\t{}\n'.format(seq))
      graph = Graph(
        type=GraphType.LINE_GRAPH,
        label="JronnWS (JRonn)",
        description='<html>Protein Disorder with JronnWS - raw scores<br/>'
                    'Above 0.5 indicates disorder</html>',
        values=values
      )
      graphline = Graphline(
        value='0.5', label="Above 0.5 indicates disorder", colour="ff0000"
      )
      print_annotation_row(graph, graphline, '23855a', file=file)
      file.write("\n")


class AAConReader:
  def run(self, args):
    annotations = self.read_annotations(open(args.input))
    if args.annot:
      with open(args.annot, 'w') as fp:
        self.print_annotations_file(annotations, fp)

  def read_annotations(self, file):
    annotations = OrderedDict()
    for line in file:
      if line == '\n': continue
      m = re.match(r'^#(\w+) ((?:-?\d+\.\d+ ?)+)$', line)
      annotations[m.group(1)] = m.group(2).split()
    return annotations

  def print_annotations_file(self, annotations, file=None):
    file = file or sys.stdout
    file.write('JALVIEW_ANNOTATION\n\n')
    for method, values in annotations.items():
      graph = Graph(GraphType.BAR_GRAPH, method, method, values)
      print_annotation_row(graph, file=file)


class RNAAlifoldReader:
  float_pat = r'[+-]?(?:[0-9]*\.)?[0-9]+'
  seq_pat = r'[_\-a-zA-Z]+'
  structure_pat = r'[\.(){}\[\],]+'

  def run(self, args):
    data = self.read_structures(open(args.input))
    if args.alifold:
      data['contacts'] = self.read_alifold(open(args.alifold))
    if args.annot:
      with open(args.annot, 'w') as fp:
        self.print_annotations(data, fp)

  @staticmethod
  def read_structures(file):
    float_pat = RNAAlifoldReader.float_pat
    seq_pat = RNAAlifoldReader.seq_pat
    structure_pat = RNAAlifoldReader.structure_pat
    result = {}
    # first line is always an alignment
    alignment = file.readline().strip()
    assert re.match(rf'{seq_pat}$', alignment), "Alignment expected."
    result['alignment'] = alignment
    # second line is always a mfe
    structure, mfe_energy = file.readline().split(None, 1)
    assert re.match(rf'{structure_pat}$', structure), "MFE structure expected"
    match = re.match(rf'\(({float_pat}) *= *({float_pat}) *\+ *({float_pat})\)$', mfe_energy)
    assert match, "Energies expected after mfe structure"
    result['mfe'] = structure, match.group(1, 2, 3)
    # rest of the file depends on the parameters
    for line in file:
      if line == '\n':
        continue
      match = re.match(structure_pat, line)
      if match:
        structure = match.group(0)
        energy = line[match.end() + 1:]
        match = re.match(rf'\[({float_pat})\]$', energy)
        if match:
          result['partition'] = structure, (match.group(1),)
          continue
        match = re.match(rf'{{({float_pat}) *= *({float_pat}) *\+ *({float_pat}) *(d={float_pat})}}', energy)
        if match:
          result['centroid'] = structure, match.group(1, 2, 3, 4)
          continue
        match = re.match(rf'{{({float_pat}) *= *({float_pat}) *\+ *({float_pat}) *(MEA={float_pat})}}', energy)
        if match:
          result['mea'] = structure, match.group(1, 2, 3, 4)
          continue
        raise ValueError(f"Unrecognised line \"{line}\"")
      pattern = (rf'\s*frequency of mfe structure in ensemble ({float_pat}); '
                 rf'ensemble diversity ({float_pat})\s*')
      match = re.match(pattern, line)
      if match:
        structure, scores = result['partition']
        result['partition'] = structure, scores + match.group(1, 2)
    return result

  @staticmethod
  def read_alifold(file):
    # skip header
    file.readline()
    file.readline()
    contacts = defaultdict(list)
    for line in file:
      cols = line.split()
      assert len(cols) >= 6 or re.match(RNAAlifoldReader.structure_pat, line), \
        "Contact probabilities expected"
      if len(cols) < 6:
        break
      probability = float(cols[3][:-1])
      item = int(cols[0]), int(cols[1]), probability
      if probability > 0:
        contacts[item[0]].append(item)
        contacts[item[1]].append(item)
    for items in contacts.values():
      items.sort(key=itemgetter(2), reverse=True)
    return contacts

  @staticmethod
  def print_annotations(data, file=sys.stdout):
    structure_to_annotations = RNAAlifoldReader.structure_to_annotations
    file.write("JALVIEW_ANNOTATION\n\n")
    print(
      'NO_GRAPH', 'RNAalifold Consensus',
      'Consensus alignment produced by RNAalifold',
      '|'.join(data['alignment']), sep='\t', file=file
    )
    structure, scores = data['mfe']
    print(
      'NO_GRAPH', 'MFE structure', 
      'Minimum free energy structure. Energy: %s = %s + %s' % scores,
      structure_to_annotations(structure), sep='\t', file=file
    )
    if 'partition' in data and 'contacts' in data:
      structure, scores = data['partition']
      contacts = data['contacts']
      graph = []
      for i, char in enumerate(structure):
        i = i + 1
        if i in contacts:
          # second value (probability) of zeroth item (highest) of i-th column
          value = contacts[i][0][2] 
          tooltip = ('%i->%i: %.1f%%' % it for it in contacts[i])
          tooltip = str.join('; ', tooltip)
        else:
          value = 0.0
          tooltip = 'No data'
        graph.append(f'{value:.1f},{char},{tooltip}')
      print(
        'BAR_GRAPH', 'Contact Probabilities',
        "Base Pair Contact Probabilities. " +
        "Energy of Ensemble: %s, frequency: %s, diversity: %s." % scores,
        "|".join(graph), sep='\t', file=file
      )
    if 'centroid' in data:
      structure, scores = data['centroid']
      print(
        'NO_GRAPH', 'Centroid Structure',
        'Centroid Structure. Energy: %s = %s + %s, %s' % scores,
        structure_to_annotations(structure), sep='\t', file=file
      )
    if 'mea' in data:
      structure, scores = data['mea']
      print(
        "NO_GRAPH", "MEA Structure",
        "Maximum Expected Accuracy Values. %s = %s + %s, %s" % scores,
        structure_to_annotations(structure), sep='\t', file=file
      )
    file.write('\n')
    props = "scaletofit=true\tshowalllabs=true\tcentrelabs=false"
    if 'mfe' in data:
      print(f"ROWPROPERTIES\tMFE Structure\t{props}", file=file)
    if 'centroid' in data:
      print(f"ROWPROPERTIES\tCentroid Structure\t{props}", file=file)
    if 'mea' in data:
      print(f"ROWPROPERTIES\tMEA Structure\t{props}", file=file)


  @staticmethod
  def structure_to_annotations(structure):
    tokens = [
      f'S,{it}' if it != '.' else f',{it}' for it in structure
    ]
    return '|'.join(tokens)



if __name__ == '__main__':
  parent_parser = ArgumentParser()
  subparsers = parent_parser.add_subparsers(dest='type')
  subparsers.required = True

  globplot_parser = subparsers.add_parser('globplot')
  globplot_parser.add_argument('--input', '-i', required=True)
  globplot_parser.add_argument('--annot', '-a')
  globplot_parser.add_argument('--feat', '-f')
  globplot_parser.set_defaults(func=GlobPlotReader)

  disembl_parser = subparsers.add_parser('disembl')
  disembl_parser.add_argument('--input', '-i', required=True)
  disembl_parser.add_argument('--annot', '-a')
  disembl_parser.add_argument('--feat', '-f')
  disembl_parser.set_defaults(func=DisEMBLReader)

  iupred_parser = subparsers.add_parser('iupred')
  iupred_parser.add_argument('--long', '-l')
  iupred_parser.add_argument('--short', '-s')
  iupred_parser.add_argument('--glob', '-g')
  iupred_parser.add_argument('--annot', '-a')
  iupred_parser.add_argument('--feat', '-f')
  iupred_parser.set_defaults(func=IUPredReader)

  jronn_parser = subparsers.add_parser('jronn')
  jronn_parser.add_argument('--input', '-i', required=True)
  jronn_parser.add_argument('--annot', '-a')
  jronn_parser.set_defaults(func=JRonnReader)

  aacon_parser = subparsers.add_parser('aacon')
  aacon_parser.add_argument('--input', '-i', required=True)
  aacon_parser.add_argument('--annot', '-a')
  aacon_parser.set_defaults(func=AAConReader)

  rnaalifold_parser = subparsers.add_parser('rnaalifold')
  rnaalifold_parser.add_argument('input')
  rnaalifold_parser.add_argument('-a', '--alifold')
  rnaalifold_parser.add_argument('annot')
  rnaalifold_parser.set_defaults(func=RNAAlifoldReader)

  args = parent_parser.parse_args()
  args.func().run(args)
