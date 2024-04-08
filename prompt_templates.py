project_structure_template = """
Generate a textual representation of React project structure for a {project_name} web application.
Don`t provide explanation. Just write it out using tabs for indentation and no other elements like hyphens or asterisks.
Don`t generate any css files or assets. Use tailwind.css for styles
Please provide a list of items in the following format:

src
  folder
    subfolder
    subfolder
  folder
    subfolder
    subfolder
      file
      file

Make sure there's only one root folder (src)
Don`t repeat the format in the response. Just the data you generated
"""

project_structure_template_json="""
Generate a textual representation of React project structure for a {project_name} web application.
Please follow the following structure:
{'template': 'react project',
  'explanation': false,
  'format': {
    'type': "tree",
    'indentation': "2 spaces",
    'prefix': false
  },
  "assets": false,
  "imports": ["tailwind"]}

"""
