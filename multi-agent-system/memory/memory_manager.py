import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
import sqlite3
from pathlib import Path
from cryptography.fernet import Fernet
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages persistent storage and memory for Boulevard."""
    
    def __init__(self, data_dir: str = "~/.boulevard"):
        self.data_dir = os.path.expanduser(data_dir)
        self.setup_storage()
        self.encryption_key = self._load_or_create_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self._init_database()

    def setup_storage(self):
        """Set up the storage directory structure."""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'keys'), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'cache'), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'logs'), exist_ok=True)

    def _load_or_create_key(self) -> bytes:
        """Load or create encryption key."""
        key_path = os.path.join(self.data_dir, 'keys', 'encryption.key')
        if os.path.exists(key_path):
            with open(key_path, 'rb') as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            with open(key_path, 'wb') as key_file:
                key_file.write(key)
            return key

    def _init_database(self):
        """Initialize the SQLite database."""
        db_path = os.path.join(self.data_dir, 'boulevard.db')
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # API Keys table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    service TEXT PRIMARY KEY,
                    encrypted_key TEXT,
                    last_updated TIMESTAMP
                )
            ''')
            
            # Trends table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT,
                    trend_data TEXT,
                    timestamp TIMESTAMP
                )
            ''')
            
            # Content table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    content_data TEXT,
                    performance_metrics TEXT,
                    created_at TIMESTAMP
                )
            ''')
            
            # Trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    action TEXT,
                    amount REAL,
                    price REAL,
                    timestamp TIMESTAMP
                )
            ''')
            
            # Agent States table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_states (
                    agent_id TEXT PRIMARY KEY,
                    state_data TEXT,
                    last_updated TIMESTAMP
                )
            ''')
            
            conn.commit()

    def store_api_keys(self, keys: Dict[str, str]):
        """Securely store API keys."""
        db_path = os.path.join(self.data_dir, 'boulevard.db')
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            for service, key in keys.items():
                encrypted_key = self.cipher_suite.encrypt(key.encode())
                cursor.execute('''
                    INSERT OR REPLACE INTO api_keys (service, encrypted_key, last_updated)
                    VALUES (?, ?, ?)
                ''', (service, encrypted_key.decode(), datetime.now()))
            conn.commit()

    def get_api_keys(self) -> Dict[str, str]:
        """Retrieve stored API keys."""
        db_path = os.path.join(self.data_dir, 'boulevard.db')
        keys = {}
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT service, encrypted_key FROM api_keys')
            for service, encrypted_key in cursor.fetchall():
                decrypted_key = self.cipher_suite.decrypt(encrypted_key.encode()).decode()
                keys[service] = decrypted_key
        return keys

    def store_trend(self, source: str, trend_data: Dict[str, Any]):
        """Store trend information."""
        db_path = os.path.join(self.data_dir, 'boulevard.db')
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trends (source, trend_data, timestamp)
                VALUES (?, ?, ?)
            ''', (source, json.dumps(trend_data), datetime.now()))
            conn.commit()

    def store_content(self, content_type: str, content_data: Dict[str, Any], metrics: Dict[str, Any]):
        """Store generated content and its performance metrics."""
        db_path = os.path.join(self.data_dir, 'boulevard.db')
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO content (type, content_data, performance_metrics, created_at)
                VALUES (?, ?, ?, ?)
            ''', (content_type, json.dumps(content_data), json.dumps(metrics), datetime.now()))
            conn.commit()

    def store_trade(self, trade_data: Dict[str, Any]):
        """Store trade information."""
        db_path = os.path.join(self.data_dir, 'boulevard.db')
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trades (symbol, action, amount, price, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                trade_data['symbol'],
                trade_data['action'],
                trade_data['amount'],
                trade_data['price'],
                datetime.now()
            ))
            conn.commit()

    def store_agent_state(self, agent_id: str, state_data: Dict[str, Any]):
        """Store agent state information."""
        db_path = os.path.join(self.data_dir, 'boulevard.db')
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO agent_states (agent_id, state_data, last_updated)
                VALUES (?, ?, ?)
            ''', (agent_id, json.dumps(state_data), datetime.now()))
            conn.commit()

    def get_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve agent state information."""
        db_path = os.path.join(self.data_dir, 'boulevard.db')
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT state_data FROM agent_states WHERE agent_id = ?', (agent_id,))
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
        return None

    def get_recent_trends(self, limit: int = 10) -> list:
        """Retrieve recent trends."""
        db_path = os.path.join(self.data_dir, 'boulevard.db')
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT source, trend_data, timestamp 
                FROM trends 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            return [
                {
                    'source': row[0],
                    'data': json.loads(row[1]),
                    'timestamp': row[2]
                }
                for row in cursor.fetchall()
            ]

    def get_content_performance(self, content_type: str = None, limit: int = 10) -> list:
        """Retrieve content performance metrics."""
        db_path = os.path.join(self.data_dir, 'boulevard.db')
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            query = '''
                SELECT type, content_data, performance_metrics, created_at 
                FROM content 
            '''
            params = []
            if content_type:
                query += ' WHERE type = ?'
                params.append(content_type)
            query += ' ORDER BY created_at DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            return [
                {
                    'type': row[0],
                    'content': json.loads(row[1]),
                    'metrics': json.loads(row[2]),
                    'created_at': row[3]
                }
                for row in cursor.fetchall()
            ]

    def get_trade_history(self, symbol: str = None, limit: int = 10) -> list:
        """Retrieve trade history."""
        db_path = os.path.join(self.data_dir, 'boulevard.db')
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM trades'
            params = []
            if symbol:
                query += ' WHERE symbol = ?'
                params.append(symbol)
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            return [
                {
                    'symbol': row[1],
                    'action': row[2],
                    'amount': row[3],
                    'price': row[4],
                    'timestamp': row[5]
                }
                for row in cursor.fetchall()
            ]
