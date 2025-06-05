document.addEventListener('DOMContentLoaded', function () {
    const nameFilter = document.getElementById('nameFilter');
    const shortNameFilter = document.getElementById('shortNameFilter');
    const table = document.getElementById('dataCentersTable');
    const rows = table.getElementsByTagName('tr');

    function filterTable() {
      const nameValue = nameFilter.value.toLowerCase();
      const shortNameValue = shortNameFilter.value.toLowerCase();

      for (let i = 1; i < rows.length; i++) {
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

    nameFilter.addEventListener('input', filterTable);
    shortNameFilter.addEventListener('input', filterTable);

    function exportToExcel() {
      alert('Экспорт в Excel пока не реализован.');
    }
  });