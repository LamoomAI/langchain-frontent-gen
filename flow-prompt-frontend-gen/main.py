from flow_prompt import FlowPrompt, PipePrompt
from flow_prompt import AIModelsBehaviour, AzureAIModel, OpenAIModel, AttemptToCall
from flow_prompt import OPENAI_GPT3_5_TURBO_0125_BEHAVIOUR
from flow_prompt import C_128K 
import os, sys
import dotenv
import json

from tree import TreeNode, build_tree_from_indented_text
import file_manager


class FrontendAgent:
	def __init__(self) -> None:
		azure_keys = json.loads(os.getenv("AZURE_KEYS", "{}"))
		self.__llm_instance = FlowPrompt(azure_keys=azure_keys)
		self.__project_prompt = PipePrompt('generate_react_project_structure')
		self.__project_prompt.add(content='Create the project folder structure for a {app_name} web application \
											in React. Use double spaces for indentation and no other symbols.\
											Make sure there`s only one root directory src which includes components and pages directories.')
		self.__component_prompt = PipePrompt('generate_react_component')
		self.__component_prompt.add(content='write a react component for a {component_name}. You may use tailwind and lucide icons for styling')
		self.__page_prompt = PipePrompt('generate_react_page_aggregate_component')
		self.__page_prompt.add('write a react component for a {page_name} page. You may use {component_list} components \
								from {comp_dir_path} if any of these belong on the page')
		self.behavior = OPENAI_GPT3_5_TURBO_0125_BEHAVIOUR


	def generate_project_structure(self, proj_name: str) -> str:
		proj_context = {'app_name': proj_name}
		structure_response = self.__llm_instance.call(self.__project_prompt.id, proj_context, self.behavior)
		return structure_response.content
		

	def generate_component(self, comp_name: str) -> str:
		comp_context = {'component_name': comp_name}
		comp_response = self.__llm_instance.call(self.__component_prompt.id, comp_context, self.behavior)
		return comp_response.content

	def generate_page(self, page_name: str, exsisting_components: list[str], path_to_components: str) -> str:
		ctx = {'page_name': page_name, 'component_list': exsisting_components, 'comp_dir_path': path_to_components}
		page_response = self.__llm_instance.call(self.__page_prompt.id, ctx, self.behavior)
		return page_response.content

	def generate_component_batch(self, dir_path: str, component_names: list[str]):
		for component_name in component_names:
			code = self.generate_component(component_name)
			file_manager.create_file(dir_path, f'{component_name}.js', code)

	def generate_page_batch(self, dir_path: str, page_names: list[str], children_components: list[str], path_to_components: str):
		for page_name in page_names:
			code = self.generate_page(page_name, children_components, path_to_components)
			file_manager.create_file(dir_path, f'{page_name}.js', code)


def extract_file_name_no_ext(full_name: str, extension: str) -> str:
	return full_name.split(extension)[0]

def extract_component_names(agent: FrontendAgent, proj_tree: TreeNode) -> list[str]:
	component_names = []
	for component_file in proj_tree.children:
		# Check if it's a leaf
		if len(component_file.children) == 0:
			if component_file.name.endswith('js') or component_file.name.endswith('jsx'):
				component_name = extract_file_name_no_ext(component_file.name, '.js')
				component_names.append(component_name)
		else:
			component_names.extend(extract_component_names(agent=agent, proj_tree=component_file))
	return component_names


if __name__ == '__main__':
	dotenv.load_dotenv(dotenv.find_dotenv())
	agent = FrontendAgent()
	proj_structure = agent.generate_project_structure(proj_name='chat app')
	
	proj_tree = build_tree_from_indented_text(proj_structure)
	proj_tree.pre_order_traverse()
 
	components_dir_subtree = proj_tree.find_node_by_name('components')
	pages_dir_subtree = proj_tree.find_node_by_name('pages')
	if components_dir_subtree is None:
		raise Exception('components dir is missing')
	
	
	component_names = extract_component_names(agent=agent, proj_tree=components_dir_subtree)
	pages_names = extract_component_names(agent=agent, proj_tree=pages_dir_subtree)
	print(component_names)
	print(pages_names)
	
	components_dir_path = file_manager.create_overwrite_directory('./temp', 'components')
	pages_dir_path = file_manager.create_overwrite_directory('./temp', 'pages')
	agent.generate_component_batch(components_dir_path, component_names)
	agent.generate_page_batch(pages_dir_path, pages_names, component_names, '../components')

 