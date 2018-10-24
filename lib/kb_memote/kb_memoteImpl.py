# -*- coding: utf-8 -*-
#BEGIN_HEADER
# The header block is where all import statments should live
import os
from Bio import SeqIO
from pprint import pprint, pformat
from AssemblyUtil.AssemblyUtilClient import AssemblyUtil
from KBaseReport.KBaseReportClient import KBaseReport
from Workspace.WorkspaceClient import Workspace
import cobrakbase
from cobra.core import Gene, Metabolite, Model, Reaction
#import memote.suite.cli.reports
from memote.suite.cli.reports import report
import memote.suite.api as api
from memote.suite.reporting import ReportConfiguration
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
        print("WOW IT DOES NOT WORK !", params, ctx)
        wsClient = Workspace(self.ws_url, token=ctx['token'])
        
        def get_object(wclient, oid, ws):
            res = wclient.get_objects2({"objects" : [{"name" : oid, "workspace" : ws}]})
            return res["data"][0]["data"]
        
        model = get_object(wsClient, params['model_id'], params['workspace'])
        
        print(model.keys())
        
        output = {'out_model_id' : params['model_id']}
        
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
