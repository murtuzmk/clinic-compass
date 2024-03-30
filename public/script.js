document.querySelectorAll('#navbar a').forEach(link => {
    link.addEventListener('click', function() {
        document.querySelector('#navbar .active').classList.remove('active');
        this.classList.add('active');
    });
});
document.getElementById('toggleSidebar').addEventListener('click', function() {
    const sidebar = document.getElementById('sidebar');
    const toggleIcon = document.getElementById('toggleSidebar').querySelector('img');

    sidebar.classList.toggle('collapsed');

    if (sidebar.classList.contains('collapsed')) {
        toggleIcon.src = 'sidebar-show-svgrepo-com.svg'; // Path to your "close" icon
        toggleIcon.alt = 'Close Sidebar';
    } else {
        toggleIcon.src = 'sidebar-hide-svgrepo-com.svg'; // Path to your "open" icon
        toggleIcon.alt = 'Open Sidebar';
    }
});