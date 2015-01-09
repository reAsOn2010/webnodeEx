#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from webnodeex.dummy import DummyRPC
from webnodeex.mediumdummy import Root
from webnodeex.proxy import ClientCenter


class MediumYieldNodeTest(unittest.TestCase):

    def setUp(self):
        ClientCenter.put('dummy_rpc', DummyRPC())
        self.root = Root()

    def test_gather_func(self):
        self.root.gao()
