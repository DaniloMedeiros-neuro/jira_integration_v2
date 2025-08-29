// SB Admin 2 Custom JavaScript - Versão Otimizada para Produção
$(document).ready(function() {
    
    // Highlight da página ativa no sidebar
    function highlightActivePage() {
        var currentPath = window.location.pathname;
        
        // Remover highlight anterior
        $('.sidebar .nav-item .nav-link').removeClass('active');
        
        // Adicionar highlight baseado na URL atual
        $('.sidebar .nav-item .nav-link').each(function() {
            var linkHref = $(this).attr('href');
            
            // Verificar se a URL atual corresponde ao link
            if (linkHref === currentPath) {
                $(this).addClass('active');
                return false; // Sair do loop
            }
            
            // Verificar URLs especiais
            if (currentPath === '/' && linkHref === '/') {
                $(this).addClass('active');
                return false;
            }
            
            // Verificar se é uma subpágina (mais específico)
            if (linkHref !== '/' && currentPath.startsWith(linkHref)) {
                $(this).addClass('active');
                return false;
            }
        });
    }
    
    // Sidebar Toggle Functionality - Versão Otimizada
    function initSidebarToggle() {
        
        // Função para toggle do sidebar
        function toggleSidebar() {
            // Toggle das classes
            $('body').toggleClass('sidebar-toggled');
            $('.sidebar').toggleClass('toggled');
            
            // Salvar estado no localStorage
            localStorage.setItem('sidebar-toggled', $('.sidebar').hasClass('toggled'));
        }
        
        // Remover eventos anteriores para evitar duplicação
        $(document).off('click', '#sidebarToggle');
        $(document).off('click', '#sidebarToggleTop');
        $('#sidebarToggle').off('click');
        $('#sidebarToggleTop').off('click');
        
        // Toggle do botão na parte inferior do sidebar
        $(document).on('click', '#sidebarToggle', function(e) {
            e.preventDefault();
            e.stopPropagation();
            toggleSidebar();
        });
        
        // Toggle do botão no topbar (mobile)
        $(document).on('click', '#sidebarToggleTop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            toggleSidebar();
        });
        
        // Restaurar estado do sidebar
        var sidebarToggled = localStorage.getItem('sidebar-toggled') === 'true';
        if (sidebarToggled) {
            $('body').addClass('sidebar-toggled');
            $('.sidebar').addClass('toggled');
        }
        
        // Fechar sidebar em mobile quando clicar fora
        $(document).on('click', function(e) {
            if ($(window).width() <= 768) {
                if (!$(e.target).closest('.sidebar, #sidebarToggleTop').length) {
                    if ($('.sidebar').hasClass('toggled')) {
                        $('body').removeClass('sidebar-toggled');
                        $('.sidebar').removeClass('toggled');
                        localStorage.setItem('sidebar-toggled', 'false');
                    }
                }
            }
        });
        
        // Verificar se os botões existem
        // Verificar elementos encontrados
        var toggleButtons = {
            'bottom': $('#sidebarToggle').length,
            'top': $('#sidebarToggleTop').length
        };
    }
    
    // Dropdown functionality - VERSÃO MELHORADA
    function initDropdowns() {
        console.log('Initializing dropdowns...');
        
        // Usar Bootstrap dropdown se disponível
        if (typeof bootstrap !== 'undefined' && bootstrap.Dropdown) {
            console.log('Bootstrap dropdown available, initializing...');
            $('.dropdown-toggle').dropdown();
        }
        
        // Melhorar dropdowns de alertas e mensagens
        $('.dropdown-list .dropdown-item').on('click', function(e) {
            e.preventDefault();
            var text = $(this).find('.text-truncate').text() || $(this).text();
            console.log('Dropdown item clicked:', text);
            
            // Aqui você pode adicionar lógica específica para cada tipo de dropdown
            if ($(this).closest('#alertsDropdown').length) {
                console.log('Alerta clicado:', text);
                // Lógica para alertas
            } else if ($(this).closest('#messagesDropdown').length) {
                console.log('Mensagem clicada:', text);
                // Lógica para mensagens
            }
        });
        
        // Verificar dropdowns
        console.log('Dropdowns found:', $('.dropdown').length);
    }
    

    
    // Notifications System - NOVA FUNCIONALIDADE
    function initNotifications() {
        console.log('Initializing notifications...');
        
        // Atualizar contadores de notificações
        function updateNotificationCounts() {
            // Simular contadores dinâmicos
            var alertCount = Math.floor(Math.random() * 5) + 1;
            var messageCount = Math.floor(Math.random() * 10) + 1;
            
            $('#alertsDropdown .badge-counter').text(alertCount + '+');
            $('#messagesDropdown .badge-counter').text(messageCount);
            
            console.log('Notification counts updated - Alerts:', alertCount, 'Messages:', messageCount);
        }
        
        // Atualizar contadores a cada 30 segundos
        setInterval(updateNotificationCounts, 30000);
        
        // Atualizar contadores iniciais
        updateNotificationCounts();
    }
    
    // Scroll to top functionality - VERSÃO SIMPLIFICADA
    function initScrollToTop() {
        $(window).scroll(function() {
            if ($(this).scrollTop() > 100) {
                $('.scroll-to-top').fadeIn();
            } else {
                $('.scroll-to-top').fadeOut();
            }
        });
        
        $('.scroll-to-top').on('click', function(e) {
            e.preventDefault();
            $('html, body').animate({scrollTop: 0}, 800);
        });
    }
    
    // Initialize all functions
    function init() {
        highlightActivePage();
        initSidebarToggle();
        initDropdowns();
        initNotifications(); // Adicionado
        initScrollToTop();
        
        // Log initialization
        console.log('SB Admin 2 Custom JS initialized successfully');
    }
    
    // Run initialization
    init();
    
    // Re-initialize on window resize
    $(window).on('resize', function() {
        // Re-highlight active page on resize
        highlightActivePage();
    });
    
    // Re-initialize on page load (for dynamic content)
    $(document).on('DOMContentLoaded', function() {
        highlightActivePage();
    });
    
    // Handle browser back/forward buttons
    $(window).on('popstate', function() {
        highlightActivePage();
    });
    
    // Custom event for page changes
    $(document).on('pageChanged', function() {
        highlightActivePage();
    });
});

// Utility functions - VERSÃO SIMPLIFICADA
window.SBAdmin2Utils = {
    // Show loading overlay
    showLoading: function(message = 'Carregando...') {
        if (!$('#loading-overlay').length) {
            $('body').append(`
                <div id="loading-overlay" class="position-fixed w-100 h-100 d-flex justify-content-center align-items-center" 
                     style="background: rgba(0,0,0,0.5); z-index: 9999; top: 0; left: 0;">
                    <div class="text-center text-white">
                        <div class="spinner-border mb-3" role="status">
                            <span class="sr-only">Carregando...</span>
                        </div>
                        <div>${message}</div>
                    </div>
                </div>
            `);
        }
    },
    
    // Hide loading overlay
    hideLoading: function() {
        $('#loading-overlay').fadeOut(300, function() {
            $(this).remove();
        });
    },
    
    // Show notification
    showNotification: function(message, type = 'info', duration = 3000) {
        var alertClass = 'alert-' + type;
        var icon = '';
        
        switch(type) {
            case 'success':
                icon = '<i class="fas fa-check-circle mr-2"></i>';
                break;
            case 'warning':
                icon = '<i class="fas fa-exclamation-triangle mr-2"></i>';
                break;
            case 'danger':
                icon = '<i class="fas fa-times-circle mr-2"></i>';
                break;
            default:
                icon = '<i class="fas fa-info-circle mr-2"></i>';
        }
        
        var notification = $(`
            <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
                 style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
                ${icon}${message}
                <button type="button" class="close" data-dismiss="alert">
                    <span>&times;</span>
                </button>
            </div>
        `);
        
        $('body').append(notification);
        
        setTimeout(function() {
            notification.fadeOut(300, function() {
                $(this).remove();
            });
        }, duration);
    },
    
    // Confirm dialog
    confirm: function(message, callback) {
        if (confirm(message)) {
            if (typeof callback === 'function') {
                callback();
            }
        }
    }
};
