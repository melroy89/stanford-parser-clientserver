# -*- coding: utf-8 -*-
# Copyright 2014 by Melroy van den Berg
"""A Jython interface to the Stanford parser (v3.3.1). 

Input in utf8.
On output, the script produces unicode.

Code based on: https://github.com/vpekar/stanford-parser-in-jython
"""

__author__ = "Melroy van den Berg <melroy@melroy.org>, Viktor Pekar <v.pekar@gmail.com>"
__version__ = "0.2"

import sys, re, os, string, math
# Add the stanford-parser.jar file to class path (default current directory)
sys.path.append('./stanford-parser.jar')

try:
    assert 'java' in sys.platform
except AssertionError:
    raise Exception("This Interface should be called from Jython!")

from java.util import *
from edu.stanford.nlp.trees import PennTreebankLanguagePack, TreePrint
from edu.stanford.nlp.parser.lexparser import LexicalizedParser
from edu.stanford.nlp.process import Morphology, PTBTokenizer, WordTokenFactory
from edu.stanford.nlp.parser.lexparser import Options
from edu.stanford.nlp.ling import Sentence, WordTag
from java.io import StringReader

class PySentence:
    """An interface to the grammaticalStructure object of SP
    """

    def __init__(self, parser, parse, xmltags={}):
        """Create a PySentence object from parse.
        @param gsf: a grammaticalStructureFactory object
        @param parse: a parse of the sentence
        @param xmltags: index of the previous text token =>
            list of intervening xmltags
        """
        self.parse = parse
        self.gs = parser.gsf.newGrammaticalStructure(parse)
        self.lemmer = parser.lemmer
        self.xmltags = xmltags

        self.node = {}
        self.word = {}
        self.tag = {}
        self.lemma = {}
        self.dep = {}
        self.rel = {}
        self.children = {}

        self.populate_indices()

    def get_lemma(self, word, tag):
        lemma = self.lemmer.lemmatize(WordTag(word, tag)).lemma()
        return lemma

    def get_pos_tag(self, node):
        parent = node.parent()
        tag = 'Z' if parent == None else parent.value()
        return tag

    def get_dependency_data(self, word, node_i, idx):
        parent = self.gs.getGovernor(node_i)
        if word in string.punctuation or parent == None:
            parent_idx = 0
            rel = 'punct'
        else:
            parent_idx = parent.index()
            rel = str(self.gs.getGrammaticalRelation(parent_idx, idx))
        return parent_idx, rel

    def get_word(self, node_i):
        word = node_i.value()

        # correct the appearance of parentheses
        if word == '-RRB-':
            word = u'('
        elif word == '-LRB-':
            word = u')'

        return word

    def populate_indices(self):

        # insert the tags before the text, if any are present before the text
        self.add_xml_tags_to_word_index(idx=0)

        # iterate over text tokens
        for node_i in self.gs.getNodes():

            if node_i.headTagNode() != None:
                continue

            idx = node_i.index()
            word = self.get_word(node_i)
            tag = self.get_pos_tag(node_i)
            p_idx, rel = self.get_dependency_data(word, node_i, idx)

            self.node[idx] = node_i
            self.word[idx] = word
            self.tag[idx] = tag
            self.lemma[idx] = self.get_lemma(word, tag)
            self.rel[idx] = rel
            self.dep[idx] = p_idx
            self.children[p_idx] = self.children.get(p_idx, [])
            self.children[p_idx].append(idx)

            # insert xml tags, if any
            self.add_xml_tags_to_word_index(idx)

    def add_xml_tags_to_word_index(self, idx):
        """@param idx: the id of the previous word
        """
        tags_at_idx = self.xmltags.get(idx)
        if tags_at_idx:
            num_tags = len(tags_at_idx)
            for tag_i in xrange(num_tags):
                tag_idx = (tag_i + 1) / float(num_tags + 1)
                tag_name = tags_at_idx[tag_i]
                self.word[idx + tag_idx] = tag_name

    def get_head(self, node):
        """Return a tuple with the head of the dependency for a node and the
        relation label.
        """
        idx = node.index()
        dep_idx = self.dep.get(idx)
        if not dep_idx:
            return None, None
        return self.node.get(dep_idx), self.rel.get(idx)

    def get_children(self, node):
        """Yield tuples each with a child of the dependency
        and the relation label
        """
        for idx in self.children.get(node.index(), []):
            yield self.node[idx], self.rel[idx]

    def get_descendants(self, start_idx):
        """Return all descendants of a node, including the node itself
        """
        def traverse(idx):
            global descendants
            for idx_i in self.children.get(idx, []):
                descendants.append(idx_i)
                traverse(idx_i)
        global descendants
        descendants = [start_idx]
        traverse(start_idx)
        return descendants

    def prune(self, idx):
        """Given an index, remove all the words dependent on the word with that
        index, including the word itself.
        """
        for idx_i in self.get_descendants(idx):
            self.delete_node(idx_i)

    def delete_node(self, idx):
        del self.node[idx], self.word[idx], self.tag[idx], self.lemma[idx], \
                self.rel[idx], self.dep[idx]
        if idx in self.children:
            del self.children[idx]

    def get_plain_text(self):
        """Output plain-text sentence.
        """
        text = ' '.join([self.word[x] for x in sorted(self.node)])
        # remove spaces in front of commas, etc
        for i in ',.:;!?':
            text = text.replace(' ' + i, i)
        return text

    def get_least_common_node(self, node_i_idx, node_j_idx):
        """Return a node that is least common for two given nodes,
        as well as the shortest path between the two nodes
        @param node_i_idx: index of node 1
        @param node_j_idx: index of node 2
        """

        common_node = None
        shortest_path = []
        path1 = self.path2root(node_i_idx)
        path2 = self.path2root(node_j_idx)

        for idx_i in path1:
            if common_node != None:
                break
            for idx_j in path2:
                if idx_i == idx_j:
                    common_node = idx_i
                    break

        if common_node != None:
            for idx_i in path1:
                shortest_path.append(idx_i)
                if idx_i == common_node:
                    break
            for idx_i in path2:
                if idx_i == common_node:
                    break
                shortest_path.append(idx_i)

        return common_node, shortest_path

    def path2root(self, idx):
        """The path to the root from a node.
        @param idx: the index of the node
        """
        path = [idx]

        if idx != 0:
            while True:
                parent = self.dep.get(idx)
                if not parent:
                    break
                path.append(parent)
                idx = parent

        return path

    def print_table(self):
        """Print the parse as a table, FDG-style, to STDOUT
        """
        def get_index(id_str):
            return '-' if '.' in id_str else id_str

        for idx in sorted(self.word):
            line = '\t'.join([
                    get_index(unicode(idx)),
                    self.word.get(idx, ''),
                    self.lemma.get(idx, ''),
                    self.tag.get(idx, ''),
                    self.rel.get(idx, ''),
                    unicode(self.dep.get(idx, '')),
                ])
            print line

    def get_parse(self):
        """Return the parse
        """
        return self.parse


    def print_tree(self, mode='penn'):
        """Prints the parse.
        @param mode: penn/typedDependenciesCollapsed/etc
        """
        tree_print = TreePrint(mode)
        tree_print.printTree(self.parse)


class StanfordParser:

    def __init__(self, parser_file = 'englishPCFG.ser.gz',
            parser_options=['-maxLength', '80', '-retainTmpSubcategories']):

        """@param parser_file: path to the serialised parser model
            (e.g. englishPCFG.ser.gz)
        @param parser_options: options
        """
        assert os.path.exists(parser_file)
        options = Options()
        options.setOptions(parser_options)
        self.lp = LexicalizedParser.getParserFromFile(parser_file, options)
        tlp = PennTreebankLanguagePack()
        self.gsf = tlp.grammaticalStructureFactory()
        self.lemmer = Morphology()
        self.word_token_factory = WordTokenFactory()
        self.parser_query = None

    def get_most_probable_parses(self, text, kbest=2):
        """Yield kbest parses of a sentence along with their probabilities.
        """
        if not self.parser_query:
            self.parser_query = self.lp.parserQuery()

        response = self.parser_query.parse(self.tokenize(text))

        if not response:
            raise Exception("The sentence cannot be parsed: %s" % text)

        for candidate_tree in self.parser_query.getKBestPCFGParses(kbest):
            py_sentence = PySentence(self, candidate_tree.object())
            prob = math.e ** candidate_tree.score()
            yield py_sentence, prob

    def parse_wordlist(self, wordList):
        """Strips XML tags first.
        @param s: the sentence to be parsed, as a string
        @return: a Sentence object
        """
        sent = []   
        [sent.append(token.replace(u'\xa0', ' ').decode('utf-8')) for token in wordList]
        parse = self.lp.apply(Sentence.toWordList(sent))
        return PySentence(self, parse)

