import json
from langchain_openai import OpenAI, AzureOpenAI
from langchain.prompts import PromptTemplate
# from langchain.schema import ( HumanMessage )
import os
import dotenv

from dom_tree import TreeNode, build_tree_from_indented_text
import prompt_templates
import file_manager

dotenv.load_dotenv(dotenv.find_dotenv())

"""
Steps to successful frontend gen
  1. decompose into components (depth:null), form VDOM
  2. generate code for components from leaves up the tree
  3. structurize & generate package file
  4. build
"""

class FrontendAgent:
	def __init__(self):
		azure_endpoint = os.environ['AZURE_API_ENDPOINT']
		azure_key = os.environ['AZURE_API_KEY']
		
		# self.__llm_instance = OpenAI(max_tokens=3900)
		self.__llm_instance = AzureOpenAI(max_tokens=4_000, azure_deployment='gpt-4-turbo', api_key=azure_key, azure_endpoint=azure_endpoint, api_version='2023-12-01-preview')
		# TODO: USE TAILWIND & LUCIDE ICONS (COMPONENT)
		self.__component_prompt_template = PromptTemplate(input_variables=['component'], template='Write a React functional component for {component}. Please use tailwind and Lucide icons. Do not use descriptions')
		self.__project_prompt_template = PromptTemplate(input_variables=['project_name'], template=prompt_templates.project_structure_template)
		self.__optimize_prompt = 'Can you rewrite the code so that there is less code and results are untouched'

	def generate_project_structure(self, project_name: str):
		# self.__project_name = project_name
		prompt = self.__project_prompt_template.format(project_name=project_name)
		return self.__llm_instance.invoke(prompt)

	def generate_component_code(self, name: str) -> str:
		component_prompt = self.__component_prompt_template.format(component=name)
		code = self.__llm_instance.invoke(component_prompt)
		return code
	
	def generate_batch(self, prompts: list[str]) -> list[str]:
		component_prompts = [self.__component_prompt_template.format(component=prompt) for prompt in prompts]
		generated_code = self.__llm_instance.generate(component_prompts)
		print(generated_code)
		return list(map(lambda comp: comp[0].text, generated_code.generations))


def extract_file_name_no_ext(full_name: str, extension: str) -> str:
	return full_name.split(extension)[0]

def generate_components(agent: FrontendAgent, proj_tree: TreeNode, project_name: str, comp_dir: str):
	for component_file in proj_tree.children:
		# Check if it's a leaf
		if len(component_file.children) == 0:
			if component_file.name.endswith('js') or component_file.name.endswith('jsx'):
				component_name = extract_file_name_no_ext(component_file.name, '.js')
				[component_code] = agent.generate_batch([f'a {component_name} for {project_name}'])
				print(component_code)
				file_manager.create_file(comp_dir, component_file.name, component_code)
		else:
			generate_components(agent=agent, proj_tree=component_file, project_name=project_name, comp_dir=comp_dir)


def main():
	# * Init
	# llm_instance = OpenAI(temperature=0.9)
	agent = FrontendAgent()
	# * TEST
	project_name = 'music streaming app'
	test_component_name = 'sidebar'
	component_template = f'a {test_component_name} for {project_name}'
	proj_frame = agent.generate_project_structure(project_name)
	print('LLM RES:')
	print(proj_frame)
	print('-------------')
	print('TREE')
	project_tree = build_tree_from_indented_text(proj_frame)
	project_tree.pre_order_traverse()

	components_dir = project_tree.find_node_by_name(target_name='components')
	components_dir.pre_order_traverse()
	comp_dir = file_manager.create_overwrite_directory('.', 'generated-components')
	# for component_file in components_dir.children:
	# 	if len(component_file.children) > 0:
	# 		if component_file.name.endswith('js') or component_file.name.endswith('jsx'):
	# 			component_name = extract_file_name_no_ext(component_file.name, '.js')
	# 			[component_code] = agent.generate_batch([f'a {component_name} for {project_name}'])
	# 			print(component_code)
	# 			file_manager.create_file(comp_dir, component_file.name, component_code)

	generate_components(agent=agent, proj_tree=components_dir, project_name=project_name, comp_dir=comp_dir)
	
	return

if __name__ == '__main__':
  	main()