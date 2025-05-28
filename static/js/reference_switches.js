// Удаление коммутатора
  document.querySelectorAll('.ref-sw-delete-btn').forEach(button => {
    button.addEventListener('click', () => {
      const id = button.getAttribute('data-id');
      if (confirm('Удалить коммутатор?')) {
        button.closest('tr').remove();
      }
    });
  });