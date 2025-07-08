from argparse import ArgumentParser

from glob import glob
from io import StringIO
import csv
import os
import sys
import re
import subprocess

class Marker:
  def __init__(self, title):
    self.title = title
    self.tests = {}
    self.headers = None
    self.current = None
    self.comments = None
    self.results = None

  def save(self):
    if self.current:
      if self.headers is None:
        self.headers = list(self.results.keys())

      self.tests[self.current] = (self.results, self.comments)
      self.current = None

  def test(self, name):
    self.save()
    self.current = name
    self.comments = []
    self.results = {}

  def comment(self, comment):
    self.comments.append(comment)

  def get_test_marks(self, test):
    return [float(v) if not t else v for v, _, _, t in self.tests[test][0].values()]

  def get_test_mark(self, test):
    results = self.tests[test][0]
    weight = sum([w for _, w, _, t in results.values() if not t])
    cap = min([c for v, c, _, t in results.values() if t and v] + [1])
    return min(sum([v * w for v, w, _, _ in results.values()]) / weight, cap)

  def get_final_mark(self):
    return sum(map(self.get_test_mark, self.tests.keys())) / len(self.tests)

  def mark(self, name, value, weight=1, description=None):
    if self.headers:
      if name not in self.headers:
        raise ValueError('Invalid mark name')
    if name in self.results:
      weight = weight if weight != 1 else self.results[name][1]
      description = description or self.results[name][2]
    self.results[name] = (value, weight, description, False)

  def cap(self, name, value, cap, description=None):
    if self.headers:
      if name not in self.headers:
        raise ValueError('Invalid mark name')
    if name in self.results:
      cap = cap if cap != 1 else self.results[name][1]
      description = description or self.results[name][2]
    self.results[name] = (value, cap, description, True)

  def csv(self):
    with StringIO() as file:
      writer = csv.writer(file)
      writer.writerow(['Test'] + self.headers + ['Total'])
      for test in self.tests:
        results = self.get_test_marks(test)
        writer.writerow([test] + [100 * v for v in results] + [100 * self.get_test_mark(test)])
      return file.getvalue()

  def __str__(self):
    # Header
    s = '## {}\n\n----------------------------\n\n'.format(self.title)

    if len(self.tests) == 0:
      return s + 'No tests yet.'

    # Criteria
    weights = []
    maxdesc = len('Description')
    master_test = next(iter(self.tests.values()))
    for header in self.headers:
      mark = master_test[0][header]
      # Description lengths
      if mark[2]:
        maxdesc = max(maxdesc, len(mark[2]))
      # Description lengths
      if mark[3] == 0:
        weights.append(mark[1])

    totalweight = sum(weights)

    s += '### Criteria\n\n'
    form = '|{{:12}}|{{:10}}|{{:{}}}|\n'.format(maxdesc)
    s += form.format('Name', 'Weight', 'Description')
    s += form.format('-' * 12, '-' * 10, '-' * maxdesc)
    form = '|{{:12}}|{{:>5.1f}}%    |{{:{}}}|\n'.format(maxdesc)
    form2 = '|{{:12}}|{{:>5.1f}}% cap|{{:{}}}|\n'.format(maxdesc)

    for header in self.headers:
      mark = master_test[0][header]
      if mark[3]:
        s += form2.format(header, 100 * mark[1], mark[2] or '')
      else:
        s += form.format(header, 100 * mark[1] / totalweight, mark[2] or '')

    # Results
    s += '\n### Results\n\n'
    cols = len(self.headers) + 1
    s += ('|{:20}|' + '{:>12} |' * cols).format('Test', *(self.headers + ['Marks'])) + '\n'
    s += ('|{:20}|' + '{:>12} |' * cols).format('-' * 20, *['-' * 12 for _ in range(cols)]) + '\n'
    # Lines
    cf = [master_test[0][h] for h in self.headers]
    cf = ['      {:>5.1f}% |' if not t else '       {:>5s} |' for _, _, _, t in cf]
    cf = ''.join(cf)
    form = '|{:20}|' + cf + '      {:>5.1f}% |\n'
    bool2yn = lambda x: 'Yes' if x else 'No'
    for test in self.tests.keys():
      marks = self.get_test_marks(test)
      s += form.format(test, *([100 * v if type(v) is float else bool2yn(v) for v in marks] + [100 * self.get_test_mark(test)]))

    # Summary
    s += ('|{:20}|' + '{:>12} |' * cols + '\n').format(
      '**Total**', *(list(' ' * (cols - 1)) + ['**{:>.1f}%**'.format(100 * self.get_final_mark())])
    )

    # Comments
    added_heading = False
    for test in self.tests:
      comments = self.tests[test][1]
      if comments:
        if not added_heading:
          s += '\n### Comments\n\n'
          added_heading = True
        s += '- {}:\n'.format(test)
        for comment in comments:
          s += '  - {}\n'.format(comment)
    return s + '\n'

# Mode 1
def mark_chk(out, exp, marker, weight_multiplier=1):
  marker.mark('Format', 0, weight=0.05*weight_multiplier,
    description='Formatting of output')
  marker.mark('Cycles', 0, weight=0.95*weight_multiplier,
    description='Correct duplicate sequences')

  out_lines = out.split('\n')
  exp_lines = exp.split('\n')

  format_mark = 1
  pattern = re.compile('^[ACGT]+ \d+ \d+$')
  total = len(exp_lines)
  count = 0
  if exp == 'None':
    if out == exp: count = 1
  elif 'ERROR' in exp:
    if exp in out_lines:
      out_lines.remove(exp)
      count = 1
      for line in out_lines:
        if 'ERROR' in line:
          count = 0
          break
  else:
    for i, line in enumerate(out_lines):
      if not line: continue

      # Format mark
      if not pattern.match(line):
        marker.comment('Invalid formatting on line {}'.format(i + 1))
        format_mark = 0

      # Logic mark
      if line in exp_lines:
        exp_lines.remove(line)
        count += 1
      else:
        count -= 1

  count = max(0, count)
  marker.mark('Format', format_mark)
  marker.mark('Cycles', count / total)
  return marker

# Mode 2
def mark_bf(out, exp, marker, weight_multiplier=1):
  marker.mark('Format', 0, weight=0.05*weight_multiplier,
    description='Formatting of output')
  marker.mark('Repititions', 0, weight=0.95*weight_multiplier,
    description='Correct sequences with no duplicate box cycles')

  out_lines = out.split('\n')
  exp_lines = exp.split('\n')

  format_mark = 1
  pattern = re.compile('^\d+ - [ACGT]+$')
  total = len(exp_lines)
  count = 0
  exp_index = 0
  for i, line in enumerate(out_lines):
    if not line: continue

    # Format mark
    if not pattern.match(line):
      marker.comment('Invalid formatting on line {}'.format(i))
      format_mark = 0
      continue

    # Logic mark
    if exp_index < total and exp_lines[exp_index] == line:
      count += 1
      exp_index += 1
    else:
      count -= 1

  count = max(0, count)
  marker.mark('Format', format_mark)
  marker.mark('Repititions', count / total)
  return marker

# Mode 3
def mark_opt(out, exp, test_path, test, marker, weight_multiplier=1):
  marker.mark('Format', 0, weight=0.05*weight_multiplier,
    description='Formatting of output')
  marker.mark('Sequence', 0, weight=0.95*weight_multiplier,
    description='Length of sequence generated in given time without box cycle repititions')

  # Format mark
  format_mark = 1
  pattern = re.compile('^\d+ - [ACGT]+$')
  if not pattern.match(out):
    marker.comment('Invalid format of sequence')
    format_mark = 0

  marker.mark('Format', format_mark)

  num = int(test[3:])
  if num <= 20:
    num = [1, 2, 3, 2, 3, 13, 5, 15, 13, 5, 15, 13, 5, 15, 13, 5, 15, 13, 5, 15][num-1]
    with open('{}/mode2/gen{}/ans.txt'.format(test_path, num)) as f:
      possibilites = f.read().strip().split('\n')
  else:
    with open('temp.in', 'w') as f:
      f.write(out.split(' ')[2])
    subprocess.run(['../src/maxseq', '1', 'temp.in'])
    os.remove('temp.in')
    with open('../out/temp_chk.txt', 'r') as f:
      output = f.read().strip()
    os.remove('../out/temp_chk.txt')

    if output == 'None':
      possibilites = [out]

  # Logic mark
  max_len = len(exp)
  if out not in possibilites:
    mark = 0
  else:
    mark = min(len(out) / max_len, 1.0)

  marker.mark('Sequence', mark)
  return marker


if __name__ == '__main__':
  parser = ArgumentParser(description='Script to mark RW214 2022 project')
  parser.add_argument('mode', metavar='mode', type=int, choices=[1, 2, 3])
  parser.add_argument('-p', '--test-path', type=str, default='tests')
  parser.add_argument('-r', '--rubric-path', type=str, default=None)
  parser.add_argument('-c', '--csv-path', type=str, default=None)

  args = parser.parse_args()
  args.mode -= 1

  mark_func = [mark_chk, mark_bf, mark_opt][args.mode]
  mode_ext = ['chk', 'bf', 'opt'][args.mode]
  title = ['(1) Checker', '(2) Brute Force Generator', '(3) Optimizer'][args.mode]
  args.mode += 1

  marker = Marker(title)
  for test in glob('{}/mode{}/*'.format(args.test_path, args.mode)):
    test = os.path.basename(test)
    marker.test(test)

    try:
      with open('../out/{}_{}.out'.format(test, mode_ext)) as f:
        output = f.read().strip()
      with open('../out/{}_{}.err'.format(test, mode_ext)) as f:
        error = f.read().strip()
      with open('{}/mode{}/{}/ans.txt'.format(args.test_path, args.mode, test)) as f:
        expected = f.read().strip()
      if 'error' not in test:
        with open('../out/{}_{}.txt'.format(test, mode_ext)) as f:
          output_file = f.read().strip()
      else:
        output_file = error

      marker.cap('Errors', True if 'Exception' in error or 'Warning' in error
        or 'Time limit' in error else False, 0.6, description='Program executed with errors')
      marker.cap('StdOut', True if output.strip() else False, 0.95,
        description='Printed to standard output')
      marker.mark('Compiled', 'Compilation error' not in output, weight=0.5,
        description='Program compiled with no errors')
      if args.mode == 3:
        mark_func(output_file, expected, args.test_path, test, marker, weight_multiplier=9.5)
      else:
        mark_func(output_file, expected, marker, weight_multiplier=9.5)
      marker.save()
    except Exception as e:
      print('Failed to mark: {}'.format(test), file=sys.stderr)
      print(e, file=sys.stderr)

  if args.rubric_path:
    try:
      with open(args.rubric_path, 'a') as f:
        f.write(str(marker))
    except:
      print('Failed to write rubric', file=sys.stderr)

  if args.csv_path:
    try:
      with open(args.csv_path, 'w') as f:
        f.write(str(marker.csv()))
    except:
      print('Failed to write CSV', file=sys.stderr)

  print(marker.get_final_mark() * 100)
