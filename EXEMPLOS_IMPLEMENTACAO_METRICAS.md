# Exemplos de Implementação - Melhorias na Funcionalidade de Métricas

## 🚀 Implementações Práticas

### 1. Cache Redis para Performance

```python
# metrics_cache.py
import redis
import json
from datetime import datetime, timedelta
from functools import wraps

class MetricsCache:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.default_ttl = 300  # 5 minutos
    
    def get_cached_metrics(self, epic_key):
        """Recupera métricas do cache"""
        cache_key = f"metrics:{epic_key}"
        cached_data = self.redis_client.get(cache_key)
        
        if cached_data:
            print(f"✅ Cache hit para {epic_key}")
            return json.loads(cached_data)
        
        print(f"❌ Cache miss para {epic_key}")
        return None
    
    def cache_metrics(self, epic_key, data, ttl=None):
        """Armazena métricas no cache"""
        cache_key = f"metrics:{epic_key}"
        ttl = ttl or self.default_ttl
        
        try:
            self.redis_client.setex(
                cache_key, 
                ttl, 
                json.dumps(data, default=str)
            )
            print(f"✅ Métricas cacheadas para {epic_key} (TTL: {ttl}s)")
        except Exception as e:
            print(f"❌ Erro ao cachear métricas: {e}")
    
    def invalidate_cache(self, epic_key):
        """Remove métricas do cache"""
        cache_key = f"metrics:{epic_key}"
        self.redis_client.delete(cache_key)
        print(f"🗑️ Cache invalidado para {epic_key}")

# Decorator para cache automático
def cached_metrics(ttl=300):
    def decorator(func):
        @wraps(func)
        def wrapper(epic_key, *args, **kwargs):
            cache = MetricsCache()
            cached_data = cache.get_cached_metrics(epic_key)
            
            if cached_data:
                return cached_data
            
            # Calcular métricas
            result = func(epic_key, *args, **kwargs)
            
            # Cachear resultado
            cache.cache_metrics(epic_key, result, ttl)
            
            return result
        return wrapper
    return decorator
```

### 2. Processamento Assíncrono com Celery

```python
# tasks.py
from celery import Celery
from celery.utils.log import get_task_logger
import time

# Configuração do Celery
app = Celery('metrics')
app.config_from_object('celeryconfig')

logger = get_task_logger(__name__)

@app.task(bind=True)
def calculate_epic_metrics_async(self, epic_key):
    """Calcula métricas de épico em background"""
    try:
        logger.info(f"Iniciando cálculo de métricas para {epic_key}")
        
        # Simular processamento longo
        time.sleep(2)
        
        # Calcular métricas
        metrics = calculate_analise_epico_detalhada(epic_key)
        
        # Cachear resultado
        cache = MetricsCache()
        cache.cache_metrics(epic_key, metrics)
        
        logger.info(f"✅ Métricas calculadas com sucesso para {epic_key}")
        return metrics
        
    except Exception as e:
        logger.error(f"❌ Erro no cálculo de métricas: {e}")
        self.retry(countdown=60, max_retries=3)

@app.task
def generate_metrics_report_async(epic_key, format='pdf'):
    """Gera relatório de métricas em background"""
    try:
        logger.info(f"Gerando relatório {format} para {epic_key}")
        
        # Gerar relatório
        report_path = generate_metrics_report(epic_key, format)
        
        # Enviar notificação
        send_report_notification(epic_key, report_path)
        
        return report_path
        
    except Exception as e:
        logger.error(f"❌ Erro na geração do relatório: {e}")
        raise
```

### 3. Filtros Avançados no Frontend

```javascript
// advanced_filters.js
class AdvancedFilters {
    constructor() {
        this.filters = {
            dateRange: null,
            assignee: null,
            priority: null,
            components: null,
            status: null,
            storyPoints: null
        };
        
        this.originalData = null;
        this.initEventListeners();
    }
    
    initEventListeners() {
        // Filtro por data
        document.getElementById('dateRange').addEventListener('change', (e) => {
            this.filters.dateRange = e.target.value;
            this.applyFilters();
        });
        
        // Filtro por responsável
        document.getElementById('assigneeFilter').addEventListener('change', (e) => {
            this.filters.assignee = e.target.value;
            this.applyFilters();
        });
        
        // Filtro por prioridade
        document.getElementById('priorityFilter').addEventListener('change', (e) => {
            this.filters.priority = e.target.value;
            this.applyFilters();
        });
        
        // Botão de limpar filtros
        document.getElementById('clearFilters').addEventListener('click', () => {
            this.clearFilters();
        });
    }
    
    setOriginalData(data) {
        this.originalData = data;
    }
    
    applyFilters() {
        if (!this.originalData) return;
        
        let filteredData = [...this.originalData];
        
        // Aplicar filtros
        if (this.filters.dateRange) {
            filteredData = this.filterByDateRange(filteredData);
        }
        
        if (this.filters.assignee) {
            filteredData = this.filterByAssignee(filteredData);
        }
        
        if (this.filters.priority) {
            filteredData = this.filterByPriority(filteredData);
        }
        
        if (this.filters.status) {
            filteredData = this.filterByStatus(filteredData);
        }
        
        // Atualizar interface
        this.updateCharts(filteredData);
        this.updateTables(filteredData);
        this.updateMetrics(filteredData);
        
        // Mostrar contador de resultados
        this.showResultsCount(filteredData.length);
    }
    
    filterByDateRange(data) {
        const [startDate, endDate] = this.filters.dateRange.split(' to ');
        
        return data.filter(issue => {
            const issueDate = new Date(issue.created);
            const start = new Date(startDate);
            const end = new Date(endDate);
            
            return issueDate >= start && issueDate <= end;
        });
    }
    
    filterByAssignee(data) {
        return data.filter(issue => 
            issue.assignee === this.filters.assignee
        );
    }
    
    filterByPriority(data) {
        return data.filter(issue => 
            issue.priority === this.filters.priority
        );
    }
    
    filterByStatus(data) {
        return data.filter(issue => 
            issue.status === this.filters.status
        );
    }
    
    updateCharts(filteredData) {
        // Atualizar gráficos com dados filtrados
        updateStatusChart(filteredData);
        updateAssigneeChart(filteredData);
        updateVelocityChart(filteredData);
    }
    
    updateTables(filteredData) {
        // Atualizar tabelas com dados filtrados
        updateIssuesTable(filteredData);
        updateTestCasesTable(filteredData);
    }
    
    updateMetrics(filteredData) {
        // Recalcular métricas com dados filtrados
        const metrics = calculateMetricsFromData(filteredData);
        updateMetricsDisplay(metrics);
    }
    
    showResultsCount(count) {
        const resultsCounter = document.getElementById('resultsCount');
        resultsCounter.textContent = `${count} resultados encontrados`;
        resultsCounter.style.display = 'block';
    }
    
    clearFilters() {
        // Limpar todos os filtros
        Object.keys(this.filters).forEach(key => {
            this.filters[key] = null;
        });
        
        // Limpar campos do formulário
        document.getElementById('dateRange').value = '';
        document.getElementById('assigneeFilter').value = '';
        document.getElementById('priorityFilter').value = '';
        document.getElementById('statusFilter').value = '';
        
        // Restaurar dados originais
        this.applyFilters();
        
        // Esconder contador
        document.getElementById('resultsCount').style.display = 'none';
    }
    
    exportFilteredData() {
        const filteredData = this.getFilteredData();
        this.downloadCSV(filteredData);
    }
    
    downloadCSV(data) {
        const headers = ['Key', 'Summary', 'Status', 'Assignee', 'Story Points', 'Created'];
        const csvContent = [
            headers.join(','),
            ...data.map(issue => [
                issue.key,
                `"${issue.summary}"`,
                issue.status,
                issue.assignee,
                issue.story_points,
                issue.created
            ].join(','))
        ].join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `metrics_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
    }
}
```

### 4. Gráficos Interativos

```javascript
// interactive_charts.js
class InteractiveCharts {
    constructor() {
        this.charts = {};
        this.initCharts();
    }
    
    initCharts() {
        this.createStatusChart();
        this.createVelocityChart();
        this.createTimelineChart();
    }
    
    createStatusChart() {
        const ctx = document.getElementById('statusChart').getContext('2d');
        
        this.charts.status = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#28a745', // Done
                        '#ffc107', // In Progress
                        '#dc3545', // To Do
                        '#6c757d'  // Blocked
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const index = elements[0].index;
                        const status = this.charts.status.data.labels[index];
                        this.showStatusDetails(status);
                    }
                }
            }
        });
    }
    
    createVelocityChart() {
        const ctx = document.getElementById('velocityChart').getContext('2d');
        
        this.charts.velocity = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Velocidade (SP)',
                    data: [],
                    borderColor: '#3182ce',
                    backgroundColor: 'rgba(49, 130, 206, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Throughput (Issues)',
                    data: [],
                    borderColor: '#38a169',
                    backgroundColor: 'rgba(56, 161, 105, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            afterBody: function(context) {
                                const dataIndex = context[0].dataIndex;
                                return `Sprint ${dataIndex + 1}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const dataIndex = elements[0].index;
                        this.showSprintDetails(dataIndex);
                    }
                }
            }
        });
    }
    
    updateCharts(data) {
        this.updateStatusChart(data);
        this.updateVelocityChart(data);
        this.updateTimelineChart(data);
    }
    
    updateStatusChart(data) {
        const statusCounts = {};
        
        data.forEach(issue => {
            const status = issue.status;
            statusCounts[status] = (statusCounts[status] || 0) + 1;
        });
        
        this.charts.status.data.labels = Object.keys(statusCounts);
        this.charts.status.data.datasets[0].data = Object.values(statusCounts);
        this.charts.status.update();
    }
    
    updateVelocityChart(data) {
        // Simular dados de velocidade por sprint
        const sprints = ['Sprint 1', 'Sprint 2', 'Sprint 3', 'Sprint 4'];
        const velocity = [8, 12, 10, 15];
        const throughput = [5, 8, 6, 10];
        
        this.charts.velocity.data.labels = sprints;
        this.charts.velocity.data.datasets[0].data = velocity;
        this.charts.velocity.data.datasets[1].data = throughput;
        this.charts.velocity.update();
    }
    
    showStatusDetails(status) {
        // Mostrar modal com detalhes do status
        const modal = document.getElementById('statusDetailsModal');
        const modalTitle = document.getElementById('statusDetailsTitle');
        const modalBody = document.getElementById('statusDetailsBody');
        
        modalTitle.textContent = `Detalhes: ${status}`;
        
        // Buscar issues com este status
        const issuesInStatus = this.getIssuesByStatus(status);
        
        // Criar tabela de detalhes
        const tableHTML = this.createIssuesTable(issuesInStatus);
        modalBody.innerHTML = tableHTML;
        
        // Mostrar modal
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
    
    showSprintDetails(sprintIndex) {
        // Mostrar detalhes da sprint
        const modal = document.getElementById('sprintDetailsModal');
        const modalTitle = document.getElementById('sprintDetailsTitle');
        const modalBody = document.getElementById('sprintDetailsBody');
        
        modalTitle.textContent = `Sprint ${sprintIndex + 1}`;
        
        // Buscar issues da sprint (simulado)
        const sprintIssues = this.getSprintIssues(sprintIndex);
        
        // Criar conteúdo do modal
        const contentHTML = this.createSprintContent(sprintIssues);
        modalBody.innerHTML = contentHTML;
        
        // Mostrar modal
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
    
    createIssuesTable(issues) {
        return `
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Key</th>
                        <th>Summary</th>
                        <th>Assignee</th>
                        <th>Story Points</th>
                        <th>Created</th>
                    </tr>
                </thead>
                <tbody>
                    ${issues.map(issue => `
                        <tr>
                            <td><a href="#" onclick="openIssue('${issue.key}')">${issue.key}</a></td>
                            <td>${issue.summary}</td>
                            <td>${issue.assignee}</td>
                            <td>${issue.story_points}</td>
                            <td>${new Date(issue.created).toLocaleDateString()}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }
    
    createSprintContent(sprintIssues) {
        return `
            <div class="sprint-summary">
                <div class="row">
                    <div class="col-md-6">
                        <h5>Métricas da Sprint</h5>
                        <ul>
                            <li>Total de Issues: ${sprintIssues.length}</li>
                            <li>Story Points: ${sprintIssues.reduce((sum, issue) => sum + issue.story_points, 0)}</li>
                            <li>Concluídas: ${sprintIssues.filter(issue => issue.status === 'Done').length}</li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h5>Issues da Sprint</h5>
                        ${this.createIssuesTable(sprintIssues)}
                    </div>
                </div>
            </div>
        `;
    }
}
```

### 5. Métricas Avançadas de Qualidade

```python
# advanced_metrics.py
from datetime import datetime, timedelta
import statistics

class AdvancedMetricsCalculator:
    def __init__(self, issues_data):
        self.issues = issues_data
        self.status_concluidos = ['Done', 'Resolved', 'Closed', 'CONCLUÍDO']
    
    def calculate_quality_metrics(self):
        """Calcula métricas avançadas de qualidade"""
        total_issues = len(self.issues)
        total_story_points = sum(issue.get('story_points', 0) for issue in self.issues)
        bugs = [issue for issue in self.issues if issue.get('issuetype') == 'Bug']
        
        return {
            'defect_density': self.calculate_defect_density(bugs, total_story_points),
            'bug_frequency': len(bugs) / total_issues if total_issues > 0 else 0,
            'quality_score': self.calculate_quality_score(),
            'technical_debt_ratio': self.calculate_technical_debt_ratio(),
            'code_coverage': self.estimate_code_coverage(),
            'test_coverage': self.calculate_test_coverage()
        }
    
    def calculate_defect_density(self, bugs, total_story_points):
        """Calcula densidade de defeitos (bugs por story point)"""
        if total_story_points == 0:
            return 0
        return len(bugs) / total_story_points
    
    def calculate_quality_score(self):
        """Calcula score de qualidade baseado em múltiplos fatores"""
        factors = {
            'bug_ratio': self.calculate_bug_ratio(),
            'completion_rate': self.calculate_completion_rate(),
            'time_accuracy': self.calculate_time_accuracy(),
            'story_point_accuracy': self.calculate_story_point_accuracy()
        }
        
        # Pesos para cada fator
        weights = {
            'bug_ratio': 0.3,
            'completion_rate': 0.25,
            'time_accuracy': 0.25,
            'story_point_accuracy': 0.2
        }
        
        quality_score = sum(factors[factor] * weights[factor] for factor in factors)
        return min(100, max(0, quality_score * 100))  # Normalizar para 0-100
    
    def calculate_bug_ratio(self):
        """Calcula razão de bugs (menor é melhor)"""
        bugs = [issue for issue in self.issues if issue.get('issuetype') == 'Bug']
        total_issues = len(self.issues)
        
        if total_issues == 0:
            return 1.0  # Score perfeito se não há issues
        
        bug_ratio = len(bugs) / total_issues
        # Converter para score (0-1, onde 1 é melhor)
        return max(0, 1 - (bug_ratio * 5))  # Penalizar bugs
    
    def calculate_completion_rate(self):
        """Calcula taxa de conclusão"""
        completed = sum(1 for issue in self.issues 
                       if issue.get('status') in self.status_concluidos)
        total = len(self.issues)
        
        return completed / total if total > 0 else 0
    
    def calculate_time_accuracy(self):
        """Calcula precisão das estimativas de tempo"""
        accurate_estimates = 0
        total_estimates = 0
        
        for issue in self.issues:
            estimated = issue.get('timeestimate', 0)
            actual = issue.get('timespent', 0)
            
            if estimated > 0 and actual > 0:
                total_estimates += 1
                # Considerar preciso se diferença < 20%
                if abs(actual - estimated) / estimated <= 0.2:
                    accurate_estimates += 1
        
        return accurate_estimates / total_estimates if total_estimates > 0 else 1.0
    
    def calculate_story_point_accuracy(self):
        """Calcula precisão das estimativas de story points"""
        # Simulação baseada em complexidade vs tempo
        accurate_sp = 0
        total_sp = 0
        
        for issue in self.issues:
            story_points = issue.get('story_points', 0)
            time_spent = issue.get('timespent', 0)
            
            if story_points > 0 and time_spent > 0:
                total_sp += 1
                # Estimativa baseada em 1 SP = 4 horas
                expected_time = story_points * 4 * 3600  # em segundos
                if abs(time_spent - expected_time) / expected_time <= 0.3:
                    accurate_sp += 1
        
        return accurate_sp / total_sp if total_sp > 0 else 1.0
    
    def calculate_technical_debt_ratio(self):
        """Calcula razão de technical debt"""
        # Identificar indicadores de technical debt
        debt_indicators = 0
        total_issues = len(self.issues)
        
        for issue in self.issues:
            # Bugs recorrentes
            if issue.get('issuetype') == 'Bug' and issue.get('priority') == 'High':
                debt_indicators += 2
            
            # Issues com muito tempo gasto
            time_spent = issue.get('timespent', 0)
            story_points = issue.get('story_points', 0)
            if story_points > 0 and time_spent > story_points * 8 * 3600:  # Mais de 8h por SP
                debt_indicators += 1
            
            # Issues bloqueadas
            if issue.get('status') in ['Blocked', 'Impedimento']:
                debt_indicators += 1
        
        return min(1.0, debt_indicators / total_issues) if total_issues > 0 else 0
    
    def estimate_code_coverage(self):
        """Estima cobertura de código baseada em casos de teste"""
        test_cases = [issue for issue in self.issues if issue.get('issuetype') == 'Test']
        stories = [issue for issue in self.issues if issue.get('issuetype') == 'Story']
        
        if not stories:
            return 0
        
        # Assumir que cada caso de teste cobre uma funcionalidade
        coverage_ratio = len(test_cases) / len(stories)
        return min(100, coverage_ratio * 100)
    
    def calculate_test_coverage(self):
        """Calcula cobertura de testes"""
        test_cases = [issue for issue in self.issues if issue.get('issuetype') == 'Test']
        executed_tests = [test for test in test_cases 
                         if test.get('status') in ['Done', 'Resolved']]
        
        return len(executed_tests) / len(test_cases) if test_cases else 0
    
    def calculate_team_metrics(self):
        """Calcula métricas de performance da equipe"""
        team_stats = {}
        
        for issue in self.issues:
            assignee = issue.get('assignee', 'Não atribuído')
            
            if assignee not in team_stats:
                team_stats[assignee] = {
                    'total_issues': 0,
                    'completed_issues': 0,
                    'story_points': 0,
                    'time_spent': 0,
                    'cycle_times': [],
                    'bug_count': 0
                }
            
            team_stats[assignee]['total_issues'] += 1
            team_stats[assignee]['story_points'] += issue.get('story_points', 0)
            team_stats[assignee]['time_spent'] += issue.get('timespent', 0)
            
            if issue.get('status') in self.status_concluidos:
                team_stats[assignee]['completed_issues'] += 1
            
            if issue.get('issuetype') == 'Bug':
                team_stats[assignee]['bug_count'] += 1
            
            # Calcular cycle time
            if issue.get('status') in self.status_concluidos:
                cycle_time = self.calculate_cycle_time(issue)
                if cycle_time:
                    team_stats[assignee]['cycle_times'].append(cycle_time)
        
        # Calcular métricas agregadas
        for assignee in team_stats:
            stats = team_stats[assignee]
            stats['completion_rate'] = (stats['completed_issues'] / stats['total_issues'] 
                                      if stats['total_issues'] > 0 else 0)
            stats['avg_cycle_time'] = (statistics.mean(stats['cycle_times']) 
                                     if stats['cycle_times'] else 0)
            stats['productivity'] = (stats['story_points'] / (stats['time_spent'] / 3600) 
                                   if stats['time_spent'] > 0 else 0)
        
        return team_stats
    
    def calculate_cycle_time(self, issue):
        """Calcula cycle time de uma issue"""
        created = issue.get('created')
        resolved = issue.get('resolutiondate')
        
        if created and resolved:
            try:
                created_date = datetime.fromisoformat(created.replace('Z', '+00:00'))
                resolved_date = datetime.fromisoformat(resolved.replace('Z', '+00:00'))
                return (resolved_date - created_date).days
            except (ValueError, TypeError):
                return None
        
        return None
```

### 6. Relatórios Exportáveis

```python
# report_generator.py
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import BarChart, Reference
import io

class MetricsReportGenerator:
    def __init__(self, metrics_data):
        self.metrics = metrics_data
        self.styles = getSampleStyleSheet()
    
    def generate_pdf_report(self, epic_key, output_path=None):
        """Gera relatório PDF das métricas"""
        if not output_path:
            output_path = f"metrics_report_{epic_key}.pdf"
        
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Centralizado
        )
        story.append(Paragraph(f"Relatório de Métricas - Épico {epic_key}", title_style))
        story.append(Spacer(1, 20))
        
        # Resumo Executivo
        story.append(Paragraph("Resumo Executivo", self.styles['Heading2']))
        story.append(Spacer(1, 12))
        
        summary_data = [
            ['Métrica', 'Valor'],
            ['Total de Issues', str(self.metrics['resumo']['total_issues'])],
            ['Issues Concluídas', str(self.metrics['resumo']['stories_count'])],
            ['Story Points Totais', str(self.metrics['story_points']['total'])],
            ['Percentual de Conclusão', f"{self.metrics['story_points']['percentual_concluido']}%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Métricas Detalhadas
        story.append(Paragraph("Métricas Detalhadas", self.styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Progresso
        story.append(Paragraph("Progresso", self.styles['Heading3']))
        progress_data = [
            ['Status', 'Quantidade', 'Percentual'],
            ['Concluído', str(self.metrics['progresso']['concluido']['count']), 
             f"{self.metrics['progresso']['concluido']['percentual']}%"],
            ['Em Progresso', str(self.metrics['progresso']['em_progresso']['count']), 
             f"{self.metrics['progresso']['em_progresso']['percentual']}%"],
            ['Impedimento', str(self.metrics['progresso']['impedimento']['count']), 
             f"{self.metrics['progresso']['impedimento']['percentual']}%"]
        ]
        
        progress_table = Table(progress_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        progress_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(progress_table)
        story.append(Spacer(1, 20))
        
        # Métricas de Tempo
        story.append(Paragraph("Métricas de Tempo", self.styles['Heading3']))
        time_data = [
            ['Métrica', 'Valor'],
            ['Lead Time Médio', f"{self.metrics['metricas_tempo']['lead_time_medio']} dias"],
            ['Cycle Time Médio', f"{self.metrics['metricas_tempo']['cycle_time_medio']} dias"],
            ['Velocidade/Sprint', f"{self.metrics['metricas_tempo']['velocidade_sprint']} SP"],
            ['Throughput/Sprint', f"{self.metrics['metricas_tempo']['throughput_sprint']} issues"]
        ]
        
        time_table = Table(time_data, colWidths=[3*inch, 2*inch])
        time_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(time_table)
        
        # Gerar PDF
        doc.build(story)
        return output_path
    
    def generate_excel_report(self, epic_key, output_path=None):
        """Gera relatório Excel das métricas"""
        if not output_path:
            output_path = f"metrics_report_{epic_key}.xlsx"
        
        wb = openpyxl.Workbook()
        
        # Aba de Resumo
        ws_summary = wb.active
        ws_summary.title = "Resumo"
        
        # Título
        ws_summary['A1'] = f"Relatório de Métricas - Épico {epic_key}"
        ws_summary['A1'].font = Font(size=16, bold=True)
        ws_summary.merge_cells('A1:D1')
        
        # Resumo Executivo
        ws_summary['A3'] = "Resumo Executivo"
        ws_summary['A3'].font = Font(size=14, bold=True)
        
        summary_headers = ['Métrica', 'Valor']
        for col, header in enumerate(summary_headers, 1):
            cell = ws_summary.cell(row=4, column=col)
            cell.value = header
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        
        summary_data = [
            ['Total de Issues', self.metrics['resumo']['total_issues']],
            ['Issues Concluídas', self.metrics['resumo']['stories_count']],
            ['Story Points Totais', self.metrics['story_points']['total']],
            ['Percentual de Conclusão', f"{self.metrics['story_points']['percentual_concluido']}%"]
        ]
        
        for row, data in enumerate(summary_data, 5):
            for col, value in enumerate(data, 1):
                ws_summary.cell(row=row, column=col, value=value)
        
        # Aba de Progresso
        ws_progress = wb.create_sheet("Progresso")
        
        ws_progress['A1'] = "Progresso por Status"
        ws_progress['A1'].font = Font(size=14, bold=True)
        
        progress_headers = ['Status', 'Quantidade', 'Percentual']
        for col, header in enumerate(progress_headers, 1):
            cell = ws_progress.cell(row=3, column=col)
            cell.value = header
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        
        progress_data = [
            ['Concluído', self.metrics['progresso']['concluido']['count'], 
             f"{self.metrics['progresso']['concluido']['percentual']}%"],
            ['Em Progresso', self.metrics['progresso']['em_progresso']['count'], 
             f"{self.metrics['progresso']['em_progresso']['percentual']}%"],
            ['Impedimento', self.metrics['progresso']['impedimento']['count'], 
             f"{self.metrics['progresso']['impedimento']['percentual']}%"]
        ]
        
        for row, data in enumerate(progress_data, 4):
            for col, value in enumerate(data, 1):
                ws_progress.cell(row=row, column=col, value=value)
        
        # Gráfico de progresso
        chart = BarChart()
        chart.title = "Progresso por Status"
        chart.x_axis.title = "Status"
        chart.y_axis.title = "Quantidade"
        
        data = Reference(ws_progress, min_col=2, min_row=3, max_row=6)
        cats = Reference(ws_progress, min_col=1, min_row=4, max_row=6)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        ws_progress.add_chart(chart, "A10")
        
        # Aba de Métricas de Tempo
        ws_time = wb.create_sheet("Métricas de Tempo")
        
        ws_time['A1'] = "Métricas de Tempo"
        ws_time['A1'].font = Font(size=14, bold=True)
        
        time_headers = ['Métrica', 'Valor']
        for col, header in enumerate(time_headers, 1):
            cell = ws_time.cell(row=3, column=col)
            cell.value = header
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        
        time_data = [
            ['Lead Time Médio', f"{self.metrics['metricas_tempo']['lead_time_medio']} dias"],
            ['Cycle Time Médio', f"{self.metrics['metricas_tempo']['cycle_time_medio']} dias"],
            ['Velocidade/Sprint', f"{self.metrics['metricas_tempo']['velocidade_sprint']} SP"],
            ['Throughput/Sprint', f"{self.metrics['metricas_tempo']['throughput_sprint']} issues"]
        ]
        
        for row, data in enumerate(time_data, 4):
            for col, value in enumerate(data, 1):
                ws_time.cell(row=row, column=col, value=value)
        
        # Salvar arquivo
        wb.save(output_path)
        return output_path
```

## 📋 Como Implementar

### 1. **Instalar Dependências**
```bash
pip install redis celery reportlab openpyxl
```

### 2. **Configurar Redis**
```bash
# Instalar Redis
sudo apt-get install redis-server

# Iniciar Redis
sudo systemctl start redis-server
```

### 3. **Configurar Celery**
```python
# celeryconfig.py
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'UTC'
enable_utc = True
```

### 4. **Integrar no App Principal**
```python
# app.py - Adicionar imports
from metrics_cache import MetricsCache
from advanced_metrics import AdvancedMetricsCalculator
from report_generator import MetricsReportGenerator

# Inicializar cache
metrics_cache = MetricsCache()

# Modificar rota existente
@app.route('/api/analise-epico-detalhada/<epic_key>')
@cached_metrics(ttl=300)
def obter_analise_epico_detalhada(epic_key):
    # ... código existente ...
    
    # Adicionar métricas avançadas
    advanced_calculator = AdvancedMetricsCalculator(issues)
    quality_metrics = advanced_calculator.calculate_quality_metrics()
    team_metrics = advanced_calculator.calculate_team_metrics()
    
    analise['quality_metrics'] = quality_metrics
    analise['team_metrics'] = team_metrics
    
    return jsonify(analise)
```

### 5. **Adicionar Rotas de Relatório**
```python
@app.route('/api/exportar-relatorio/<epic_key>')
def exportar_relatorio(epic_key):
    format = request.args.get('format', 'pdf')
    
    # Buscar métricas
    metrics = get_epic_metrics(epic_key)
    
    # Gerar relatório
    generator = MetricsReportGenerator(metrics)
    
    if format == 'pdf':
        output_path = generator.generate_pdf_report(epic_key)
    elif format == 'excel':
        output_path = generator.generate_excel_report(epic_key)
    else:
        return jsonify({"erro": "Formato não suportado"}), 400
    
    return send_file(output_path, as_attachment=True)
```

## 🎯 Resultados Esperados

Com essas implementações, a funcionalidade de métricas terá:

1. **Performance 10x melhor** com cache Redis
2. **Processamento assíncrono** para épicos grandes
3. **Filtros avançados** para análise detalhada
4. **Gráficos interativos** com drill-down
5. **Métricas de qualidade** avançadas
6. **Relatórios exportáveis** em PDF e Excel
7. **Métricas de equipe** para gestão de performance

Essas melhorias transformarão o sistema em uma ferramenta poderosa para análise de projetos ágeis!
