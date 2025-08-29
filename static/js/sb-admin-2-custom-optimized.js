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
            if ($(window).width() < 768) {
                if (!$(e.target).closest('.sidebar, #sidebarToggle, #sidebarToggleTop').length) {
                    $('body').removeClass('sidebar-toggled');
                    $('.sidebar').removeClass('toggled');
                }
            }
        });
        
        // Verificar elementos encontrados
        var toggleButtons = {
            'bottom': $('#sidebarToggle').length,
            'top': $('#sidebarToggleTop').length
        };
    }
    
    // Dropdown functionality - Versão Otimizada
    function initDropdowns() {
        
        // Usar Bootstrap dropdown se disponível
        if (typeof bootstrap !== 'undefined' && bootstrap.Dropdown) {
            $('.dropdown-toggle').dropdown();
        }
        
        // Melhorar dropdowns de alertas e mensagens
        $('.dropdown-list .dropdown-item').on('click', function(e) {
            e.preventDefault();
            var text = $(this).find('.text-truncate').text() || $(this).text();
            
            // Aqui você pode adicionar lógica específica para cada tipo de dropdown
            if ($(this).closest('#alertsDropdown').length) {
                // Lógica para alertas
            } else if ($(this).closest('#messagesDropdown').length) {
                // Lógica para mensagens
            }
        });
    }
    
    // Topbar Search Functionality - Versão Otimizada

    
    // Notifications System - Versão Otimizada
    function initNotifications() {
        
        // Atualizar contadores de notificações
        function updateNotificationCounts() {
            // Simular contadores dinâmicos
            var alertCount = Math.floor(Math.random() * 5) + 1;
            var messageCount = Math.floor(Math.random() * 10) + 1;
            
            // Atualizar badges
            $('.badge-counter').each(function() {
                var $badge = $(this);
                if ($badge.closest('#alertsDropdown').length) {
                    $badge.text(alertCount + '+');
                } else if ($badge.closest('#messagesDropdown').length) {
                    $badge.text(messageCount);
                }
            });
        }
        
        // Atualizar contadores a cada 30 segundos
        updateNotificationCounts();
        setInterval(updateNotificationCounts, 30000);
        
        // Marcar notificações como lidas
        $('.dropdown-item').on('click', function() {
            var $badge = $(this).closest('.dropdown').find('.badge-counter');
            if ($badge.length) {
                $badge.text('0');
            }
        });
    }
    
    // Utilitários SB Admin 2
    window.SBAdmin2Utils = {
        showLoading: function(message) {
            // Implementar loading
            if (message) {
                // Mostrar mensagem de loading
            }
        },
        
        hideLoading: function() {
            // Esconder loading
        },
        
        showNotification: function(message, type) {
            // Implementar notificação
            if (type === 'warning') {
                // Mostrar warning
            }
        }
    };
    
    // Inicializar todas as funcionalidades
    highlightActivePage();
    initSidebarToggle();
    initDropdowns();
    
    initNotifications();
    
    // Adicionar classes CSS para melhorar a aparência
    $('body').addClass('sb-admin-2-loaded');
    
});
