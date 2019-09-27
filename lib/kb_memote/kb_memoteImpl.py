# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import uuid
import cobra
import cobrakbase

from cobrakbase.core.model import KBaseFBAModel
from cobrakbase.core import KBaseGenome
from cobrakbase.core import KBaseBiochemMedia
from cobrakbase.core.converters import KBaseFBAModelToCobraBuilder

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.WorkspaceClient import Workspace
from installed_clients.kb_cobrapyClient import kb_cobrapy

import memote.suite.api as memote_api
from memote.suite.reporting import ReportConfiguration
#END_HEADER


class kb_memote:
    '''
    Module Name:
    kb_memote

    Module Description:
    A KBase module: kb_memote
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.2.0"
    GIT_URL = ""
    GIT_COMMIT_HASH = ""

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        self.ws_url = config['workspace-url']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_memote(self, ctx, params):
        """
        :param params: instance of type "RunMemoteParams" -> structure:
           parameter "workspace" of String, parameter "model_id" of String,
           parameter "media_id" of String, parameter "out_model_id" of String
        :returns: instance of type "RunMemoteResults" -> structure: parameter
           "model_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_memote
        print(params)
        kbase_api = cobrakbase.KBaseAPI(ctx['token'], config={'workspace-url' : self.ws_url})
        modelseed = cobrakbase.modelseed.from_local('/kb/module/data/ModelSEEDDatabase')
        
        kmodel_data = kbase_api.get_object(params['model_id'], params['workspace'])
        fbamodel = KBaseFBAModel(kmodel_data)
        
        builder = KBaseFBAModelToCobraBuilder(fbamodel)
        
        if 'genome_ref' in kmodel_data:
            logging.info("Annotating model with genome information: %s", kmodel_data['genome_ref'])
            ref_data = kbase_api.get_object_info_from_ref(kmodel_data['genome_ref'])
            genome_data = kbase_api.get_object(ref_data.id, ref_data.workspace_id)
            builder.with_genome(KBaseGenome(genome_data))
            
        media = None
        
        if 'media_id' in params and not params['media_id'] == "" and not params['media_id'] == None:
            print("MEDIA ID", params['media_id'])
            media_data = kbase_api.get_object(params['media_id'], params['workspace'])
            media = KBaseBiochemMedia(media_data)
            
        if media == None:
            if 'gapfillings' in kmodel_data and len(kmodel_data['gapfillings']) > 0:
                print("Pulling media from gapfilling...", kmodel_data['gapfillings'])
                ref = kmodel_data['gapfillings'][0]['media_ref']
                ref_data = kbase_api.get_object_info_from_ref(ref)
                media_data = kbase_api.get_object(ref_data.id, ref_data.workspace_id)
                media = KBaseBiochemMedia(media_data)
                
        if not media == None:
            builder.with_media(media)
                
        #converts to cobra model object with builder
        model = builder.build()
        cobrakbase.annotate_model_with_modelseed(model, modelseed)

        #modelseed = cobrakbase.modelseed.from_local('/kb/module/data/ModelSEEDDatabase-dev')
        #print(cobrakbase.annotate_model_with_modelseed(model, modelseed))
        a, results = memote_api.test_model(model, results=True, skip=['test_thermodynamics'])
        config = ReportConfiguration.load()
        html = memote_api.snapshot_report(results, config)
        
        report_folder = self.shared_folder
        
        with open(report_folder + "/report.html", 'w') as f:
            f.write(html)
        cobra.io.write_sbml_model(model, report_folder + "/model.xml")
        
        report_client = KBaseReport(self.callback_url)
        report_params = {
            'direct_html_link_index' : 0,
            'workspace_name' : params['workspace'],
            'report_object_name' : 'run_memote_' + uuid.uuid4().hex,
            'objects_created' : [],
            'html_links' : [
                {'name' : 'report', 'description' : 'Memote HTML Report', 'path' : report_folder + "/report.html"}
            ],
            'file_links' : [
                {'name' : params['model_id'] + ".xml", 'description' : 'desc', 'path' : report_folder + "/model.xml"}
            ]
        }
        
        report_info = report_client.create_extended_report(report_params)
        
        output = {
            'report_name' : report_info['name'],
            'report_ref' : report_info['ref']
        }
        
        #END run_memote
        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_memote return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def run_kb_memote(self, ctx, params):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_kb_memote
        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': {'objects_created':[],
                                                'text_message': params['parameter_1']},
                                                'workspace_name': params['workspace_name']})
        output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref'],
        }
        #END run_kb_memote

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_kb_memote return value ' +
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
