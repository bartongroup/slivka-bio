import enum
import re
import sys
from argparse import ArgumentParser
from collections import namedtuple, OrderedDict


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
      r'# ([\w ]+)\n'
      r'Number of globular domains:\s*\d+\s*\n'
      r'((?:\s+globular domain\s+(\d)\.\s+(\d+) - (\d+)\s*\n)+)'
      r'> ?\1+\n[A-Za-z \n]+'
    )
    self.annot_pattern = re.compile(
      r'# ([\w ]+)\n((?: *\d+ [A-Za-z] +\d+\.\d+\n)+)'
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
    text = file.read()
    annotations = OrderedDict()
    for match in self.annot_pattern.finditer(text):
      sequence = match.group(1)
      annotations[sequence] = re.findall(
        r'^ *\d+ [A-Za-z] +(\d+\.\d+)$', match.group(2), re.MULTILINE
      )
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
      seq = re.match(r'^> ?(\w+)$', line).group(1)
      doms = re.match(r'^^# GlobDoms\s*((?:\d+-\d+(?:, )?)*)', next(file)).group(1)
      doms = [tuple(r.split('-')) for r in doms.split(', ')] if doms else []
      dis = re.match(r'^^# Disorder\s*((?:\d+-\d+(?:, )?)*)', next(file)).group(1)
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
      seq = re.match(r'^> ?(\w+)$', line).group(1)
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
      seq = re.match(r'> ?([\w ]+)$', line).group(1)
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

  # aacon_parser = subparsers.add_parser('aacon')
  # aacon_parser.add_argument('--input', '-i', required=True)
  # aacon_parser.add_argument('--annot', '-a')
  # aacon_parser.set_defaults(func=AAConReader)

  args = parent_parser.parse_args()
  args.func().run(args)
