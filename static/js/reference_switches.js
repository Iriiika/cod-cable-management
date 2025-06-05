// Удаление коммутатора
document.querySelectorAll('.ref-sw-delete-btn').forEach(button => {
  button.addEventListener('click', () => {
    const id = button.getAttribute('data-id');
    if (confirm('Удалить коммутатор?')) {
      fetch(`/delete_switch/${id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        if (response.ok) {
          button.closest('tr').remove();
        } else {
          alert('Ошибка при удалении коммутатора.');
        }
      })
      .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при удалении.');
      });
    }
  });
});