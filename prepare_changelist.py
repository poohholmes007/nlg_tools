# Lint as: python3
# -*- coding: utf-8 -*-
"""Create changelist for NLG tasks.

Usage examples:    

$ blaze run //experimental/users/szujoupris/changelist:prepare_changelist -- \
    --prepare_LA_cl=True \
    --file_name=<file_name> --file_category=<file_category> \
    --bug_number=<bug_number> \
    --workflow_id=<workflow_id> \
    --i18n_trix=<trix_link>

"""
import os, re

from xxx import app
from xxx import flags
from xxx.xxx import trix as Trix
from xxx.xxx import piper_api_wrapper

FLAGS = flags.FLAGS
flags.DEFINE_boolean('prepare_GenX_cl', False, 'whether to prepare GenX changelist')
flags.DEFINE_boolean('prepare_LA_cl', False, 'whether to prepare lexical annotation changelist')
flags.DEFINE_boolean('load_from_trix_to_csv', False, 'whether to load from trix to csv')
flags.DEFINE_boolean('create_readme', False, 'whether to create readme')
flags.DEFINE_integer('bug_number', None, 'bug request number')
flags.DEFINE_string('file_name', None, 'suggested file name by bug request')
flags.DEFINE_string('file_category', None, 'suggeseted {file category}+ by bug request')
flags.DEFINE_string('i18n_trix', None, 'trix where annotations are made')
flags.DEFINE_string('workflow_id', None, 'Podium workflow id')

Sheet_ID = '14dec3IiVaLFm-M803w0rEMeXsMD2sw1IoiTTKols-zM'
Worksheet = 'LA_data'
Desc_Regex = [
    ': KG identifier',
    ': the orthography that will be generated for each entity',
    ': the context in which the name is used']

class PrepareChangelist(object):

  def __init__(self):
    self.file_name = FLAGS.file_name
    self.file_category = FLAGS.file_category if FLAGS.file_category else 'events/olympics'
    self.bug_number = FLAGS.bug_number
    self.i18n_trix = FLAGS.i18n_trix
    self.workflow_id = FLAGS.workflow_id
    self.l_l = self.file_name.replace(' ', '_')
    self.lsl = self.file_name
    self.csc = self.file_name.title()

  def _get_data(self):
    trix = Trix.TrixClient(trix_key=Sheet_ID)
    trix.SetWorksheet(sheet_name=Worksheet)
    data = trix.GetRows()
    return data

  def load_from_trix_to_csv(self):
    data = self._get_data()
    header = list(data[0].keys())
    header_row = ','.join(header)

    output_rows = []
    for n in range(len(data)):
      mid_name_etc = list(data[n].values())
      row = ','.join(mid_name_etc)
      output_rows.append(row)
    annotation = header_row + '\n' + '\n'.join(output_rows) + '\n'
    return annotation

  def create_readme(self):
    readme_part1 = f"""# Readme file for: {self.l_l}.csv
        
## {self.csc}
        
This file contains lexical annotations for {self.lsl}.
These annotations were done manually by the Pygmalion ZH team.
The annotation work was tracked in b/{self.bug_number}.
        
Fields:
"""
    data = self._get_data()
    header = list(data[0].keys())
    descriptions = Desc_Regex
    fields = [i + j for i, j in zip(header, descriptions)]
    readme_part2 = '* ' + '\n* '.join(fields) + '\n'
    readme = readme_part1 + readme_part2
    return readme

  def prepare_LA_cl(self):
    cl_desc = self._LADesc()
    target_workspace = 'LA_' + self.l_l
    piper = piper_api_wrapper.GetPiperApiWrapper()
    ws_name = piper.CreateWorkspace(name=target_workspace, description=cl_desc)
    piper.CreateChange(workspace_name=ws_name, description=cl_desc)

    target_dir = f'/google/src/cloud/szujoupris/{target_workspace}/google3/nlp/generation/data/cmn_tw/production/'
    annotation_path = os.path.join(target_dir, self.file_category,
                                   f'{self.l_l}.csv')
    readme_path = os.path.join(target_dir, self.file_category,
                               f'readme_{self.l_l}.md')
    annotation = self.load_from_trix_to_csv()
    readme = self.create_readme()
    
    with open(
        annotation_path, 'w', encoding='utf-8') as csv, open(
            readme_path, 'w', encoding='utf-8') as md:
      csv.write(annotation)
      md.write(readme)

  def _LADesc(self):
    cl_desc = f"""[ETA:d-MMM][cmn-TW] Develop Lexical Annotations for {self.csc}

develop according to b/{self.bug_number} and the corresponding [trix]({self.i18n_trix})

"""
    return cl_desc

  def prepare_GenX_cl(self):
    ws_name = 'GenX_' + self.l_l
    cl_desc = self._GenXDesc()

    command = f"""/google/data/ro/teams/podium/workflow/export_workflow \
--workflow_server_addr=blade:podium \
--workflow_id={self.workflow_id} \
--authoring_status=ANNOTATED \
--pwd=$PWD \
--update_minion_file=true \
--include_en_diffbase_cl \
--owner=PYGMALION

"""
    os.system('cd $(p4 g4d -f "%s") && g4 change -b %d --desc "%s"' %
              (ws_name, self.bug_number, cl_desc))
    os.system('cd $(p4 g4d -f "%s") && g4 sync #head' % ws_name)
    os.system('cd $(p4 g4d -f "%s") && %s' % (ws_name, command))

  def _GenXDesc(self):
    cl_desc = f"""[ETA:d-MMM][cmn-TW] Update GenX messages for {self.csc}"""
    return cl_desc

def main(argv):
  if len(argv) > 1:
    raise app.UsageError('WTF')

  prepare_cl = PrepareChangelist()
  if FLAGS.prepare_GenX_cl:
    prepare_cl.prepare_GenX_cl()
  if FLAGS.prepare_LA_cl:
    prepare_cl.prepare_LA_cl()
  if FLAGS.load_from_trix_to_csv:
    prepare_cl.load_from_trix_to_csv()
  if FLAGS.create_readme:
    prepare_cl.create_readme()

if __name__ == '__main__':
  app.run(main)
  
