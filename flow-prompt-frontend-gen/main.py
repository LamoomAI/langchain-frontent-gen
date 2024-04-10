from flow_prompt import FlowPrompt, PipePrompt
from flow_prompt import AIModelsBehaviour, AzureAIModel, AttemptToCall
import os
import dotenv

class FrontendAgent:
	def __init__(self) -> None:
		fp_api_token = os.environ['FLOW_PROMPT_API_KEY']
		# openai_key = os.environ['']
		self.__llm_instance = FlowPrompt(api_token=fp_api_token, openai_key=)
		self.__project_prompt = PipePrompt('generate_react_project_structure')
		self.__project_prompt.add(content='Create the project folder structure for a {app_name} web application \
												in React. Use double spaces for indentation', role='system')
		self.__component_prompt = PipePrompt('generate_react_component')
		self.behavior = AIModelsBehaviour(
			attempts=[
				AttemptToCall(
					ai_model=AzureAIModel(
						realm="westus",
						deployment_id="gpt-4-turbo",
						max_tokens=40_000,
						support_functions=True,
						should_verify_client_has_creds=False,
					),
					weight=100,
				),
			]
		)
		

	def generate_project_structure(self, proj_name: str) -> str:
		proj_context = {'app_name': proj_name}
		llm_response = self.__llm_instance.call(self.__project_prompt.id, proj_context, self.behavior)
		

	def generate_component(self, comp_name: str) -> str:
		comp_prompt_text = 'write a react component for a {component_name}'.format(component_name=comp_name)
		self.__component_prompt.add()
		return

if __name__ == '__main__':
	dotenv.load_dotenv(dotenv.find_dotenv())
	agent = FrontendAgent()
	print(agent.generate_project_structure(proj_name='chat app'))
