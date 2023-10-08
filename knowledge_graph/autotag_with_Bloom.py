from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM
from utils import autotag_with_Bloom

if __name__ == '__main__':
	device = 'cpu'
	max_new_tokens = 100
	login(token="")
	
	# load model tokenizer
	checkpoint = 'bigscience/bloom-7b1'
	# checkpoint = 'bigscience/bloom-560m'
	model = AutoModelForCausalLM.from_pretrained(checkpoint, device_map=device)
	tokenizer = AutoTokenizer.from_pretrained(checkpoint)

	prompt = f"""
	In the following, I will give you a paragraph which will be seperated with dash sign '-'.
	Your task is to summarize the paragraph into one tag(or say keyword). Only one tag should be generated. 
	The tag should be like a simple category indicating the concept of the paragraph.
	----------
	The collection of hydrological data in Italy has been managed at the national level by the National 
	Hydrological and Mareographic Service (SIMN) since early 1900. The dismantlement of the SIMN, performed 
	about 30 years ago, resulted in data collection being transferred to a regional level. This change has 
	determined problems in the availability of complete and homogeneous data for the whole country. Historical 
	hydrological measurements are usually available only in the printed version of the Hydrological Yearbooks 
	and limited efforts have been spent to digitize this collection. Within the SIREN (Saving Italian 
	hydRological mEasuremeNts) project we aim to digitize these data by crowd-sourcing the recovery of 
	hydrological measurements from historical Hydrological Yearbooks to produce a consistent dataset. Research 
	group: Paola Mazzoglio, Miriam Bertola, Luca Lombardo, Alberto Viglione, Francesco Laio and Pierluigi Claps. 
	Project supported by Politecnico di Torino Department of Environment, Land and Infrastructure Engineering.
	----------
	"""
	outputs = autotag_with_Bloom(prompt, model, tokenizer, max_new_tokens, device)
	print(outputs)
