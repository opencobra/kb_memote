# -*- coding: utf-8 -*-
#BEGIN_HEADER
# The header block is where all import statments should live
from __future__ import print_function
import os
import uuid
from Bio import SeqIO
from pprint import pprint, pformat
from AssemblyUtil.AssemblyUtilClient import AssemblyUtil
from KBaseReport.KBaseReportClient import KBaseReport
from Workspace.WorkspaceClient import Workspace
from DataFileUtil.DataFileUtilClient import DataFileUtil
import cobrakbase
import cobra
from cobra.core import Gene, Metabolite, Model, Reaction
#import memote.suite.cli.reports
from memote.suite.cli.reports import report
import memote.suite.api as api
from memote.suite.reporting import ReportConfiguration

import urllib2

import pandas as pd

from os import listdir
from os.path import isfile, join
#END_HEADER


class kb_memote:
    '''
    Module Name:
    kb_memote

    Module Description:
    A KBase module: kb_memote
Brief description about memote
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = ""
    GIT_COMMIT_HASH = ""

    #BEGIN_CLASS_HEADER
    # Class variables and functions can be defined in this block
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR

        # Any configuration parameters that are important should be parsed and
        # saved in the constructor.
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        self.ws_url = config['workspace-url']
        #END_CONSTRUCTOR
        pass


    def runMemote(self, ctx, params):
        """
        The actual function is declared using 'funcdef' to specify the name
        and input/return arguments to the function.  For all typical KBase
        Apps that run in the Narrative, your function should have the
        'authentication required' modifier.
        :param params: instance of type "RunMemote" -> structure: parameter
           "workspace" of type "workspace_name" (A string representing a
           workspace name.), parameter "model_id" of type "model_id" (A
           string representing a model id.), parameter "out_model_id" of type
           "model_id" (A string representing a model id.), parameter
           "compounds" of list of type "EachCompound" -> structure: parameter
           "compound_id" of String, parameter "compound_name" of String
        :returns: instance of type "MemoteResults" -> structure: parameter
           "model_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN runMemote

        #This is where the implementation code goes
        #print("WOW IT DOES NOT WORK !", params, ctx)
        #print("setup Workspace")
        
        wsClient = Workspace(self.ws_url, token=ctx['token'])
        dfuClient = DataFileUtil(self.callback_url)
        
        def get_object_info_from_ref(ws, ref):
            return ws.get_object_info3({'objects' : [{'ref' : ref}]}
        )
        
        def get_object(wclient, oid, ws):
            res = wclient.get_objects2({"objects" : [{"name" : oid, "workspace" : ws}]})
            return res["data"][0]["data"]
        
        print("get workspace model", params['model_id'])
        kmodel = get_object(wsClient, params['model_id'], params['workspace'])
        
        media_constraints = None
        
        if 'media_id' in params and not params['media_id'] == "" and not params['media_id'] == None:
            print("MEDIA ID", params['media_id'])
            media = get_object(wsClient, params['media_id'], params['workspace'])
            media_constraints = cobrakbase.convert_media(media)
        
        
        if media_constraints == None:
            if 'gapfillings' in kmodel and len(kmodel['gapfillings']) > 0:
                print("Pulling media from gapfilling...", kmodel['gapfillings'])
                ref = kmodel['gapfillings'][0]['media_ref']
                ref_data = get_object_info_from_ref(wsClient, ref)['infos'][0]
                o_id = ref_data[1]
                o_ws = ref_data[7]
                o_data = get_object(wsClient, o_id, o_ws)
                media_constraints = cobrakbase.convert_media(o_data)
        
        print("Loading genome...", kmodel['genome_ref'])
        ref_data = get_object_info_from_ref(wsClient, kmodel['genome_ref'])['infos'][0]
        o_id = ref_data[1]
        o_ws = ref_data[7]
        genome = get_object(wsClient, o_id, o_ws)
        
        #print("model attributes", kmodel.keys())
        #print(dir())
        model = cobrakbase.convert_kmodel(kmodel, media_constraints)
        html = ""
        #print("COBRA Model", dir(model))
        
        solution = model.optimize()
        print("solution", solution)
        
        #use urls for now but later get from local
        data = urllib2.urlopen('https://raw.githubusercontent.com/ModelSEED/ModelSEEDDatabase/dev/Biochemistry/Aliases/Compounds_Aliases.tsv')
        cpd_df = pd.read_csv(data, sep='\t')
        
        data = urllib2.urlopen('https://raw.githubusercontent.com/ModelSEED/ModelSEEDDatabase/dev/Biochemistry/Aliases/Reactions_Aliases.tsv')
        rxn_df = pd.read_csv(data, sep='\t')

        data = urllib2.urlopen('https://raw.githubusercontent.com/ModelSEED/ModelSEEDDatabase/dev/Biochemistry/Structures/ModelSEED_Structures.txt')
        stru_df = pd.read_csv(data, sep='\t')
        
        structures  = cobrakbase.read_modelseed_compound_structures(stru_df)
        rxn_aliases = cobrakbase.read_modelseed_reaction_aliases(rxn_df)
        cpd_aliases = cobrakbase.read_modelseed_compound_aliases(cpd_df)
        
        #temp fix for 
        def get_old_alias(alias, feature, gene_aliases):
            if alias.startswith('EcoGene:'):
                gene_aliases[feature['id']]['ecogene'] = alias.split(':')[1]
            elif alias.startswith('UniProtKB/Swiss-Prot:'):
                gene_aliases[feature['id']]['uniprot'] = alias.split(':')[1]
            elif alias.startswith('NP_'):
                gene_aliases[feature['id']]['ncbiprotein'] = alias
            elif alias.startswith('ASAP:'):
                gene_aliases[feature['id']]['asap'] = alias.split(':')[1]
            elif alias.startswith('GI:'):
                gene_aliases[feature['id']]['ncbigi'] = alias
            elif alias.startswith('GeneID:'):
                gene_aliases[feature['id']]['ncbigene'] = alias.split(':')[1]
            else:
                1

        def read_genome_aliases_temp(genome):
            gene_aliases = {}
            for feature in genome['features']:
                gene_aliases[feature['id']] = {}
                if 'aliases' in feature and type(feature['aliases']) == list:
                    for alias in feature['aliases']:
                        if type(alias) == list:
                            for a in alias:
                                #risk parsing the first element
                                get_old_alias(a, feature, gene_aliases)
                        else:
                            get_old_alias(alias, feature, gene_aliases)
                            #print('discard', alias)
                #print(feature['aliases' in ])
            return gene_aliases
        
        gene_aliases = read_genome_aliases_temp(genome)
        
        for m in model.metabolites:
            seed_id = None
            if 'seed.compound' in m.annotation:
                seed_id = m.annotation['seed.compound']
            if seed_id in structures:
                m.annotation.update(structures[seed_id])
            if seed_id in cpd_aliases:
                m.annotation.update(cpd_aliases[seed_id])
                
        for r in model.reactions:
            seed_id = None
            if 'seed.reaction' in r.annotation:
                seed_id = r.annotation['seed.reaction']
            if seed_id in rxn_aliases:
                r.annotation.update(rxn_aliases[seed_id])
        
        for g in model.genes:
            if g.id in gene_aliases:
                g.annotation.update(gene_aliases[g.id])
        
        #for m in model.genes:
        #    print(m.id, m.annotation)
            
        a, results = api.test_model(model, results=True, skip=['test_thermodynamics'])
        config = ReportConfiguration.load()
        html = api.snapshot_report(results, config)
        
        #with open("report.html", "w") as html_file:
        #    print(html, file=html_file)
        
        report_folder = self.shared_folder
        
        f = open(report_folder + "/report.html", "w")
        f.write(html.encode('utf8'))
        
        cobra.io.write_sbml_model(model, report_folder + "/model.xml")
        #/kb/module/work/tmp/56ed386bf8024ea486ee4fa95421a995
        print("report_folder", report_folder)
        #os.makedirs(report_folder, 0755);
        onlyfiles = [f for f in listdir(report_folder) if isfile(join(report_folder, f))]
        print("Files:", onlyfiles)
        
        #shock_id = dfuClient.file_to_shock({
        #    'file_path' : report_folder,
        #    'make_handle' : 0,
        #    'pack' : 'zip'
        #})['shock_id']
        
        #print("shock_id:", shock_id)
        
        reportClient = KBaseReport(self.callback_url)
        report_params = {
            'direct_html_link_index' : 0,
            'workspace_name' : params['workspace'],
            'report_object_name' : 'runMemote_' + uuid.uuid4().hex,
            'objects_created' : [],
            'html_links' : [
                {'name' : 'report', 'description' : 'Memote HTML Report', 'path' : report_folder + "/report.html"}
            ],
            'file_links' : [
                {'name' : params['model_id'] + ".xml", 'description' : 'desc', 'path' : report_folder + "/model.xml"}
            ]
        }
        
        print("create_extended_report", report_params)

        reportInfo = reportClient.create_extended_report(report_params)
        
        print("reportInfo", reportInfo)
        
        output = {
            'report_name' : reportInfo['name'],
            'report_ref' : reportInfo['ref']
        }
        
        #END runMemote

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method runMemote return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
