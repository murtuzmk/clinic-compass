document.querySelectorAll('nav#navbar a').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        document.querySelector('.active').classList.remove('active');
        this.classList.add('active');

        const sectionId = this.getAttribute('href');
        document.querySelector(sectionId).scrollIntoView({ behavior: 'smooth' });
    });
});
