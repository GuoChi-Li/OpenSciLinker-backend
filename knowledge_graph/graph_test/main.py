import GPUtil
import psutil
import time 
import random
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from _graph import Node, Link, Graph

def print_cpu_info():
	# Get CPU count and usage percentage
	cpu_count = psutil.cpu_count(logical=False)  # Physical CPU count
	cpu_percent = psutil.cpu_percent(interval=1, percpu=True)  # CPU usage percentage
	print(f"Physical CPU Count: {cpu_count}")

	# Get CPU frequency
	cpu_freq = psutil.cpu_freq()
	print(f"CPU Frequency (current): {cpu_freq.current} MHz")
	print(f"CPU Frequency (min): {cpu_freq.min} MHz")
	print(f"CPU Frequency (max): {cpu_freq.max} MHz")

	# Get CPU temperature (Note: Temperature may not be available on all systems)
	try:
		temperature = psutil.sensors_temperatures()
		cpu_temp = temperature['coretemp'][0].current if 'coretemp' in temperature else None
		print(f"CPU Temperature: {cpu_temp}°C")
	except AttributeError:
		print("CPU temperature information not available.")
	except KeyError:
		print("CPU temperature information not available.")

def print_gpu_info():
	# Get GPU information using GPUtil
	try:
		gpu_info = GPUtil.getGPUs()[0]
		gpu_name = gpu_info.name
		gpu_driver = gpu_info.driver
		gpu_memory_total = gpu_info.memoryTotal
		gpu_memory_free = gpu_info.memoryFree
		gpu_memory_used = gpu_info.memoryUsed
		gpu_utilization = gpu_info.load
		print(f"GPU Name: {gpu_name}")
		print(f"GPU Driver: {gpu_driver}")
		print(f"GPU Memory Total: {gpu_memory_total} MB")
		print(f"GPU Memory Free: {gpu_memory_free} MB")
		print(f"GPU Memory Used: {gpu_memory_used} MB")
		print(f"GPU Utilization: {gpu_utilization}%")
	except Exception as e:
		print(f"GPU information not available: {e}")


def test_computation_time_with_graph(graph, model_name, src, tgt, device):
	print('#'*50)
	print(f'Testing graph of with {len(graph)} nodes...')
	print(f'Testing model: {model_name}...')
	print(f'Testing on: {device}...')

	model = SentenceTransformer(model_name)
	num_param = sum([p.numel() for p in model.parameters()])
	print(f'Number of parameters: {num_param/1e6:.0f}M')

	s = time.time()
	abstracts = [node.abstract for node in graph.nodes]
	embeddings = model.encode(abstracts).tolist()
	# for i in range(len(embeddings)):
	# 	tgt = embeddings.copy()
	# 	src = tgt.pop(i)
	# 	sim = cos_sim(src, tgt)
	f = time.time()
	print(f'cost: {f-s:.4f} sec')
	return f-s


if __name__ == '__main__':
	# >----------------------------------------------------------------------------------------------------
	# > generate dummy graph
	# >----------------------------------------------------------------------------------------------------
	# small graph
	num_proj = 10
	nodes = [
		Node(idx=i, title=f'project {i}', tag='test1, test2, test3', 
	   		abstract='abstract '*random.randint(10, 100), 
			source='testing', owner='sudo', status='testing') for i in range(num_proj)
	]
	links = [
		Link(source=random.randint(1, num_proj), 
	   		target=random.randint(1, num_proj)) for _ in range(num_proj)
	]
	graph_small = Graph(nodes, links)
	graph_small.to_json('./dummy_data_small.json')

	# large graph
	num_proj = 1000
	nodes = [
		Node(idx=i, title=f'project {i}', tag='test1, test2, test3', 
	   		abstract='abstract '*random.randint(10, 100), 
			source='testing', owner='sudo', status='testing') for i in range(num_proj)
	]
	links = [
		Link(source=random.randint(1, num_proj), 
	   		target=random.randint(1, num_proj)) for _ in range(num_proj)
	]
	graph_large = Graph(nodes, links)
	graph_large.to_json('./dummy_data_large.json')

	
	src = ["This is an test."]
	tgt = ["This is an example sentence", "Each sentence is converted"]

	# >----------------------------------------------------------------------------------------------------
	# > device information
	# >----------------------------------------------------------------------------------------------------
	print_cpu_info()
	print_gpu_info()

	# >----------------------------------------------------------------------------------------------------
	# > all-mpnet-base-v2: 420MB
	# >----------------------------------------------------------------------------------------------------
	cpu_cost = test_computation_time_with_graph(graph_small, 'sentence-transformers/all-mpnet-base-v2', src, tgt, 'cpu')
	gpu_cost = test_computation_time_with_graph(graph_small, 'sentence-transformers/all-mpnet-base-v2', src, tgt, 'cuda')
	cpu_cost = test_computation_time_with_graph(graph_large, 'sentence-transformers/all-mpnet-base-v2', src, tgt, 'cpu')
	gpu_cost = test_computation_time_with_graph(graph_large, 'sentence-transformers/all-mpnet-base-v2', src, tgt, 'cuda')

	# >----------------------------------------------------------------------------------------------------
	# > all-MiniLM-L6-v2: 80 MB
	# >----------------------------------------------------------------------------------------------------
	cpu_cost = test_computation_time_with_graph(graph_small, 'sentence-transformers/all-MiniLM-L6-v2', src, tgt, 'cpu')
	gpu_cost = test_computation_time_with_graph(graph_small, 'sentence-transformers/all-MiniLM-L6-v2', src, tgt, 'cuda')
	cpu_cost = test_computation_time_with_graph(graph_large, 'sentence-transformers/all-MiniLM-L6-v2', src, tgt, 'cpu')
	gpu_cost = test_computation_time_with_graph(graph_large, 'sentence-transformers/all-MiniLM-L6-v2', src, tgt, 'cuda')

	# >----------------------------------------------------------------------------------------------------
	# > paraphrase-albert-small-v2: 43 MB
	# >----------------------------------------------------------------------------------------------------
	cpu_cost = test_computation_time_with_graph(graph_small, 'sentence-transformers/paraphrase-albert-small-v2', src, tgt, 'cpu')
	gpu_cost = test_computation_time_with_graph(graph_small, 'sentence-transformers/paraphrase-albert-small-v2', src, tgt, 'cuda')
	cpu_cost = test_computation_time_with_graph(graph_large, 'sentence-transformers/paraphrase-albert-small-v2', src, tgt, 'cpu')
	gpu_cost = test_computation_time_with_graph(graph_large, 'sentence-transformers/paraphrase-albert-small-v2', src, tgt, 'cuda')


