// app/static/index/script.js
document.addEventListener('DOMContentLoaded', function() {
    var nav = document.getElementById('navigation');
    var menu = nav.querySelector('.nav-links');
    var overlay = document.getElementById('overlay');
    var lastScrollTop = 0;

    window.addEventListener('scroll', function() {
        var scrollTop = window.pageYOffset || document.documentElement.scrollTop;

        if (scrollTop > lastScrollTop && scrollTop > 60) {
            nav.classList.add('scrolled');
            nav.classList.remove('hidden');
        } else {
            nav.classList.add('hidden');
        }
        lastScrollTop = scrollTop;

        if (scrollTop === 0) {
            nav.classList.remove('scrolled');
            nav.classList.remove('hidden');
        }
    });

    document.getElementById('menu-toggle').addEventListener('click', function() {
        menu.classList.toggle('active');
        nav.classList.toggle('menu-opened');
    });

    var buttons = document.querySelectorAll('.action-button');
    buttons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            overlay.style.right = '0';
            setTimeout(function() {
                window.location.href = button.getAttribute('href');
            }, 500);
        });
    });

    var navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            overlay.style.right = '0';
            setTimeout(function() {
                window.location.href = link.getAttribute('href');
            }, 500);
        });
    });
});
