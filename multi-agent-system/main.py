import asyncio
import argparse
import logging
import json
import os
from typing import Dict, Any
from agents.agent import BuilderAgent, ProjectManagerAgent
from environment.environment import Environment
from memory.memory_manager import MemoryManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalAppBuilder:
    """Local application builder system."""
    
    def __init__(self):
        self.memory = MemoryManager()
        self.environment = Environment()
        self.setup_agents()
        logger.info("Local App Builder system initialized")

    def setup_agents(self):
        """Initialize and register the required agents."""
        try:
            # Initialize agents
            builder = BuilderAgent("builder-1")
            project_manager = ProjectManagerAgent("pm-1")
            
            # Register agents
            self.environment.register_agent(builder)
            self.environment.register_agent(project_manager)
            
            logger.info("Agents initialized and registered")
        except Exception as e:
            logger.error(f"Error setting up agents: {e}")
            raise

    async def create_project(self, framework: str, project_name: str) -> Dict[str, Any]:
        """Create a new local project."""
        try:
            # Create project management task
            pm_task = {
                'type': 'create_project',
                'name': project_name,
                'framework': framework,
                'target_agents': ['pm-1']
            }
            
            # Initialize project through project manager
            pm_result = await self.environment.distribute_task(pm_task)
            if pm_result['status'] != 'success':
                return pm_result
            
            # Create local build task
            build_task = {
                'type': 'local_build',
                'framework': framework,
                'project_name': project_name,
                'target_agents': ['builder-1']
            }
            
            # Execute local build
            build_result = await self.environment.distribute_task(build_task)
            
            if build_result['status'] == 'success':
                # Store project details in memory
                self.memory.store_project_details(project_name, {
                    'framework': framework,
                    'status': 'created',
                    'build_result': build_result
                })
            
            return build_result
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return {
                'status': 'error',
                'message': f'Failed to create project: {str(e)}'
            }

    async def list_projects(self) -> Dict[str, Any]:
        """List all local projects."""
        try:
            projects = self.memory.get_all_projects()
            return {
                'status': 'success',
                'projects': projects
            }
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return {
                'status': 'error',
                'message': f'Failed to list projects: {str(e)}'
            }

async def main():
    parser = argparse.ArgumentParser(description='Local App Builder - Create and manage local applications')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create project command
    create_parser = subparsers.add_parser('create', help='Create a new project')
    create_parser.add_argument('framework', choices=['react', 'vue', 'flask', 'fastapi'], help='Project framework')
    create_parser.add_argument('name', help='Project name')
    
    # List projects command
    subparsers.add_parser('list', help='List all projects')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize the system
    app_builder = LocalAppBuilder()
    
    try:
        if args.command == 'create':
            logger.info(f"Creating new {args.framework} project: {args.name}")
            result = await app_builder.create_project(args.framework, args.name)
            if result['status'] == 'success':
                logger.info(f"Successfully created project {args.name}")
                logger.info(f"Project details: {json.dumps(result, indent=2)}")
            else:
                logger.error(f"Failed to create project: {result['message']}")
                
        elif args.command == 'list':
            result = await app_builder.list_projects()
            if result['status'] == 'success':
                logger.info("Available projects:")
                for project in result['projects']:
                    logger.info(f"- {project['name']} ({project['framework']})")
            else:
                logger.error(f"Failed to list projects: {result['message']}")
                
    except KeyboardInterrupt:
        logger.info("Shutting down Local App Builder...")
    except Exception as e:
        logger.error(f"Error in Local App Builder: {e}")

if __name__ == "__main__":
    asyncio.run(main())
