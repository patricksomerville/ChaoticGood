import asyncio
from typing import List, Dict, Any, Optional
from agents.agent import Agent
from integrations.service_connector import CrewAIConnector, TaskadeConnector, AbacusConnector
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Environment:
    """Class to manage the multi-agent environment with local development support."""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.crewai_connector: Optional[CrewAIConnector] = None
        self.taskade_connector: Optional[TaskadeConnector] = None
        self.abacus_connector: Optional[AbacusConnector] = None
        self.local_projects_dir = os.path.expanduser("~/projects")
        os.makedirs(self.local_projects_dir, exist_ok=True)
        logger.info("Environment initialized with local development support.")

    def set_service_connectors(self, 
                             crewai_connector: CrewAIConnector,
                             taskade_connector: TaskadeConnector,
                             abacus_connector: AbacusConnector):
        """Set service connectors for the environment."""
        self.crewai_connector = crewai_connector
        self.taskade_connector = taskade_connector
        self.abacus_connector = abacus_connector

    def register_agent(self, agent: Agent):
        """Register an agent in the environment and set up its service connectors."""
        self.agents[agent.agent_id] = agent
        
        # Set up service connectors for the agent
        agent.crewai_connector = self.crewai_connector
        agent.taskade_connector = self.taskade_connector
        agent.abacus_connector = self.abacus_connector
        
        logger.info(f"Agent {agent.agent_id} registered in the environment with service connectors.")

    def get_project_path(self, project_name: str) -> str:
        """Get the local path for a project."""
        return os.path.join(self.local_projects_dir, project_name)

    async def create_local_project(self, framework: str, project_name: str) -> Dict[str, Any]:
        """Create a new local project directory."""
        project_path = self.get_project_path(project_name)
        
        try:
            os.makedirs(project_path, exist_ok=True)
            logger.info(f"Created local project directory: {project_path}")
            
            # Create basic project structure
            with open(os.path.join(project_path, 'README.md'), 'w') as f:
                f.write(f"# {project_name}\n\nA {framework} project.")
                
            return {
                'status': 'success',
                'message': f'Created local project directory at {project_path}',
                'project_path': project_path
            }
        except Exception as e:
            logger.error(f"Error creating local project: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }

    async def distribute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Distribute a task to an appropriate agent."""
        # Handle local project creation
        if task.get('type') == 'local_build':
            project_result = await self.create_local_project(
                task.get('framework'),
                task.get('project_name')
            )
            if project_result['status'] != 'success':
                return project_result
            
            # Add project path to task for the agent
            task['project_path'] = project_result['project_path']
        
        # Find suitable agent for the task
        for agent in self.agents.values():
            if agent.agent_id in task.get('target_agents', []):
                logger.info(f"Distributing task to {agent.agent_id}")
                result = await agent.process_task(task)
                logger.info(f"Task result from {agent.agent_id}: {result}")
                return result
                
        logger.warning("No suitable agent found for the task.")
        return {'status': 'error', 'message': 'No suitable agent found'}

    async def run(self):
        """Run the environment and manage agent interactions."""
        while True:
            await asyncio.sleep(1)  # Keep the environment running
