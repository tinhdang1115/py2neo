#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Copyright 2011-2015, Nigel Small
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from py2neo import  Node, Relationship, cast, cast_node, cast_relationship
from test.util import Py2neoTestCase


def assert_node(node, *labels, **properties):
    assert isinstance(node, Node)
    assert node.labels() == set(labels)
    assert dict(node) == properties


class GraphyCastTestCase(Py2neoTestCase):

    def test_cast(self):
        assert cast(None) is None

    def test_can_cast_node(self):
        alice = Node(name="Alice")
        self.graph.create(alice)
        casted = cast(alice)
        assert isinstance(casted, Node)
        assert casted.remote
        assert casted["name"] == "Alice"

    def test_can_cast_dict(self):
        casted = cast({"name": "Alice"})
        assert isinstance(casted, Node)
        assert not casted.remote
        assert casted["name"] == "Alice"

    def test_can_cast_rel(self):
        a = Node()
        b = Node()
        ab = Relationship(a, "KNOWS", b)
        self.graph.create(ab)
        casted = cast(ab)
        assert isinstance(casted, Relationship)
        assert casted.remote
        assert casted.start_node() == a
        assert casted.type() == "KNOWS"
        assert casted.end_node() == b

    def test_can_cast_3_tuple(self):
        alice = Node()
        bob = Node()
        casted = cast((alice, "KNOWS", bob))
        assert isinstance(casted, Relationship)
        assert not casted.remote
        assert casted.start_node() is alice
        assert casted.type() == "KNOWS"
        assert casted.end_node() is bob

    def test_can_cast_4_tuple(self):
        alice = Node()
        bob = Node()
        casted = cast((alice, "KNOWS", bob, {"since": 1999}))
        assert isinstance(casted, Relationship)
        assert not casted.remote
        assert casted.start_node() is alice
        assert casted.type() == "KNOWS"
        assert casted.end_node() is bob
        assert casted["since"] == 1999


class NodeCastTestCase(Py2neoTestCase):

    def test_cast_node(self):
        alice = Node("Person", "Employee", name="Alice", age=33)
        assert cast_node(None) is None
        assert cast_node(alice) is alice
        assert_node(cast_node("Person"), "Person")
        assert_node(cast_node({"name": "Alice"}), name="Alice")
        assert_node(cast_node(("Person", "Employee", {"name": "Alice", "age": 33})),
                    "Person", "Employee", name="Alice", age=33)
        with self.assertRaises(TypeError):
            cast_node(3.14)

    
class RelationshipCastTestCase(Py2neoTestCase):
    
    def test_can_cast_relationship(self):
        a = Node()
        b = Node()
        ab = Relationship(a, "KNOWS", b)
        self.graph.create(a | b | ab)
        casted = cast_relationship(ab)
        assert isinstance(casted, Relationship)
        assert casted.remote
        assert casted.start_node() == a
        assert casted.type() == "KNOWS"
        assert casted.end_node() == b
        
    def test_cannot_cast_0_tuple(self):
        with self.assertRaises(TypeError):
            cast_relationship(())

    def test_cannot_cast_1_tuple(self):
        with self.assertRaises(TypeError):
            cast_relationship(("Alice",))

    def test_cannot_cast_2_tuple(self):
        with self.assertRaises(TypeError):
            cast_relationship(("Alice", "KNOWS"))

    def test_can_cast_3_tuple(self):
        alice = Node()
        bob = Node()
        casted = cast_relationship((alice, "KNOWS", bob))
        assert isinstance(casted, Relationship)
        assert not casted.remote
        assert casted.start_node() == alice
        assert casted.type() == "KNOWS"
        assert casted.end_node() == bob
        
    def test_can_cast_3_tuple_with_unbound_rel(self):
        alice = Node()
        bob = Node()
        casted = cast_relationship((alice, ("KNOWS", {"since": 1999}), bob))
        assert isinstance(casted, Relationship)
        assert not casted.remote
        assert casted.start_node() == alice
        assert casted.type() == "KNOWS"
        assert casted.end_node() == bob
        assert casted["since"] == 1999
        
    def test_can_cast_4_tuple(self):
        alice = Node()
        bob = Node()
        casted = cast_relationship((alice, "KNOWS", bob, {"since": 1999}))
        assert isinstance(casted, Relationship)
        assert not casted.remote
        assert casted.start_node() == alice
        assert casted.type() == "KNOWS"
        assert casted.end_node() == bob
        assert casted["since"] == 1999
        
    def test_cannot_cast_6_tuple(self):
        with self.assertRaises(TypeError):
            cast_relationship(("Alice", "KNOWS", "Bob", "foo", "bar", "baz"))

    def test_can_cast_from_tuple_of_entities(self):
        a = Node()
        b = Node()
        r = Relationship(a, "TO", b)
        casted = cast_relationship((a, r, b))
        assert isinstance(casted, Relationship)
        assert not casted.remote
        assert casted.start_node() == a
        assert casted.type() == "TO"
        assert casted.end_node() == b

    def test_can_cast_relationship_with_integer_nodes(self):
        a = Node()
        b = Node()
        nodes = [a, b]
        r = cast_relationship((0, "TO", 1), nodes)
        assert r.start_node() is a
        assert r.end_node() is b
        assert r.type() == "TO"
