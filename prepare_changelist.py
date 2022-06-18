# Lint as: python3
# -*- coding: utf-8 -*-
"""Create files for NLG tasks.

Usage examples:

$ python3 prepare_cl.py \
    --prepare_GenX_file True \
    --prepare_LA_file True \
    --bug_numbers 235289028 235289039 235289040 \
    --file_names analytics_utils analytics_insight analytics_metrics \
    --workflow_ids 00000000e2451207 00000000e2451218 00000000e2451229

"""
import os, re
import gspread
import argparse
from oauth2client.service_account import ServiceAccountCredentials

parser = argparse.ArgumentParser()
parser.add_argument('--prepare_GenX_file', default=False, type=bool, help='whether to prepare GenX file')
parser.add_argument('--prepare_LA_file', default=False, type=bool, help='whether to prepare lexical annotation file')
parser.add_argument('--load_from_trix_to_csv', default=False, type=bool, help='whether to load from trix to csv')
parser.add_argument('--create_readme', default=False, type=bool, help='whether to create readme')
parser.add_argument('--bug_numbers', default='', type=str, nargs='+', help='list of bug request numbers separated by space')
parser.add_argument('--file_names', default='', type=str, nargs='+', help='list of file names separated by space') # file_category
parser.add_argument('--workflow_ids', default='', type=str, nargs='+', help='list of Podium workflow ids separated by space')

args = parser.parse_args()

_Sheet_ID = '1-4kX1K5VCXaQYPvJGiKabIolh8MR4ZJrezNoeZS6GVc'
_Target_Dir = '/Users/poohholmes007/Desktop/data_science/testing/'
Auth_Info = 'ETL.json'
Desc_Regex = [
    ': KG identifier',
    ': the orthography that will be generated for each entity',
    ': the context in which the name is used']

class PrepareChangelist(object):

  def __init__(self):
    self.sheet_id = _Sheet_ID
    self.target_dir = _Target_Dir

  def _get_data(self):
    gc = gspread.service_account(filename=Auth_Info)
    sheet = gc.open_by_key(self.sheet_id)
    data = sheet.get_worksheet(0).get_all_values()
    return data

  def load_from_trix_to_csv(self):

    data = self._get_data()
    output_rows = [','.join(row) for row in data]
    annotation = '\n'.join(output_rows)
    return annotation

  def create_readme(self, bug_number, l_l, lsl, csc):

    readme_part1 = f"""# Readme file for: {l_l}.csv
        
## {csc}
        
This file contains lexical annotations for {lsl}.
These annotations were done manually by the Pygmalion ZH team.
The annotation work was tracked in b/{bug_number}.
        
Fields:
"""

    data = self._get_data()
    headers = data[0]
    descriptions = Desc_Regex
    fields = [i + j for i, j in zip(headers, descriptions)]
    readme_part2 = '* ' + '\n* '.join(fields) + '\n'
    readme = readme_part1 + readme_part2
    return readme

  def prepare_LA_file(self, bug_number, l_l, lsl, csc):

    annotation_path = os.path.join(self.target_dir, f'{l_l}.csv')
    readme_path = os.path.join(self.target_dir, f'readme_{l_l}.md')
    annotation = self.load_from_trix_to_csv()
    readme = self.create_readme(bug_number, l_l, lsl, csc)
    with open(
        annotation_path, 'w', encoding='utf-8') as csv, open(
            readme_path, 'w', encoding='utf-8') as md:
      csv.write(annotation)
      md.write(readme)
    
  def prepare_GenX_file(self, bug_number, lsl, workflow_id):
    # for future use
    print('Success!', bug_number, lsl, workflow_id)

def main():
    
  prepare_cl = PrepareChangelist()
  for item in zip(args.bug_numbers, args.file_names, args.workflow_ids):
    l_l = item[1]
    lsl = item[1].replace('_', ' ')
    csc = item[1].replace('_', ' ').title()

    if args.prepare_GenX_file:
      prepare_cl.prepare_GenX_file(item[0], lsl, item[2])
    if args.prepare_LA_file:
      prepare_cl.prepare_LA_file(item[0], l_l, lsl, csc)
    if args.load_from_trix_to_csv:
      prepare_cl.load_from_trix_to_csv()
    if args.create_readme:
      prepare_cl.create_readme(item[0], l_l, lsl, csc)
    
if __name__ == '__main__':
    main()
