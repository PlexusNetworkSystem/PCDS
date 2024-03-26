function suspend() {
    fetch('/panelcmd', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            token: token,
            process: 'suspend'
        })
    })
        .then(response => {
            if (response.ok) {
                console.log('System suspended successfully');
            } else {
                console.error('Failed to suspend system');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}
function wakeup() {
    fetch('/panelcmd', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            token: token,
            process: 'wakeup'
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.message === '[200] System Waked Up') {
                console.log('System wake up successfully');
            } else {
                console.error('Failed to wake up system');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

fetch('/panelcmd', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        token: token,
        process: 'generic'
    })
})
    .then(response => response.json())
    .then(data => {
        console.log(data);
        document.getElementById('header_ip').textContent = data.ip;
        document.getElementById('software_name').textContent = data.name;
        document.getElementById('software_version').textContent = data.version;
        document.getElementById('software_env').textContent = data.environment;
        document.getElementById('software_running_user').textContent = data.user;
        document.getElementById('software_port').textContent = data.port;
        document.getElementById('server_name').textContent = data.servername;
        document.getElementById('server_location').textContent = data.location;
        document.getElementById('server_specs_cpu').textContent = data.cpu;
        document.getElementById('server_specs_gpu').textContent = data.gpu;
        document.getElementById('server_specs_ram').textContent = data.ram + " GB";
        document.getElementById('server_specs_os').textContent = data.os;
        document.getElementById('server_specs_disk').textContent = data.disk + "GB";
    })
    .catch(error => {
        console.error('Error:', error);
    });


setInterval(() => {
    fetch('/panelcmd', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            token: token,
            process: 'dynamic'
        })
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('cpu_usage').textContent = data.cpu_usage + '%';
            document.getElementById("cpu_usage_bar").value = data.cpu_usage;
            document.getElementById('ram_usage').textContent = data.ram_usage + '%';
            document.getElementById("ram_usage_bar").value = data.ram_usage;
            document.getElementById('software_status').textContent = data.status;
            if (data.status === 'running') {
                document.getElementById('software_status').style = 'background: green;';
            } else {
                document.getElementById('software_status').style = 'background: #a60000;';
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}, 1000);

setInterval(() => {
    fetch('/panelcmd', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            token: token,
            process: 'disk'
        })
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('disk_usage').textContent = data.used + '%';
            document.getElementById("disk_usage_bar").value = data.used;
        })
        .catch(error => {
            console.error('Error:', error);
        });
}, 5000);

