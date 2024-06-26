import asyncio
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
import dotenv

from tree import TreeNode, build_tree_from_indented_text
import prompt_templates
import file_manager

dotenv.load_dotenv(dotenv.find_dotenv())


class FrontendAgent:
	def __init__(self):
		self.__llm_instance = OpenAI(max_tokens=3900)
		self.__component_prompt_template = PromptTemplate(input_variables=['component'], template='Write a React functional component for {component}. Please use tailwind and Lucide icons. Do not use descriptions')
		self.__project_prompt_template = PromptTemplate(input_variables=['project_name'], template=prompt_templates.project_structure_template)
		self.pages_prompt = PromptTemplate(input_variables=['page_name', 'project_name', 'components'], input_types={'page_name': str, 'project_name': str, 'components': list[str]}, template='Create a {page_name} \
																		 react page component for {project_name}. You may use {components} if any of these belong on the page. Don`t explain anything, just write code. All components are located in ../components directory')
		self.pages_chain = self.pages_prompt | self.__llm_instance

	def generate_project_structure(self, project_name: str):
		# self.__project_name = project_name
		prompt = self.__project_prompt_template.format(project_name=project_name)
		return self.__llm_instance.invoke(prompt)

	def invoke_component_code(self, name: str) -> str:
		component_prompt = self.__component_prompt_template.format(component=name)
		code = self.__llm_instance.invoke(component_prompt)
		return code
	
	def generate_component_code(self, prompts: list[str]) -> list[str]:
		component_prompts = [self.__component_prompt_template.format(component=prompt) for prompt in prompts]
		generated_code = self.__llm_instance.generate(component_prompts)
		return list(map(lambda comp: comp[0].text, generated_code.generations))

def extract_file_name_no_ext(full_name: str, extension: str) -> str:
	return full_name.split(extension)[0]

def generate_components(agent: FrontendAgent, proj_tree: TreeNode) -> list[str]:
	component_names = []
	for component_file in proj_tree.children:
		# Check if it's a leaf
		if len(component_file.children) == 0:
			if component_file.name.endswith('js') or component_file.name.endswith('jsx'):
				component_name = extract_file_name_no_ext(component_file.name, '.js')
				component_names.append(component_name)
		else:
			component_names.extend(generate_components(agent=agent, proj_tree=component_file))
	return component_names


async def main():
	agent = FrontendAgent()
	project_name = 'chat app'
	proj_frame = agent.generate_project_structure(project_name)
	
	print('TREE')
	project_tree = build_tree_from_indented_text(proj_frame)
	project_tree.pre_order_traverse()

	components_dir = project_tree.find_node_by_name(target_name='components')
	components_dir.pre_order_traverse()

	tree_components = generate_components(agent=agent, proj_tree=components_dir)
	print(tree_components)

	# Generate components
	comp_dir_path = file_manager.create_overwrite_directory('./temp', 'components')

	# * batch generate example
	component_codes = agent.generate_component_code([f'a {component_name} for {project_name}'] for component_name in tree_components)
	for component_code, component_name in zip(component_codes, tree_components):
		file_manager.create_file(comp_dir_path, f'{component_name}.js', component_code)

	# Aggregate into pages
	pages_dir_subtree = project_tree.find_node_by_name(target_name='pages')
	tree_pages = None
	if pages_dir_subtree is not None:
		tree_pages = generate_components(agent=agent, proj_tree=pages_dir_subtree)

		gen_pages = await agent.pages_chain.abatch([{'page_name': curr_page, 'project_name': project_name, 'components': tree_components} for curr_page in tree_pages])
		page_dir = file_manager.create_overwrite_directory('./temp', 'pages')
		for page_code, page_name in zip(gen_pages, tree_pages):
			file_manager.create_file(page_dir, f'{page_name}.js', page_code)


if __name__ == '__main__':
  	asyncio.run(main())