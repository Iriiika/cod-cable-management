// Удаление пользователя
  document.querySelectorAll('.ref-users-delete-btn').forEach(button => {
    button.addEventListener('click', () => {
      const id = button.getAttribute('data-id');
      if (confirm('Удалить пользователя?')) {
        button.closest('tr').remove();
      }
    });
  });