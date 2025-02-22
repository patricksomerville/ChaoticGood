#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BoulevardInstaller:
    def __init__(self):
        self.home_dir = str(Path.home())
        self.boulevard_dir = os.path.join(self.home_dir, '.boulevard')
        self.config_dir = os.path.join(self.boulevard_dir, 'config')
        self.install_dir = os.path.join(self.home_dir, 'boulevard')

    def create_directories(self):
        """Create necessary directories for Boulevard."""
        dirs = [
            self.boulevard_dir,
            self.config_dir,
            os.path.join(self.boulevard_dir, 'logs'),
            os.path.join(self.boulevard_dir, 'data'),
            os.path.join(self.boulevard_dir, 'keys'),
            self.install_dir
        ]
        
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")

    def safe_copy(self, src, dst):
        """Safely copy a file or directory."""
        try:
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                logger.info(f"Copied directory: {os.path.basename(src)}")
            else:
                if os.path.exists(dst):
                    os.remove(dst)
                shutil.copy2(src, dst)
                logger.info(f"Copied file: {os.path.basename(src)}")
        except Exception as e:
            logger.error(f"Error copying {src} to {dst}: {e}")
            raise

    def copy_files(self):
        """Copy Boulevard files to installation directory."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # First, clean the installation directory
        if os.path.exists(self.install_dir):
            shutil.rmtree(self.install_dir)
        os.makedirs(self.install_dir)
        
        # Copy all Python files and directories
        for item in os.listdir(current_dir):
            src = os.path.join(current_dir, item)
            dst = os.path.join(self.install_dir, item)
            
            if item == 'install.py' or item.startswith('.'):
                continue
                
            self.safe_copy(src, dst)

    def create_config_template(self):
        """Create a template configuration file."""
        config_template = {
            "api_keys": {
                "crewai": "your_crewai_api_key",
                "taskade": "your_taskade_api_key",
                "abacus": "your_abacus_api_key",
                "newsapi": "your_newsapi_key",
                "binance_api": "your_binance_api_key",
                "binance_secret": "your_binance_secret_key",
                "twitter": "your_twitter_api_key",
                "reddit": "your_reddit_api_key"
            },
            "settings": {
                "monitoring_interval": 300,
                "data_retention_days": 30,
                "log_level": "INFO"
            }
        }
        
        config_path = os.path.join(self.config_dir, 'config.json')
        with open(config_path, 'w') as f:
            json.dump(config_template, f, indent=2)
        logger.info(f"Created configuration template: {config_path}")

    def create_launcher(self):
        """Create a launcher script for Boulevard."""
        launcher_content = f'''#!/bin/bash
export PYTHONPATH="{self.install_dir}:$PYTHONPATH"
cd {self.install_dir}
python3 main.py --config {os.path.join(self.config_dir, 'config.json')} "$@"
'''
        
        launcher_path = os.path.join(self.install_dir, 'boulevard')
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        
        # Make launcher executable
        os.chmod(launcher_path, 0o755)
        logger.info(f"Created launcher script: {launcher_path}")

    def create_requirements(self):
        """Create requirements.txt file."""
        requirements = [
            "aiohttp>=3.8.0",
            "cryptography>=3.4.7",
            "python-dotenv>=0.19.0",
            "sqlalchemy>=1.4.23",
            "requests>=2.26.0",
            "websockets>=10.0",
            "python-binance>=1.0.15",
            "tweepy>=4.4.0",
            "praw>=7.4.0",
            "newsapi-python>=0.2.6"
        ]
        
        req_path = os.path.join(self.install_dir, 'requirements.txt')
        with open(req_path, 'w') as f:
            f.write('\n'.join(requirements))
        logger.info(f"Created requirements file: {req_path}")

    def install_dependencies(self):
        """Install required Python packages."""
        try:
            subprocess.run([
                sys.executable, 
                '-m', 
                'pip', 
                'install', 
                '--user',
                '-r', 
                os.path.join(self.install_dir, 'requirements.txt')
            ], check=True)
            logger.info("Installed dependencies successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing dependencies: {e}")
            raise

    def install(self):
        """Run the complete installation process."""
        try:
            logger.info("Starting Boulevard installation...")
            
            # Create necessary directories
            self.create_directories()
            
            # Copy files
            self.copy_files()
            
            # Create configuration template
            self.create_config_template()
            
            # Create launcher
            self.create_launcher()
            
            # Create requirements.txt
            self.create_requirements()
            
            # Install dependencies
            self.install_dependencies()
            
            # Print success message
            print("\nBoulevard has been successfully installed!")
            print("\nTo complete the setup:")
            print(f"1. Edit the configuration file at: {os.path.join(self.config_dir, 'config.json')}")
            print("2. Add your API keys to the configuration file")
            print(f"\nTo run Boulevard:")
            print(f"{os.path.join(self.install_dir, 'boulevard')}")
            print("\nOptionally, you can add Boulevard to your PATH:")
            print(f"echo 'export PATH=\"$PATH:{self.install_dir}\"' >> ~/.bashrc")
            print("source ~/.bashrc")
            
        except Exception as e:
            logger.error(f"Installation failed: {e}")
            raise

if __name__ == "__main__":
    installer = BoulevardInstaller()
    installer.install()
