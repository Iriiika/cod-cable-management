// Удаление подключения 
  document.querySelectorAll('.comm-delete-btn').forEach(button => {
    button.addEventListener('click', () => {
      const id = button.getAttribute('data-id');
      if (confirm('Удалить подключение?')) {
        button.closest('tr').remove();
      }
    });
  });