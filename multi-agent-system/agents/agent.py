import asyncio
from typing import Dict, List, Optional, Any
from integrations.service_connector import CrewAIConnector, TaskadeConnector, AbacusConnector
from abc import ABC, abstractmethod
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Agent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, agent_id: str, capabilities: List[str]):
        """Initialize agent with optional service connectors."""
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.message_queue = asyncio.Queue()
        self.busy = False
        # Service connectors will be set by the environment
        self.crewai_connector: Optional[CrewAIConnector] = None
        self.taskade_connector: Optional[TaskadeConnector] = None
        self.abacus_connector: Optional[AbacusConnector] = None
        logger.info(f"Agent {agent_id} initialized with capabilities: {capabilities}")

    async def send_message(self, target_agent: 'Agent', message: Dict[str, Any]):
        """Send a message to another agent."""
        await target_agent.message_queue.put({
            'from': self.agent_id,
            'content': message
        })
        logger.info(f"Agent {self.agent_id} sent message to {target_agent.agent_id}")

    async def receive_message(self) -> Optional[Dict[str, Any]]:
        """Receive a message from the message queue."""
        try:
            message = await self.message_queue.get()
            logger.info(f"Agent {self.agent_id} received message: {message}")
            return message
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            return None

    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task and return the result."""
        pass

class BuilderAgent(Agent):
    """Specialized agent for building applications with local support."""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, capabilities=['build', 'deploy', 'local_build'])
        self.supported_frameworks = ['react', 'vue', 'flask', 'fastapi']
        self.build_templates = {}
        self.local_build_config = {}
        
    async def _create_crewai_task(self, framework: str, project_name: str) -> Optional[Dict[str, Any]]:
        """Create a task in CrewAI for the build process."""
        if self.crewai_connector:
            return await self.crewai_connector.create_agent({
                'task': f'Build {framework} application: {project_name}',
                'role': 'builder',
                'goal': f'Successfully create and configure {framework} application'
            })
        return None

    async def _create_taskade_item(self, framework: str, project_name: str) -> Optional[Dict[str, Any]]:
        """Create a task item in Taskade for tracking."""
        if self.taskade_connector:
            return await self.taskade_connector.create_task({
                'title': f'Build {framework} app: {project_name}',
                'description': f'Create and configure new {framework} application',
                'status': 'in_progress'
            })
        return None

    async def create_local_project(self, framework: str, project_name: str, project_path: str) -> Dict[str, Any]:
        """Create a local project setup using templates."""
        if framework not in self.supported_frameworks:
            return {'status': 'error', 'message': f'Unsupported framework: {framework}'}
        
        try:
            from utils.template_manager import TemplateManager
            template_manager = TemplateManager()
            
            # Apply project template
            logger.info(f"Creating {framework} project: {project_name} at {project_path}")
            result = template_manager.apply_template(framework, project_path, project_name)
            
            if result['status'] != 'success':
                return result
            
            # Run installation commands
            install_result = await template_manager.run_install_commands(framework, project_path)
            if install_result['status'] != 'success':
                return install_result
            
            # Store local build configuration
            self.local_build_config[project_name] = {
                'framework': framework,
                'created_at': datetime.now().isoformat(),
                'project_path': project_path,
                'start_command': template_manager.get_start_command(framework)
            }
            
            return {
                'status': 'success',
                'message': f'Local project {project_name} created successfully',
                'project_details': self.local_build_config[project_name],
                'start_command': template_manager.get_start_command(framework)
            }
            
        except Exception as e:
            logger.error(f"Error creating local project: {e}")
            return {
                'status': 'error',
                'message': f'Failed to create project: {str(e)}'
            }
        
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a build task."""
        if task.get('type') == 'local_build':
            framework = task.get('framework')
            project_name = task.get('project_name')
            project_path = task.get('project_path')
            
            if not project_path:
                return {
                    'status': 'error',
                    'message': 'Project path is required for local build'
                }
                
            return await self.create_local_project(framework, project_name, project_path)
        
        if task.get('type') != 'build':
            return {'status': 'error', 'message': 'Unsupported task type'}

        framework = task.get('framework')
        project_name = task.get('project_name')
        
        if framework not in self.supported_frameworks:
            return {'status': 'error', 'message': f'Unsupported framework: {framework}'}

        try:
            self.busy = True
            logger.info(f"BuilderAgent {self.agent_id} starting build for {framework}")
            
            # Create tasks in integrated services
            crewai_task = await self._create_crewai_task(framework, project_name)
            taskade_item = await self._create_taskade_item(framework, project_name)
            
            # Get build recommendations from Abacus if available
            if self.abacus_connector:
                build_prediction = await self.abacus_connector.get_model_prediction({
                    'framework': framework,
                    'project_type': 'application',
                    'context': project_name
                })
            
            # Simulate build process
            await asyncio.sleep(2)
            
            result = {
                'status': 'success',
                'message': f'Successfully built {framework} application',
                'framework': framework,
                'timestamp': asyncio.get_running_loop().time(),
                'crewai_task_id': crewai_task.get('id') if crewai_task else None,
                'taskade_item_id': taskade_item.get('id') if taskade_item else None
            }
            
            logger.info(f"BuilderAgent {self.agent_id} completed build: {result}")
            return result
        except Exception as e:
            logger.error(f"Build error: {e}")
            return {'status': 'error', 'message': str(e)}
        finally:
            self.busy = False

class ProjectManagerAgent(Agent):
    """Agent responsible for managing project creation and coordination."""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, capabilities=['project_management', 'coordination'])
        self.active_projects = {}

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a project management task."""
        task_type = task.get('type')
        if task_type == 'create_project':
            project_name = task.get('name')
            framework = task.get('framework')
            
            self.active_projects[project_name] = {
                'status': 'initializing',
                'framework': framework,
                'created_at': asyncio.get_running_loop().time()
            }
            
            logger.info(f"ProjectManagerAgent {self.agent_id} created project: {project_name}")
            return {
                'status': 'success',
                'message': f'Project {project_name} initialized',
                'project_details': self.active_projects[project_name]
            }
        
        return {'status': 'error', 'message': 'Unsupported task type'}
