// ==========================================
// Abinav Khadka Portfolio - Interactions
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // Smooth reveal animations on scroll
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const revealOnScroll = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                revealOnScroll.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Add reveal class to elements
    const revealElements = document.querySelectorAll(
        '.project-card, .highlight-card, .skill-category, .section-header'
    );

    revealElements.forEach(el => {
        el.classList.add('reveal');
        revealOnScroll.observe(el);
    });

    // Navbar background on scroll
    const nav = document.querySelector('.nav');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 100) {
            nav.classList.add('nav-scrolled');
        } else {
            nav.classList.remove('nav-scrolled');
        }
        
        lastScroll = currentScroll;
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Hero text animation
    const heroTitle = document.querySelector('.hero-title');
    const heroSubtitle = document.querySelector('.hero-subtitle');
    const heroTag = document.querySelector('.hero-tag');
    const heroCta = document.querySelector('.hero-cta');
    const heroStats = document.querySelector('.hero-stats');

    if (heroTag) heroTag.style.animation = 'fadeInUp 0.6s ease forwards';
    if (heroTitle) heroTitle.style.animation = 'fadeInUp 0.6s ease 0.1s forwards';
    if (heroSubtitle) heroSubtitle.style.animation = 'fadeInUp 0.6s ease 0.2s forwards';
    if (heroCta) heroCta.style.animation = 'fadeInUp 0.6s ease 0.3s forwards';
    if (heroStats) heroStats.style.animation = 'fadeInUp 0.6s ease 0.4s forwards';

    // Add animation styles dynamically
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .reveal {
            opacity: 0;
            transform: translateY(40px);
            transition: all 0.6s ease;
        }
        
        .reveal.revealed {
            opacity: 1;
            transform: translateY(0);
        }
        
        .nav-scrolled {
            background: rgba(10, 10, 15, 0.95) !important;
        }
        
        .hero-tag,
        .hero-title,
        .hero-subtitle,
        .hero-cta,
        .hero-stats {
            opacity: 0;
        }
    `;
    document.head.appendChild(style);

    // Stagger animation for highlight cards
    const highlightCards = document.querySelectorAll('.highlight-card');
    highlightCards.forEach((card, index) => {
        card.style.transitionDelay = `${index * 0.1}s`;
    });

    // Stagger animation for skill categories
    const skillCategories = document.querySelectorAll('.skill-category');
    skillCategories.forEach((category, index) => {
        category.style.transitionDelay = `${index * 0.1}s`;
    });

    console.log('Portfolio loaded successfully ✨');
});

