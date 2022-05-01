# !/usr/bin/python
# -*- coding: utf-8 -*-
"""Quick script to search g3 directory.

Usage examples:

$ blaze run //experimental/users/szujoupris/search:search -- \
    --check_symmetry=True \
    --extract_value_from_key=False \
    --replace_pattern_of_files=False \
    --list_url_update_files=False

"""
import re
import os
import glob
import csv

from xxx import app
from xxx import flags
from xxx.xxx import text_format
from xxx.xxx import resources_pb2
from xxx.xxx import piper_api_wrapper

FLAGS = flags.FLAGS
flags.DEFINE_boolean('check_symmetry', False, 'whether to check symmetry')
flags.DEFINE_boolean('extract_value_from_key', False, 'whether to extract value from key')
flags.DEFINE_boolean('replace_pattern_of_files', False, 'whether to replace pattern of files')
flags.DEFINE_boolean('list_url_update_files', False, 'whether to list url and update files')

Source_Files_Regex = '/**/*/nlp/generation/data/cmn_tw/**/*.csv'
Search_Regex = [r'discoverability_default']
Edit_Workspace = 'GenX_okgoogle'
Source_File = '/**/*/nlp/generation/messages/assistant/home_automation/home_automation_cmn-TW.genx.textpb'
Match_File = '/**/*/nlp/generation/data/cmn_tw/production/common_nouns/readme_genres.md'
Pris_Workspace = '/**/*/GenX_xxx/'
Creator_CL = 444021133
Output_File = '/**/*/nlp/generation/data/cmn_tw/production/common_nouns/generic_nouns.csv'
Key = '_ProviderName' # r"provider_mid == '(.*)'"
GenXFile = text_format.Parse(open(Source_File, encoding='utf-8').read(), resources_pb2.Resources(), allow_unknown_extension=True)

def extract_value_from_key(of_msg=False, of_lex=False):  # to take more than one value
  key_value = {}
  genxfile = GenXFile
  if of_msg:
    template = genxfile.message_template
    for regex in Search_Regex:
      for (a, b) in template.items():
        if regex in a:
          all_variants = [variant.value for variant in b.variant]
          value = ','.join(all_variants)
          key_value[a] = value

  if of_lex:
    all_srcs = glob.glob(
        Source_Files_Regex, recursive=True)  # get all source files
    for key in open(Match_File, encoding='utf-8').readlines():
      for source_file in all_srcs:
        with open(source_file, 'r', encoding='utf_8', newline='') as csv_file:
          reader = csv.reader(csv_file)
          for fields in reader:
            mid_name = (fields[0], fields[1])
            if key.strip() in mid_name:  # type of row: list
              key_value[key] = mid_name[1]
              break

  print(key_value)

def replace_pattern_of_files():
  for file_to_read in glob.glob(Source_Files_Regex, recursive=True):
    replace_pattern(file_to_read)

def replace_pattern(file_to_read):
  with open(file_to_read, 'r', encoding='utf-8') as input_file:
    old_content = input_file.read()
    new_content = ''
    for regex in Search_Regex:
      if len(regex.findall(old_content)) > 0:
        new_content = regex.sub(r'(lex.Np lexicon', old_content)
    if new_content:
      file_to_write = file_to_read.replace('GenX_xxx', Edit_Workspace)
      with open(file_to_write, 'w', encoding='utf-8') as output_file:
        output_file.write(new_content)

def check_symmetry(of_condition=False, of_key=False, locale='cmn-TW'):
  creator_workspace = get_verticals_of_cl(locale)[0]
  for vertical in get_verticals_of_cl(locale)[1]:
    paths = dict(
        en=Pris_Workspace + vertical + '_en.genx.textpb',
        tw=Pris_Workspace + vertical + f'_{locale}.genx.textpb',
        meta=Pris_Workspace + vertical + '_0META.genx.textpb',
        pending=creator_workspace + vertical + f'_{locale}.genx.textpb')

    message = []

    if of_condition:
      en_mids = _GetItems(paths['en'], of_condition=True)[0]
      tw_mids = _GetItems(paths['tw'], of_condition=True)[0]
      pending_mids = _GetItems(paths['pending'], of_condition=True)[0]
      mids_to_update = en_mids - tw_mids
      missing_mids = en_mids - pending_mids
      mids_to_remove = pending_mids - en_mids
      list_length = len(_GetItems(paths['pending'], of_condition=True)[1])
      set_length = len(_GetItems(paths['pending'], of_condition=True)[0])
      duplicate = True if list_length != set_length else False

      if mids_to_update:
        message.append('Mids to update:\n  %r' % mids_to_update)
      if missing_mids:
        message.append('Missing mids:\n  %r' % missing_mids)
      if mids_to_remove:
        message.append('Mids to remove:\n  %r' % mids_to_remove)
      if duplicate:
        message.append('!DUPLICATE')
      summary = '\n'.join(message)

    if of_key:
      en_keys = _GetItems(paths['en'])
      tw_keys = _GetItems(paths['pending']) if os.path.isfile(
          paths['tw']) == False else _GetItems(
              paths['tw'])  # the directory of new files is absent from G3
      dnt_keys = _GetItems(paths['meta'], do_not_translate=True)
      pending_keys = _GetItems(paths['pending'])

      translate_keys = en_keys - dnt_keys
      missing_keys = translate_keys - pending_keys
      keys_to_remove = pending_keys - translate_keys

      if missing_keys:
        message.append('Missing keys:\n  %r' % missing_keys)
      if keys_to_remove:
        message.append('Keys to remove:\n  %r' % keys_to_remove)
      summary = vertical + '\n' + '\n\n'.join(message) + '\n'

    print(summary)

def get_verticals_of_cl(locale):
  piper = piper_api_wrapper.GetPiperApiWrapper()
  cl_info = piper.GetChange(change_number=Creator_CL)
  idap_workspace = cl_info.change_id.workspace_id.workspace_name
  creator = idap_workspace.split(':')[0]
  workspace = idap_workspace.split(':')[1]
  creator_workspace = f'/google/src/cloud/{creator}/{workspace}/'

  verticals = []
  for file in cl_info.source_files:
    path = file.source_file_id.workspace_path
    m = re.search(f'(.*)_{locale}.genx.textpb', path)
    if m == None:
      continue
    vertical = m.group(1)
    verticals.append(vertical)
  return (creator_workspace, verticals)


def _GetItems(path, of_condition=False, do_not_translate=False):
  if do_not_translate:
    msg_set_meta = text_format.ParseLines(
        open(path, encoding='utf_8'), resources_pb2.MessageSetMetadata())

  else:
    template = GenXFile.message_template

  items = set()
  list_items = list()
  toolchain_dict = {}
  if of_condition:
    for (a, b) in template.items():
      m = re.search(Key, a)
      if m == None:
        continue
      for variant in b.variant:  # first_of.
        for condition in variant.condition:
          items.add(condition)
          list_items.append(condition)
          break
      return (items, list_items)

  elif do_not_translate:
    all_keys = [(m.key, m.translation_readiness)
                for m in msg_set_meta.schema.message_schema]
    items = set(a for a, b in all_keys
                if (b == 3 or b == 4))  # dnt_keys & TRANSLATED_VIA_ZXX
    return items

  else:
    items = set(a for (a, b) in template.items())
    return items

def list_url_update_files():
  for file_name in glob.glob(Source_Files_Regex, recursive=True):
    with open(file_name, 'r', encoding='utf-8') as file:
      for line in file.readlines():
        m1 = re.search(r'use\s(.*?)\s', line)
        if m1 != None:
          wf_url = m1.group(1)
          m2 = re.search(r'/call/(.*)_cmn-TW', file_name)
          ss_name = re.sub(r'_', r' ', m2.group(1))
          layout = ('{:<50}{:>100}')
          print(layout.format(ss_name, wf_url))

def main(argv):
  if len(argv) > 1:
    raise app.UsageError('Too many command-line arguments.')

  if FLAGS.extract_value_from_key:
    extract_value_from_key(of_msg=False, of_lex=True)
  if FLAGS.check_symmetry:
    check_symmetry(of_condition=False, of_key=True, locale='cmn-TW')
  if FLAGS.replace_pattern_of_files:
    replace_pattern_of_files()
  if FLAGS.list_url_update_files:
    list_url_update_files()

if __name__ == '__main__':
  app.run(main)
