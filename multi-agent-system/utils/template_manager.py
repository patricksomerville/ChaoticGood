import json
import os
from typing import Dict, Any, Optional
import logging
import shutil
from pathlib import Path
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TemplateManager:
    """Manages project templates and their application."""
    
    def __init__(self, templates_dir: str = None):
        self.templates_dir = templates_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'templates'
        )
        logger.info(f"Template manager initialized with directory: {self.templates_dir}")

    def get_template(self, framework: str) -> Optional[Dict[str, Any]]:
        """Load a template configuration for the specified framework."""
        template_path = os.path.join(self.templates_dir, framework, 'template.json')
        try:
            with open(template_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Template not found for framework: {framework}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing template for {framework}: {e}")
            return None

    def apply_template(self, framework: str, project_path: str, project_name: str) -> Dict[str, Any]:
        """Apply a template to create a new project."""
        template = self.get_template(framework)
        if not template:
            return {
                'status': 'error',
                'message': f'Template not found for framework: {framework}'
            }

        try:
            # Create project directory if it doesn't exist
            os.makedirs(project_path, exist_ok=True)

            # Create files from template
            for file_path, file_config in template['files'].items():
                # Replace template variables
                content = file_config['content']
                if isinstance(content, str):
                    content = content.replace('{{project_name}}', project_name)
                elif isinstance(content, dict):
                    content = json.dumps(content, indent=2).replace('{{project_name}}', project_name)
                
                # Create file
                full_path = os.path.join(project_path, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, 'w') as f:
                    if isinstance(content, dict):
                        json.dump(content, f, indent=2)
                    else:
                        f.write(content)

            logger.info(f"Applied {framework} template to {project_path}")
            return {
                'status': 'success',
                'message': f'Successfully created {framework} project: {project_name}',
                'project_path': project_path,
                'framework': framework
            }

        except Exception as e:
            logger.error(f"Error applying template: {e}")
            return {
                'status': 'error',
                'message': f'Failed to apply template: {str(e)}'
            }

    async def run_install_commands(self, framework: str, project_path: str) -> Dict[str, Any]:
        """Run installation commands for the project."""
        template = self.get_template(framework)
        if not template:
            return {
                'status': 'error',
                'message': f'Template not found for framework: {framework}'
            }

        try:
            results = []
            for cmd in template.get('install_commands', []):
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    cwd=project_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                result = {
                    'command': cmd,
                    'success': process.returncode == 0,
                    'output': stdout.decode() if stdout else '',
                    'error': stderr.decode() if stderr else ''
                }
                results.append(result)
                
                if not result['success']:
                    return {
                        'status': 'error',
                        'message': f'Installation command failed: {cmd}',
                        'results': results
                    }

            return {
                'status': 'success',
                'message': 'Successfully installed project dependencies',
                'results': results
            }

        except Exception as e:
            logger.error(f"Error running install commands: {e}")
            return {
                'status': 'error',
                'message': f'Failed to run install commands: {str(e)}'
            }

    def get_start_command(self, framework: str) -> Optional[str]:
        """Get the command to start the project."""
        template = self.get_template(framework)
        if template and template.get('start_commands'):
            return template['start_commands'][0]
        return None

    def list_templates(self) -> Dict[str, Any]:
        """List all available templates."""
        try:
            templates = []
            for framework in os.listdir(self.templates_dir):
                template_path = os.path.join(self.templates_dir, framework, 'template.json')
                if os.path.exists(template_path):
                    with open(template_path, 'r') as f:
                        template = json.load(f)
                        templates.append({
                            'framework': framework,
                            'name': template.get('name'),
                            'version': template.get('version')
                        })
            
            return {
                'status': 'success',
                'templates': templates
            }
        except Exception as e:
            logger.error(f"Error listing templates: {e}")
            return {
                'status': 'error',
                'message': f'Failed to list templates: {str(e)}'
            }
