# -*- coding: utf-8 -*-
#BEGIN_HEADER
# The header block is where all import statments should live
import os
from Bio import SeqIO
from pprint import pprint, pformat
from Workspace.WorkspaceClient import Workspace as workspaceService
from KBaseReport.KBaseReportClient import KBaseReport
from kb_memote.kb_memote import KBaseMemote
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

        print("WOW IT DOES NOT WORK !", params)
        print("CTX", ctx)
        wsClient = workspaceService(self.workspaceURL, token=ctx['token'])
        
        def get_object(wclient, oid, ws):
            res = wclient.get_objects2({"objects" : [{"name" : oid, "workspace" : ws}]})
            return res["data"][0]["data"]
        
        #This is where the implementation code goes

        #('WOW IT DOES NOT WORK !', {u'model_id': u'e_coli_core.kb', u'media_id': u'e_coli_core.media', u'workspace': u'filipeliu:narrative_1505405117321', u'out_model_id': u'sdasd'})
        
        #get model and media from workspace
        model = get_object(wsClient, params['model_id'], params['workspace'])
        media = {}
        #kb_memote.snapshot(model, media)
        
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
