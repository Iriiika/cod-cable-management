document.addEventListener('DOMContentLoaded', function () {
    const nameFilter = document.getElementById('nameFilter');
    const shortNameFilter = document.getElementById('shortNameFilter');
    const table = document.getElementById('dataCentersTable');
    const tbody = table.getElementsByTagName('tbody')[0];
    const headers = table.getElementsByTagName('th');

    let sortDirection = 1;
    let lastSortedColumn = -1;

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

    for (let i = 0; i < headers.length - 1; i++) {
      headers[i].style.cursor = 'pointer';
      headers[i].addEventListener('click', () => sortTable(i));
    }

    nameFilter.addEventListener('input', filterTable);
    shortNameFilter.addEventListener('input', filterTable);
});