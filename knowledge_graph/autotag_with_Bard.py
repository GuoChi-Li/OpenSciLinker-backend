import json 
from bardapi import BardCookies

if __name__ == '__main__':
	cookie_dict_path = '../../cookie_dict.json'
	with open(cookie_dict_path, 'r') as f:
		cookie_dict = json.load(f)
	bard = BardCookies(cookie_dict=cookie_dict)

	prompt = f"""
	In the following, I will give you a paragraph which will be seperated with dash sign '-'.
	Your task is to summarize the paragraph into tags(or say keywords). A tag is a category indicating 
	the concept of the paragraph. One tag or multiple tags should be generated. Your answer should contain
	only the tags.
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
	outputs = bard.get_answer(prompt)['content']
	print(outputs)
