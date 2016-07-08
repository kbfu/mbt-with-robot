# coding=utf-8

from networkx.readwrite import graphml
from os import listdir
from os.path import isfile, join
import os
from robot.api import TestSuite
from robot.reporting import ResultWriter
import random
import sys


def generate_suite(suite, nodes, edges, exec_path):
    test = suite.tests.create(str(exec_path).strip(' '))
    for i in range(len(exec_path) - 1):
        prev_node = exec_path[i]
        next_node = exec_path[i + 1]
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


def random_walker(file_path, coverage, walk_path=None):
    # 初始化robot suite
    test_suite_name = os.path.basename(file_path).split('.')[0]
    suite = TestSuite(test_suite_name)
    suite.resource.imports.library('ApolloLibrary')

    g = graphml.read_graphml(file_path)
    e = [e for e in g.edges_iter()]
    n = [n for n in g.node]
    edges = g.edge
    nodes = g.node
    now_coverage = 0
    exec_paths = []

    while now_coverage < coverage:
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
            exec_paths = [exec_paths[i] for i in range(len(exec_paths)) if i == 0 or exec_paths[i] != exec_paths[i - 1]]
            curr_nodes = list(set([item for sub_list in exec_paths for item in sub_list]))
            now_coverage = float(len(curr_nodes)) / float(len(n)) * 100

    # 整合成robot suite
    if walk_path is None:
        for exec_path in exec_paths:
            generate_suite(suite, nodes, edges, exec_path)
    else:
        sorted_path = []
        for path in walk_path:
            temp = path.replace('[', '').replace(']', '').replace(',', '')
            sorted_path.append(temp)
        generate_suite(suite, nodes, edges, sorted_path)

    # 运行suite并回收报告
    suite.run(output='results/{}.xml'.format(test_suite_name))
    xml_files = [join('results/', f) for f in os.listdir('results/') if isfile(join('results/', f))]
    ResultWriter(*xml_files) \
        .write_results(log='reports/{}_log.html'.format(test_suite_name)
                       , report='reports/{}_report.html'.format(test_suite_name)
                       , output='reports/{}_output.xml'.format(test_suite_name))


if __name__ == '__main__':
    # 判断命令行参数
    if '--help' in sys.argv:
        print 'example, specify a model file: python random_walker.py --coverage 100 --modelpath model_file.graphml\n'
        print 'or specify a model path: python random_walker.py --coverage 100 --modelpath model_path\n'
        print "or specify a walk path in model: python random_walker.py --coverage 100 --modelpath model_file.graphml" \
              " --walkpath ['n0', 'n1', 'n2', 'n7', 'n16', 'n23']"
        sys.exit()
    elif '--coverage' not in sys.argv or '--modelpath' not in sys.argv:
        print 'need coverage and modelpath parameters'
        sys.exit()
    else:
        for i in range(len(sys.argv)):
            if sys.argv[i] == '--coverage':
                try:
                    coverage = sys.argv[i + 1]
                except IndexError:
                    print 'please give a value to --coverage parameter'
                    sys.exit()
                if str(sys.argv[i + 1]).startswith('--'):
                    print 'please give a value to --coverage parameter'
                    sys.exit()
                try:
                    coverage = int(coverage)
                except ValueError:
                    print 'the value given for coverage is not a number'
                    sys.exit()
                if coverage not in range(1, 101):
                    print 'the value given for coverage should be in 1 to 100'
                    sys.exit()
            elif sys.argv[i] == '--modelpath':
                try:
                    model_path = sys.argv[i + 1]
                except IndexError:
                    print 'please give a value to --modelpath parameter'
                    sys.exit()
                if str(sys.argv[i + 1]).startswith('--'):
                    print 'please give a value to --modelpath parameter'
                    sys.exit()
                if os.path.exists(model_path) is False:
                    print "modelpath doesn't exist"
                    sys.exit()
            elif sys.argv[i] == '--walkpath':
                try:
                    walk_path = sys.argv[i + 1:]
                except IndexError:
                    print 'please give a value to --walkpath parameter'
                    sys.exit()
                if str(sys.argv[i + 1:]).startswith('--'):
                    print 'please give a value to --modelpath parameter'
                    sys.exit()
        try:
            if walk_path is not None:
                if isfile(model_path):
                    random_walker(model_path, coverage, walk_path)
                else:
                    model_files = [join(model_path, f)
                                   for f in listdir(model_path) if isfile(join(model_path, f))]
                    for model_file in model_files:
                        random_walker(model_file, coverage, walk_path)
        except NameError:
            if isfile(model_path):
                random_walker(model_path, coverage)
            else:
                model_files = [join(model_path, f)
                               for f in listdir(model_path) if isfile(join(model_path, f))]
                for model_file in model_files:
                    random_walker(model_file, coverage)
