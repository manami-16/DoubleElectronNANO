from CRABClient.UserUtilities import config
import yaml
import datetime
import copy
from fnmatch import fnmatch
from argparse import ArgumentParser

production_tag = datetime.date.today().strftime('%Y%b%d')

config = config()
config.section_('General')
config.General.transferOutputs = True
config.General.transferLogs = True
config.General.workArea = 'DoubleElectronNANO_{:s}'.format(production_tag)

config.section_('Data')
config.Data.publication = False
config.Data.outLFNDirBase = '/store/group/cmst3/group/xee/tree_v1'

config.Data.inputDBS = 'global'

config.section_('JobType')
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'BParkingNano/test/run_nano_cfg.py'
config.JobType.maxJobRuntimeMin = 2000 ## default 3000
config.JobType.maxMemoryMB = 3500
config.JobType.allowUndistributedCMSSW = True

config.section_('User')
config.section_('Site')
# config.Site.storageSite = 'T3_US_CMU'
config.Site.storageSite = 'T2_CH_CERN'

if __name__ == '__main__':

  from CRABAPI.RawCommand import crabCommand
  from CRABClient.ClientExceptions import ClientException
  from http.client import HTTPException
  from multiprocessing import Process

  def submit(config):
      try:
          crabCommand('submit', config = config)
      except HTTPException as hte:
          print("Failed submitting task:",hte.headers)
      except ClientException as cle:
          print("Failed submitting task:",cle)

  parser = ArgumentParser()
  parser.add_argument('-y', '--yaml', default = 'BParkingNano/production/samples_INCLUSIVE_Run3_2023.yml', help = 'File with dataset descriptions')
  parser.add_argument('-f', '--filter', default='*', help = 'filter samples, POSIX regular expressions allowed')
  parser.add_argument('-r', '--lhcRun', type=int, default=3, help = 'Run 2 or 3 (default)')
  parser.add_argument('-yy', '--year', type=int, default=2023, help = 'Year of the dataset')
  parser.add_argument('-m', '--mode', type=str, default="reco", help= 'reco = apply skim, eff = disable all selections, vbf = apply vbf hlts')
  parser.add_argument('-s', '--saveAllNanoContent', type=bool, default=True, help= 'Save all nano content (default = True)')
  parser.add_argument('-sr', '--saveRegressionVars', type=bool, default=False, help='Save regression variables (default = False)')
  args = parser.parse_args()

  configs = []
  with open(args.yaml) as f:
    doc = yaml.load(f,Loader=yaml.FullLoader) # Parse YAML file
    common = doc['common'] if 'common' in doc else {'data' : {}}

    # loop over samples
    for sample, info in doc['samples'].items():
        # Input DBS
        input_dbs = info['dbs'] if 'dbs' in info else None
        isMC = info['isMC']
        version = info['version'] if 'version' in info else 'Z'

        config.Data.inputDBS = input_dbs if input_dbs is not None else 'global'
        config.Data.inputDataset = info['dataset']

        print(f'submitting -- {sample}')
        config.General.requestName = sample

        config.Data.splitting = 'FileBased' if isMC else 'LumiBased'
        if not isMC:
            config.Data.lumiMask = common['data']['lumiMask']
        else:
            config.Data.lumiMask = ''
            
        if 'userInputFiles' in info:
            config.Data.userInputFiles = info['userInputFiles']

        config.Data.unitsPerJob = common['data']['splitting']

        # globaltag = info.get(
        #     'globaltag',
        #     common[common_branch].get('globaltag', None)
        # )

        config.JobType.pyCfgParams = [
            'isMC={:.0f}'.format(int(isMC)),
            'reportEvery=5000',
            'tag={:s}'.format(production_tag),
            # 'globalTag={:s}'.format(globaltag), This is set in run_nano_cfg.py
            'lhcRun={:.0f}'.format(args.lhcRun),
            'year={:.0f}'.format(args.year),
            'mode={:s}'.format(args.mode),
            'saveAllNanoContent={:.0f}'.format(int(args.saveAllNanoContent)),
            'saveRegressionVars={:.0f}'.format(int(args.saveRegressionVars)),
            'version={:s}'.format(version)
        ]

        ext1 = {False:'data', True:'mc'}
        ext2 = {3 : 'Run3', 2 : 'Run2'}
        ext3 = {"eff" : "noskim", "reco" : "", "trg" : ""}
        ext4 = {True: 'allNano', False: ''}
        ext5 = {True: 'withRegVars', False: ''}

        output_flags = ["DoubleElectronNANO", ext2[args.lhcRun], str(args.year), ext1[isMC]]
        if args.mode == "eff":
            output_flags.append(ext3[args.mode])
        if args.saveAllNanoContent:
            output_flags.append(ext4[args.saveAllNanoContent])
        if args.saveRegressionVars:
            output_flags.append(ext5[args.saveRegressionVars])
        output_flags.append(production_tag)

        config.JobType.outputFiles = ['_'.join(output_flags)+'.root']
        config.Data.outLFNDirBase = '/store/group/cmst3/group/xee/tree_v1'

        if "HAHM" in sample:
            config.Data.outLFNDirBase += '/signalSamples/HAHM_DarkPhoton_13p6TeV_Nov2024'
        elif "Run20" in sample:
            config.Data.outLFNDirBase += '/data'
        else:
            config.Data.outLFNDirBase += '/backgroundSamples'

        last_subfolder_pieces = []

        if args.mode == "eff":
            last_subfolder_pieces.append('noskim')
        if args.saveAllNanoContent:
            last_subfolder_pieces.append('allnanoColl')
        if args.saveRegressionVars:
            last_subfolder_pieces.append('withRegVars')

        if len(last_subfolder_pieces) > 0:
            config.Data.outLFNDirBase += '/' + '_'.join(last_subfolder_pieces)

        print()
        print(config)
        config_copy = copy.deepcopy(config)
        configs.append(config_copy)
    print("Do you want to submit all task? (y/n)")
    if input().strip().lower() == 'y':
        for c in configs:
            # p = Process(target = submit, args=(c,))
            # p.start()
            # p.join()
            submit(c)
