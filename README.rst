WebNode EX
==========

`WebNode Ex` is a data collector, using coroutine to gather function calls and aggregate, using tree to solve dependency.

Usage:
---

1. Implement Drivers. Examples(DummyRPC, DummyReids) in webnodeex/dummy.py
2. Implement RootNode. Example(DummyMediumYieldRoot) in webnode/mediumdummy.py
3. Implement the nodes, and declare functions in `register()`, declare children in `children()`. Examples in webnode/mediumdummy.py:

::
    class Node1(MediumYieldNode):

       def __init__(self, i):
           super(Node1, self).__init__()
           self.i = i

       def register(self):
           d1, d2, self.d3 = yield [
               self.dummy_rpc.call_by_id(self.i),
               self.dummy_rpc.call_by_id(2),
               [self.dummy_rpc.call_by_id(i) for i in range(1, 6)],
           ]
           print d1, d2, self.d3

       def children(self):
           node1, nodes = yield [
               Node2(),
               [NodePlus2(i=x) for x in self.d3],
           ]

4.  run root's method `gao()`
