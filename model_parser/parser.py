# coding=utf-8

from networkx.readwrite import graphml
import networkx as nx
from os import listdir
from os.path import isfile, join
import os
from robot.api import TestSuite
from robot.reporting import ResultWriter


def parser(file_path):
    # 初始化robot suite
    test_suite_name = os.path.basename(file_path).split('.')[0]
    suite = TestSuite(test_suite_name)
    suite.resource.imports.library('TestLibrary')

    g = graphml.read_graphml(file_path)
    e = [e for e in g.edges_iter()]
    n = [n for n in g.node]
    edges = g.edge
    nodes = g.node

    revers_paths = []
    exec_paths = []

    # 获取所有反向路径
    for edge in e:
        if edge[0] >= edge[1]:
            revers_paths.append(edge)

    # 遍历反向路径
    if len(revers_paths) > 0:
        for revers_path in revers_paths:
            for path in nx.all_simple_paths(g, 'n0', revers_path[0]):
                exec_paths.append(path + [revers_path[1]])

    # 搜寻所有的末端路径
    for node in n:
        if len(g.successors(node)) == 0:
            for path in nx.all_simple_paths(g, 'n0', node):
                exec_paths.append(path)

    # 整合成robot suite
    for exec_path in exec_paths:
        test = suite.tests.create(str(exec_path).strip(' '))
        for i in range(len(exec_path)-1):
            prev_node = exec_path[i]
            next_node = exec_path[i+1]
            if str(nodes[prev_node]['label']).lower() == 'start':
                test.keywords.create(edges['n0'][next_node]['label'])
                test.keywords.create(nodes[next_node]['label'])
            else:
                test.keywords.create(nodes[prev_node]['label'])
                test.keywords.create(edges[prev_node][next_node]['label'])
                test.keywords.create(nodes[next_node]['label'])

    # 运行suite并回收报告
    suite.run(output='../results/{}.xml'.format(test_suite_name))
    xml_files = [join('../results/', f) for f in listdir('../results/') if isfile(join('../results/', f))]
    ResultWriter(*xml_files) \
        .write_results(log='../reports/{}_log.html'.format(test_suite_name)
                       , report='../reports/{}_report.html'.format(test_suite_name)
                       , output='../reports/{}_output.xml'.format(test_suite_name))

if __name__ == '__main__':
    input_file = raw_input('input path or file: ')
    if isfile(input_file):
        parser(input_file)
    else:
        model_files = [join(input_file, f)
                       for f in listdir(input_file) if isfile(join(input_file, f))]
        for model_file in model_files:
            parser(model_file)
