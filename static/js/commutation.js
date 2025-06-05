// Удаление пользователя
document.querySelectorAll('.ref-users-delete-btn').forEach(button => {
  button.addEventListener('click', () => {
    const id = button.getAttribute('data-id');
    if (confirm('Удалить пользователя?')) {
      fetch(`/delete_user/${id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        if (response.ok) {
          button.closest('tr').remove();
        } else {
          alert('Ошибка при удалении пользователя.');
        }
      })
      .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при удалении.');
      });
    }
  });
});