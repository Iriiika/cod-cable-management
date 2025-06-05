document.addEventListener('DOMContentLoaded', function () {
    const nameFilter = document.getElementById('nameFilter');
    const shortNameFilter = document.getElementById('shortNameFilter');
    const table = document.getElementById('dataCentersTable');
    const tbody = table.getElementsByTagName('tbody')[0];
    const headers = table.getElementsByTagName('th');

    let sortDirection = 1;
    let lastSortedColumn = -1;

    // Фильтрация
    function filterTable() {
      const nameValue = nameFilter.value.toLowerCase();
      const shortNameValue = shortNameFilter.value.toLowerCase();
      const rows = tbody.getElementsByTagName('tr');

      for (let i = 0; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        const name = cells[0].textContent.toLowerCase();
        const shortName = cells[1].textContent.toLowerCase();

        if (name.includes(nameValue) && shortName.includes(shortNameValue)) {
          rows[i].style.display = '';
        } else {
          rows[i].style.display = 'none';
        }
      }
    }

    // Сортировка
    function sortTable(columnIndex) {
      const rows = Array.from(tbody.getElementsByTagName('tr'));

      if (lastSortedColumn === columnIndex) {
        sortDirection = -sortDirection;
      } else {
        sortDirection = 1;
        lastSortedColumn = columnIndex;
      }

      rows.sort((a, b) => {
        const aValue = a.getElementsByTagName('td')[columnIndex].textContent.toLowerCase();
        const bValue = b.getElementsByTagName('td')[columnIndex].textContent.toLowerCase();
        return sortDirection * aValue.localeCompare(bValue);
      });

      while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
      }

      rows.forEach(row => tbody.appendChild(row));

      filterTable();
    }

    // Редактирование ячеек
    function makeEditable(cell, dcId, field) {
      const originalText = cell.textContent.trim();
      const input = document.createElement('input');
      input.type = 'text';
      input.value = originalText;
      input.className = 'edit-input';

      cell.textContent = '';
      cell.appendChild(input);
      input.focus();

      input.addEventListener('blur', () => {
        const newValue = input.value.trim();
        cell.textContent = newValue;

        if (newValue !== originalText) {
          const data = field === 'name' ? { name: newValue, short_name: cell.parentElement.cells[1].textContent.trim() } 
                                        : { name: cell.parentElement.cells[0].textContent.trim(), short_name: newValue };
          fetch(`/update_data_center/${dcId}`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
          })
          .then(response => response.json())
          .then(result => {
            if (result.error) {
              alert(result.error);
              cell.textContent = originalText;
            }
          })
          .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при сохранении изменений.');
            cell.textContent = originalText;
          });
        }
      });

      input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          input.blur();
        }
      });
    }

    // Делаем ячейки редактируемыми при двойном клике
    tbody.addEventListener('dblclick', (e) => {
      const cell = e.target;
      if (cell.tagName === 'TD' && cell.cellIndex < 2) { // Только первые две колонки (name, short_name)
        const row = cell.parentElement;
        const dcId = row.cells[2].querySelector('.delete-btn')?.href.match(/dc_id=(\d+)/)?.[1];
        if (dcId) {
          const field = cell.cellIndex === 0 ? 'name' : 'short_name';
          makeEditable(cell, dcId, field);
        }
      }
    });

    for (let i = 0; i < headers.length - 1; i++) {
      headers[i].style.cursor = 'pointer';
      headers[i].addEventListener('click', () => sortTable(i));
    }

    nameFilter.addEventListener('input', filterTable);
    shortNameFilter.addEventListener('input', filterTable);
});