"""
Configuração e gerenciamento de chave API OpenAI
"""
import os
import json
from pathlib import Path
from typing import Optional


class Config:
    """Gerenciador de configurações da aplicação"""

    CONFIG_DIR = Path.home() / ".legal_document_analyzer"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    def __init__(self):
        """Inicializa o gerenciador de configurações"""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self._load_config()

    def _load_config(self) -> dict:
        """Carrega configurações do arquivo local"""
        if self.CONFIG_FILE.exists():
            with open(self.CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_api_key(self, api_key: str) -> None:
        """
        Salva a chave API OpenAI localmente

        Args:
            api_key: Chave API da OpenAI
        """
        config = self._load_config()
        config['openai_api_key'] = api_key

        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)

        # Define também como variável de ambiente para a sessão atual
        os.environ['OPENAI_API_KEY'] = api_key

    def get_api_key(self) -> Optional[str]:
        """
        Recupera a chave API OpenAI

        Returns:
            Chave API ou None se não estiver configurada
        """
        # Primeiro tenta carregar do arquivo
        config = self._load_config()
        api_key = config.get('openai_api_key')

        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            return api_key

        # Se não encontrar, tenta da variável de ambiente
        return os.environ.get('OPENAI_API_KEY')

    def delete_api_key(self) -> None:
        """Remove a chave API salva"""
        config = self._load_config()
        if 'openai_api_key' in config:
            del config['openai_api_key']

            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)

        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']

    def is_configured(self) -> bool:
        """
        Verifica se a chave API está configurada

        Returns:
            True se configurada, False caso contrário
        """
        return self.get_api_key() is not None
