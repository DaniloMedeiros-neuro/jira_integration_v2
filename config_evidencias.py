"""
Configurações do Sistema de Evidências de Testes
================================================

Este arquivo contém todas as configurações para o sistema de evidências
melhorado, incluindo validações, formatos suportados e configurações
de processamento.
"""

import os
from typing import Dict, List, Any

# ========================================
# CONFIGURAÇÕES GERAIS
# ========================================

# Configurações de processamento
PROCESSING_CONFIG = {
    'max_file_size_mb': 10,
    'supported_formats': ['.html', '.htm'],
    'temp_dir': 'temp_evidence',
    'output_dir': 'prints_tests',
    'log_dir': 'logs',
    'backup_enabled': True,
    'backup_dir': 'backups'
}

# Configurações de screenshots
SCREENSHOT_CONFIG = {
    'default_width': 1280,
    'default_height': 720,
    'quality': 90,
    'format': 'PNG',
    'enable_real_screenshots': False,  # Controlado por variável de ambiente
    'selenium_timeout': 30,
    'selenium_headless': True,
    'chrome_options': [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-images',
        '--disable-javascript'
    ]
}

# Configurações de validação de logs
LOG_VALIDATION_CONFIG = {
    'min_score_valid': 30,
    'min_score_probably_valid': 20,
    'required_keywords': ['test', 'teste', 'pass', 'fail', 'success', 'error'],
    'framework_indicators': {
        'robot_framework': [
            'robot framework',
            'keyword',
            'suite',
            'test case'
        ],
        'selenium': [
            'selenium',
            'webdriver',
            'browser'
        ],
        'junit': [
            'junit',
            'testng',
            'test class'
        ],
        'cucumber': [
            'cucumber',
            'gherkin',
            'scenario',
            'feature'
        ]
    },
    'css_classes': [
        'test-result', 'test-pass', 'test-fail', 'test-success', 'test-error',
        'pass', 'fail', 'success', 'error', 'skip', 'warn',
        'robot', 'keyword', 'suite', 'test'
    ],
    'icons': {
        'success': ['✅', '✓', 'PASS', 'SUCCESS', 'SUCESSO'],
        'failure': ['❌', '✗', 'FAIL', 'ERROR', 'FALHA']
    }
}

# Configurações de extração de códigos
CODE_EXTRACTION_CONFIG = {
    'patterns': [
        r'([A-Z]{2,4}-\d+)',  # PROJ-123, CREDT-456
        r'([A-Z]+-\d+)',      # QUALQUER-123
        r'([A-Z]{2,4}\d+)',   # PROJ123, CREDT456 (sem hífen)
        r'(BC-\d+)',          # Padrão específico BC
        r'(TEST-\d+)',        # Padrão específico TEST
        r'(BUG-\d+)',         # Padrão específico BUG
        r'(FEATURE-\d+)',     # Padrão específico FEATURE
    ],
    'fallback_prefix': 'TESTE',
    'max_fallback_number': 999
}

# Configurações de integração com Jira
JIRA_CONFIG = {
    'max_attachment_size_mb': 10,
    'supported_attachment_types': ['.png', '.jpg', '.jpeg', '.gif', '.txt'],
    'comment_template': 'evidencias_comment_template.md',
    'auto_comment': True,
    'validate_issue_key': True,
    'issue_key_pattern': r'^[A-Z]+-\d+$'
}

# Configurações de logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'file_rotation': 'daily',
    'max_log_files': 30,
    'log_to_console': True,
    'log_to_file': True
}

# Configurações de notificações
NOTIFICATION_CONFIG = {
    'enable_notifications': True,
    'notification_types': ['success', 'error', 'warning', 'info'],
    'auto_hide_delay': 5000,  # 5 segundos
    'max_notifications': 5
}

# ========================================
# TEMPLATES HTML PARA SCREENSHOTS
# ========================================

SCREENSHOT_TEMPLATES = {
    'default': {
        'title': 'Evidência de Teste',
        'theme': 'modern',
        'include_timestamp': True,
        'include_environment_info': True,
        'include_test_details': True
    },
    'minimal': {
        'title': 'Test Evidence',
        'theme': 'minimal',
        'include_timestamp': False,
        'include_environment_info': False,
        'include_test_details': True
    },
    'detailed': {
        'title': 'Detailed Test Evidence',
        'theme': 'detailed',
        'include_timestamp': True,
        'include_environment_info': True,
        'include_test_details': True,
        'include_system_info': True
    }
}

# ========================================
# CONFIGURAÇÕES DE PERFORMANCE
# ========================================

PERFORMANCE_CONFIG = {
    'max_concurrent_screenshots': 3,
    'screenshot_timeout': 30,
    'processing_timeout': 300,
    'memory_limit_mb': 512,
    'enable_caching': True,
    'cache_ttl_seconds': 3600
}

# ========================================
# CONFIGURAÇÕES DE SEGURANÇA
# ========================================

SECURITY_CONFIG = {
    'allowed_file_extensions': ['.html', '.htm'],
    'max_file_size_bytes': 10 * 1024 * 1024,  # 10MB
    'sanitize_html': True,
    'validate_file_content': True,
    'block_executable_files': True,
    'log_security_events': True
}

# ========================================
# CONFIGURAÇÕES DE BACKUP
# ========================================

BACKUP_CONFIG = {
    'enable_backup': True,
    'backup_original_files': True,
    'backup_processed_files': True,
    'backup_retention_days': 30,
    'backup_compression': True,
    'backup_encryption': False
}

# ========================================
# FUNÇÕES DE CONFIGURAÇÃO
# ========================================

def get_config() -> Dict[str, Any]:
    """Retorna todas as configurações como um dicionário"""
    return {
        'processing': PROCESSING_CONFIG,
        'screenshot': SCREENSHOT_CONFIG,
        'validation': LOG_VALIDATION_CONFIG,
        'code_extraction': CODE_EXTRACTION_CONFIG,
        'jira': JIRA_CONFIG,
        'logging': LOGGING_CONFIG,
        'notifications': NOTIFICATION_CONFIG,
        'templates': SCREENSHOT_TEMPLATES,
        'performance': PERFORMANCE_CONFIG,
        'security': SECURITY_CONFIG,
        'backup': BACKUP_CONFIG
    }

def validate_config() -> List[str]:
    """Valida as configurações e retorna lista de erros"""
    errors = []
    
    # Validar tamanhos de arquivo
    if PROCESSING_CONFIG['max_file_size_mb'] <= 0:
        errors.append("max_file_size_mb deve ser maior que 0")
    
    if SECURITY_CONFIG['max_file_size_bytes'] <= 0:
        errors.append("max_file_size_bytes deve ser maior que 0")
    
    # Validar timeouts
    if SCREENSHOT_CONFIG['selenium_timeout'] <= 0:
        errors.append("selenium_timeout deve ser maior que 0")
    
    if PERFORMANCE_CONFIG['screenshot_timeout'] <= 0:
        errors.append("screenshot_timeout deve ser maior que 0")
    
    # Validar padrões de código
    if not CODE_EXTRACTION_CONFIG['patterns']:
        errors.append("Pelo menos um padrão de extração deve ser definido")
    
    # Validar configurações de Jira
    if JIRA_CONFIG['max_attachment_size_mb'] <= 0:
        errors.append("max_attachment_size_mb deve ser maior que 0")
    
    return errors

def get_environment_config() -> Dict[str, Any]:
    """Obtém configurações baseadas em variáveis de ambiente"""
    config = {}
    
    # Screenshots reais
    config['enable_real_screenshots'] = os.getenv('CAPTURE_REAL_SCREENSHOTS', 'false').lower() == 'true'
    
    # Configurações do Jira
    config['jira_url'] = os.getenv('JIRA_URL')
    config['jira_email'] = os.getenv('JIRA_EMAIL')
    config['jira_token'] = os.getenv('JIRA_API_TOKEN')
    
    # Configurações de debug
    config['debug_mode'] = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    config['log_level'] = os.getenv('LOG_LEVEL', 'INFO')
    
    # Configurações de performance
    config['max_concurrent'] = int(os.getenv('MAX_CONCURRENT_SCREENSHOTS', '3'))
    config['timeout'] = int(os.getenv('SCREENSHOT_TIMEOUT', '30'))
    
    return config

def update_config_from_env():
    """Atualiza configurações baseadas em variáveis de ambiente"""
    env_config = get_environment_config()
    
    # Atualizar configurações de screenshot
    SCREENSHOT_CONFIG['enable_real_screenshots'] = env_config['enable_real_screenshots']
    
    # Atualizar configurações de logging
    LOGGING_CONFIG['level'] = env_config['log_level']
    
    # Atualizar configurações de performance
    PERFORMANCE_CONFIG['max_concurrent_screenshots'] = env_config['max_concurrent']
    PERFORMANCE_CONFIG['screenshot_timeout'] = env_config['timeout']

# ========================================
# CONSTANTES
# ========================================

# Status de processamento
PROCESSING_STATUS = {
    'PENDING': 'pending',
    'PROCESSING': 'processing',
    'COMPLETED': 'completed',
    'FAILED': 'failed',
    'CANCELLED': 'cancelled'
}

# Tipos de evidência
EVIDENCE_TYPES = {
    'SUCCESS': 'success',
    'FAILURE': 'failure',
    'WARNING': 'warning',
    'INFO': 'info'
}

# Frameworks suportados
SUPPORTED_FRAMEWORKS = [
    'robot_framework',
    'selenium',
    'junit',
    'testng',
    'cucumber',
    'pytest',
    'jest',
    'mocha'
]

# Formatos de saída
OUTPUT_FORMATS = {
    'PNG': 'png',
    'JPG': 'jpg',
    'JPEG': 'jpeg',
    'GIF': 'gif',
    'TXT': 'txt'
}

# ========================================
# CONFIGURAÇÃO DO LOGGER
# ========================================

import logging
import logging.handlers
from datetime import datetime
import os

def setup_logger():
    """Configura o logger global do sistema"""
    # Criar diretório de logs se não existir
    log_dir = PROCESSING_CONFIG['log_dir']
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Nome do arquivo de log com data
    log_filename = f"evidencias_{datetime.now().strftime('%Y%m%d')}.log"
    log_path = os.path.join(log_dir, log_filename)
    
    # Configurar logger
    logger = logging.getLogger('evidencias_system')
    logger.setLevel(getattr(logging, LOGGING_CONFIG['level']))
    
    # Limpar handlers existentes
    logger.handlers.clear()
    
    # Handler para arquivo
    if LOGGING_CONFIG['log_to_file']:
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=LOGGING_CONFIG['max_log_files']
        )
        file_handler.setLevel(getattr(logging, LOGGING_CONFIG['level']))
        file_formatter = logging.Formatter(LOGGING_CONFIG['format'])
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Handler para console
    if LOGGING_CONFIG['log_to_console']:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, LOGGING_CONFIG['level']))
        console_formatter = logging.Formatter(LOGGING_CONFIG['format'])
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger

# ========================================
# INICIALIZAÇÃO
# ========================================

# Atualizar configurações com variáveis de ambiente
update_config_from_env()

# Configurar logger global
logger = setup_logger()

# Validar configurações
config_errors = validate_config()
if config_errors:
    logger.warning("⚠️  Avisos de configuração:")
    for error in config_errors:
        logger.warning(f"   - {error}")
else:
    logger.info("✅ Configurações validadas com sucesso")
