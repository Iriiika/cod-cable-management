document.querySelector('form').addEventListener('submit', (e) => {
    const serverId = document.getElementById('server_id').value;
    const switchId = document.getElementById('switch_id').value;
    const port = document.getElementById('port').value;
    const label = document.getElementById('label').value;

    if (!serverId || !switchId || !port || !label) {
      e.preventDefault();
      alert('Пожалуйста, заполните все поля');
    }
  });