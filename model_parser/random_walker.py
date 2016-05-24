# coding=utf-8

from networkx.readwrite import graphml
from os import listdir
from os.path import isfile, join
import os
from robot.api import TestSuite
from robot.reporting import ResultWriter
import random


def random_walker(file_path):
    # 初始化robot suite
    test_suite_name = os.path.basename(file_path).split('.')[0]
    suite = TestSuite(test_suite_name)
    suite.resource.imports.library('ApolloLibrary')

    g = graphml.read_graphml(file_path)
    e = [e for e in g.edges_iter()]
    n = [n for n in g.node]
    edges = g.edge
    nodes = g.node
    coverage = 0
    exec_paths = []

    while coverage < 100:
        curr_path = []
        node = 'n0'
        while g.successors(node):
            if len(g.successors(node)) > 0 and node == 'n0':
                curr_path.append('n0')
                node = g.successors(node)[int(random.uniform(0, len(g.successors(node))))]
                curr_path.append(node)
            elif len(g.successors(node)) > 0 and node != 'n0':
                prev_node = curr_path[-2]
                node = g.successors(node)[int(random.uniform(0, len(g.successors(node))))]
                if node == prev_node:
                    break
                curr_path.append(node)
            elif len(g.successors(node)) == 0:
                break
        exec_paths.append(curr_path)
        if len(exec_paths) > 1:
            exec_paths = sorted(exec_paths)
            exec_paths = [exec_paths[i] for i in range(len(exec_paths)) if i == 0 or exec_paths[i] != exec_paths[i-1]]
            curr_nodes = list(set([item for sub_list in exec_paths for item in sub_list]))
            coverage = len(curr_nodes)/len(n)*100

    # 整合成robot suite
    for exec_path in exec_paths:
        test = suite.tests.create(str(exec_path).strip(' '))
        for i in range(len(exec_path)-1):
            prev_node = exec_path[i]
            next_node = exec_path[i+1]
            if str(nodes[prev_node]['label']).lower() == 'start':
                test.keywords.create('Log', args=['测试开始'.decode('utf-8')])
                e_label = edges['n0'][next_node]['label']
                if len(e_label.split('/')) > 1:
                    test.keywords.create(e_label.split('/')[0], args=[e_label.split('/')[1]])
                else:
                    test.keywords.create(edges['n0'][next_node]['label'])
                test.keywords.create('Log', args=['当前的节点为: {}'.format(next_node).decode('utf-8')])
                n_label = nodes[next_node]['label']
                if len(n_label.split('/')) > 1:
                    test.keywords.create(n_label.split('/')[0], args=[n_label.split('/')[1]])
                else:
                    test.keywords.create(n_label)
            else:
                test.keywords.create('Log', args=['当前的向量为: {}'.format(edges[prev_node][next_node]['id']).decode('utf-8')])
                e_label = edges[prev_node][next_node]['label']
                if len(e_label.split('/')) > 1:
                    test.keywords.create(e_label.split('/')[0], args=[e_label.split('/')[1]])
                else:
                    test.keywords.create(e_label)
                test.keywords.create('Log', args=['当前的节点为: {}'.format(next_node).decode('utf-8')])
                n_label = nodes[next_node]['label']
                if len(n_label.split('/')) > 1:
                    test.keywords.create(n_label.split('/')[0], args=[n_label.split('/')[1]])
                else:
                    test.keywords.create(n_label)

    # 运行suite并回收报告
    suite.run(output='../results/{}.xml'.format(test_suite_name))
    xml_files = [join('../results/', f) for f in os.listdir('../results/') if isfile(join('../results/', f))]
    ResultWriter(*xml_files) \
        .write_results(log='../reports/{}_log.html'.format(test_suite_name)
                       , report='../reports/{}_report.html'.format(test_suite_name)
                       , output='../reports/{}_output.xml'.format(test_suite_name))

if __name__ == '__main__':
    input_file = raw_input('input model path or file: ')
    if isfile(input_file):
        random_walker(input_file)
    else:
        model_files = [join(input_file, f)
                       for f in listdir(input_file) if isfile(join(input_file, f))]
        for model_file in model_files:
            random_walker(model_file)

