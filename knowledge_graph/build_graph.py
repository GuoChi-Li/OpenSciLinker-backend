import os 
import glob 
import argparse
import json 
from utils import Node, Graph, get_links_from_nodes, auto_tag_with_GPT

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--mode', type=str, dest='mode', default='build')
args = parser.parse_args()

crawl_root = '../web-crawler/data'
crawl_folder = 'CitizenScience_gov'
crawl_target = '20231007_feed.json'
crawl_path = f'{crawl_root}/{crawl_folder}/clean'

if __name__ == '__main__':
	if args.mode == 'build':
		print(f'building graph for {crawl_path}')

		with open(f'{crawl_path}/{crawl_target}', 'r', encoding='utf-8') as f:
			data = json.load(f)

		# >--------------------------------------------------
		# > building graph only for a part of data
		part = 6
		max_data_len = 50
		start_idx = part*max_data_len
		end_idx = (part+1)*max_data_len
		if part >= 0:
			data = data[start_idx:end_idx]
		# >--------------------------------------------------

		nodes = [Node.from_dict(dct) for dct in data]
		for i in range(len(nodes)):
			nodes[i].category = crawl_folder

		# auto tagging and linking the graph
		nodes = auto_tag_with_GPT(nodes, chunk_size=1)
		links = get_links_from_nodes(nodes)

		graph = Graph(nodes, links)
		graph.to_json(f'{crawl_path}/knowledge_graph_{start_idx}-{end_idx}.json', simplify=True)
		graph.to_json(f'{crawl_path}/knowledge_graph_full_{start_idx}-{end_idx}.json', simplify=False)

	if args.mode == 'link':
		crawl_path = '../web-crawler/data'
		crawl_target = 'min_git_crawl_info.json'

		print(f'linking graph for {crawl_path}')
		with open(f'{crawl_path}/{crawl_target}', 'r') as f:
			data = json.load(f)

		nodes = [Node.from_dict(dct) for dct in data]
		links = get_links_from_nodes(nodes)
		graph = Graph(nodes, links)
		graph.to_json(f'{crawl_path}/knowledge_graph.json', simplify=True)
		graph.to_json(f'{crawl_path}/knowledge_graph_full.json', simplify=False)

	if args.mode == 'merge':
		print(f'merging graph')

		merging_paths = [f'{crawl_root}/{folder}/clean' for folder in next(os.walk(crawl_root))[1]]
		merging_paths += [crawl_root]

		graphs = []
		for merging_path in merging_paths:
			graph_paths = glob.glob(f'{merging_path}/knowledge_graph*.json')
			for gp in graph_paths:
				if 'full' not in gp and 'merge' not in gp:
					graphs.append(Graph.from_json(gp))

		# reassign idx
		graph = Graph.merge(graphs)
		for i in range(len(graph.nodes)):
			graph.nodes[i].idx = i
		graph.to_json(f'{crawl_root}/knowledge_graph_merged.json')
			



