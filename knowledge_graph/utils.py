import time
import torch
import json
import uuid
import openai
from tqdm import tqdm
from typing import List
from bardapi import BardCookies
from search_engine import NodeSearchEngine

class Node():
	def __init__(self, title, tag, subtag, abstract, url, owner, status, category, idx=None):
		self.idx = idx or uuid.uuid4().hex 
		self.title = title
		self.tag = tag
		self.subtag = subtag
		self.abstract = abstract
		self.url = url
		self.owner = owner
		self.status = status
		self.category = category

		if isinstance(self.tag, list):
			self.tag = ', '.join(self.tag)

		if isinstance(self.subtag, list):
			self.subtag = ', '.join(self.subtag)

	def __repr__(self) -> str:
		return str(self.to_dict())

	@classmethod
	def from_dict(cls, dct):
		return cls(
			title		= cls.get_alias(dct, ['title', 'project_name']),
			tag			= cls.get_alias(dct, ['tag', 'main_tag']),
			subtag		= cls.get_alias(dct, ['subtag', 'sub_tag', 'subtags', 'keywords']),
			abstract	= cls.get_alias(dct, ['abstract', 'project_description', 'description']),
			url			= cls.get_alias(dct, ['url', 'project_url_external', 'Project URL']),
			owner		= cls.get_alias(dct, ['owner', 'publisher']),
			status		= cls.get_alias(dct, ['status', 'project_status']),
			category	= cls.get_alias(dct, ['category']),
			idx 		= cls.get_alias(dct, ['idx'])
		)
	
	@staticmethod
	def get_alias(dct:dict, alias:List[str]=None) -> str:
		for k in dct.keys():
			if k in alias:
				return dct[k]
		return None
	
	def to_dict(self, simplify=False):
		if simplify:
			return {
				'idx': self.idx, 
				'title': self.title, 
				'tag': self.tag
			}
		else:
			return {
				'idx': self.idx, 
				'title': self.title, 
				'tag': self.tag, 
				'subtag': self.subtag, 
				'abstract': self.abstract,
				'url': self.url, 
				'owner': self.owner,
				'status': self.status,
				'category': self.category
			}

class Link():
	def __init__(self, source, target, weight=1.0):
		self.source = source
		self.target = target
		self.weight = weight

	def __repr__(self) -> str:
		return str(self.to_dict())

	@classmethod
	def from_dict(cls, dct):
		return cls(
			dct.get('source'), 
			dct.get('target'), 
			dct.get('weight', 1.0)
		)
	
	def to_dict(self):
		return {
			'source': self.source,
			'target': self.target
		}

class Graph():
	def __init__(self, nodes:List[Node], links:List[Link]):
		self.nodes = nodes
		self.links = links

	def __len__(self) -> int:
		return len(self.nodes)

	def __repr__(self) -> str:
		return str(self.to_dict())

	@classmethod
	def from_json(cls, json_path):
		with open(json_path, 'r') as f:
			data = json.load(f)
		nodes = [Node.from_dict(node) for node in data['nodes']]
		links = [Link.from_dict(link) for link in data['links']]
		return cls(nodes, links)
	
	@classmethod
	def merge(cls, graphs, relink=False):
		nodes = []
		for graph in graphs:
			nodes += graph.nodes
		if relink:
			links = get_links_from_nodes(nodes)
		else:
			links = [Link(0, 0)]
		return cls(nodes, links)

	def to_dict(self, simplify=False):
		return {
			'nodes': [node.to_dict(simplify) for node in self.nodes],
			'links': [link.to_dict() for link in self.links]
		}

	def to_json(self, json_path, simplify=False):
		dct = self.to_dict(simplify)
		with open(json_path, 'w') as f:
			json.dump(dct, f, indent=4)

	
class Prompter:
	tag_prefix = f"""
		In the following, I will give you a paragraph which will be seperated with dash sign '-'.
		Your task is to summarize the paragraph into tag(or say keyword). A tag is a category indicating 
		the concept of the paragraph. Only one tag should be generated. Your answer should contain
		only one tag. Your answer should not contain content other than the tag. 
		The tag should be one of the given 25 tags: ["Arts", "Biology", "Environmental Science", "History", 
		"Language", "Literature", "Health and Medicine", "Nature", "Physics", "Chemistry", "Social Science", 
		"Astronomy", "Education", "Mathematics", "Cultural Studies", "Geology", "Psychology", "Anthropology", 
		"Political Science", "Computer Science", "Electrical Engineering", "Mechanical Engineering", "Civil Engineering", 
		"Materials Science", "Data"].
	"""

	tag_prefix_compact = f"""
		Summarize the following paragraph into the provided 25 tags: ["Arts", "Biology", "Environmental Science", 
		"History", "Language", "Literature", "Health and Medicine", "Nature", "Physics", "Chemistry", "Social Science", 
		"Astronomy", "Education", "Mathematics", "Cultural Studies", "Geology", "Psychology", "Anthropology", 
		"Political Science", "Computer Science", "Electrical Engineering", "Mechanical Engineering", "Civil Engineering", 
		"Materials Science", "Data"]. Your response should consist of one tag or multiple tags seperated by a single comma ','.
		No additional content should be included.
	"""

	subtag_prefix = f"""
		In the following, I will give you a paragraph which will be seperated with dash sign '-'.
		Your task is to summarize the paragraph into tags(or say keywords). A tag is a category indicating 
		the concept of the paragraph. One tag or multiple tags should be generated. Your answer should contain
		only the tags. Your answer should not contain contents other than the tags. The tags should be seperated 
		by a single comma ','.
	"""

	subtag_prefix_compact = f"""
		Summarize the paragraph into one or more tags, separated by a single comma ','. Your response should only 
		include the tags, and no additional content.
	"""

	@classmethod
	def add_tag_prefix(cls, content):
		return f"""
			{cls.tag_prefix}
			----------
			{content}
			----------
			""" 
	
	@classmethod
	def add_tag_prefix_compact(cls, content):
		return f"""
			{cls.tag_prefix_compact}
			{content}
		"""
	
	@classmethod
	def add_subtag_prefix(cls, content):
		return f"""
			{cls.subtag_prefix}
			----------
			{content}
			----------
		"""
	
	@classmethod
	def add_subtag_prefix_compact(cls, content):
		return f"""
			{cls.subtag_prefix_compact}
			{content}
		"""


def autotag_with_Bloom(prompt, model, tokenizer, max_new_tokens=100, device='cpu'):
	inputs = tokenizer.encode(prompt, return_tensors='pt').to(device)
	with torch.cuda.amp.autocast():
		outputs = model.generate(inputs, max_new_tokens=max_new_tokens)
	return tokenizer.decode(outputs[0], skip_special_tokens=True)


def auto_tag_with_Bard(nodes:List[Node], Bard_cookie_path='../../cookie_dict.json') -> List[Node]:
	with open(Bard_cookie_path, 'r') as f:
		cookie_dict = json.load(f)
	bard = BardCookies(cookie_dict=cookie_dict)

	for node in tqdm(nodes, desc='asking Bard for tags...'):
		# tag
		prompt = Prompter.add_tag_prefix(node.abstract)
		node.tag = bard.get_answer(prompt)['content']

		# subtag
		prompt = Prompter.add_subtag_prefix(node.abstract)
		node.subtag += ', ' + bard.get_answer(prompt)['content']

	return nodes

def auto_tag_with_GPT(nodes:List[Node], model='gpt-3.5-turbo', chunk_size=1) -> List[Node]:
	# batch mode, not sure responses are correct (?)
	if chunk_size > 1:
		for i in tqdm(range(len(nodes)//chunk_size+1)):
			chunk_slice = slice(i*chunk_size, (i+1)*chunk_size)
			chunk_nodes = nodes[chunk_slice]

			# tag
			messages = [{"role": "system", "content": Prompter.tag_prefix_compact}]
			messages += [{"role": "user", "content": node.abstract} for node in chunk_nodes]
			response = openai.ChatCompletion.create(model=model, messages=messages, n=len(messages))

			for node, choice in zip(chunk_nodes, response.choices[1:]):
				node.tag = choice.message.content


			# subtag
			messages = [{"role": "system", "content": Prompter.subtag_prefix_compact}]
			messages += [{"role": "user", "content": node.abstract} for node in chunk_nodes]
			response = openai.ChatCompletion.create(model=model, messages=messages, n=len(messages))
			for node, choice in zip(chunk_nodes, response.choices):
				node.subtag = choice.message.content

			nodes[chunk_slice] = chunk_nodes
	# single mode
	else:
		for node in tqdm(nodes, desc=f'asking {model} for tags'):
			done = False
			while not done:
				try:
					# tag
					response = openai.ChatCompletion.create(
						model=model,
						messages=[{"role": "user", "content": Prompter.add_tag_prefix_compact(node.abstract)}],
						request_timeout=60
					)
					node.tag = response.choices[0].message.content
				
					# subtag
					response = openai.ChatCompletion.create(
						model=model,
						messages=[{"role": "user", "content": Prompter.add_subtag_prefix_compact(node.abstract)}],
						request_timeout=60
					)
					node.subtag = response.choices[0].message.content
					done = True
				except Exception as e:
					print(e)
					print('#'*50)
					print('GPT encounters error ! Retry after 10 seconds...')
					done = False
					time.sleep(10)

	return nodes

def get_links_from_nodes(nodes:List[Node]) -> List[Link]:
	# node idx map
	links_map = NodeSearchEngine(nodes).get_links_map()
	return [Link(src, tgt) for src, val in links_map.items() for tgt in val]
