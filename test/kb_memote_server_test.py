# -*- coding: utf-8 -*-
import unittest
import os  # noqa: F401
import json  # noqa: F401
import time
import requests

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint  # noqa: F401

from biokbase.workspace.client import Workspace as workspaceService
from kb_memote.kb_memoteImpl import kb_memote
from kb_memote.kb_memoteServer import MethodContext
from kb_memote.authclient import KBaseAuth as _KBaseAuth

from AssemblyUtil.AssemblyUtilClient import AssemblyUtil

class kb_memoteTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_memote'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'kb_memote',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL)
        cls.serviceImpl = kb_memote(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_kb_memote_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})  # noqa
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    #def load_fasta_file(self, filename, obj_name, contents):
        #f = open(filename, 'w')
        #f.write(contents)
        #f.close()
        #assemblyUtil = AssemblyUtil(self.callback_url)
        #assembly_ref = assemblyUtil.save_assembly_from_fasta({'file': {'path': #filename},
        #                                                      'workspace_name': #self.getWsName(),
        #                                                      'assembly_name': obj_name
        #                                                      })
        #return assembly_ref

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_run_memote_ok(self):
                        
        #iMR1_799 iJO1366_no_inte kb.Ec_core_flux1
        example1 = {
            'model_id': 'iMR1_799',
            'media_id': '',
            'workspace': 'filipeliu:narrative_1505345231093'
        }
        example2 = {
            'model_id': 'ecoli.model',
            'media_id': '',
            'workspace': 'filipeliu:narrative_1543990426496'
        }
        result = self.getImpl().runMemote(self.getContext(), example2)
        
        print("test_run_memote_ok", result)
        #assembly_ref = self.load_fasta_file(os.path.join(self.scratch, 'test1.fasta'),
        #                                    'TestAssembly',
        #                                    fasta_content)

        # Second, call your implementation
        #ret = self.getImpl().filter_contigs(self.getContext(),
        #                                    {'workspace_name': self.getWsName(),
        #                                     'assembly_input_ref': assembly_ref,
        #                                     'min_length': 10
        #                                     })

        # Validate the returned data
        #self.assertEqual(ret[0]['n_initial_contigs'], 3)
        #self.assertEqual(ret[0]['n_contigs_removed'], 1)
        #self.assertEqual(ret[0]['n_contigs_remaining'], 2)

    def test_filter_contigs_err1(self):
        print("test_filter_contigs_err2")
        #with self.assertRaises(ValueError) as errorContext:
        #    self.getImpl().filter_contigs(self.getContext(),
        #                                  {'workspace_name': self.getWsName(),
        #                                   'assembly_input_ref': '1/fake/3',
        #                                   'min_length': '-10'})
        #self.assertIn('min_length parameter cannot be negative', str(errorContext.exception))

    def test_filter_contigs_err2(self):
        print("test_filter_contigs_err2")
        #with self.assertRaises(ValueError) as errorContext:
        #    self.getImpl().filter_contigs(self.getContext(),
        #                                  {'workspace_name': self.getWsName(),
        #                                   'assembly_input_ref': '1/fake/3',
        #                                   'min_length': 'ten'})
        #self.assertIn('Cannot parse integer from min_length parameter', #str(errorContext.exception))
