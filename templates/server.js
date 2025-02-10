document.getElementById('signUpForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('http://127.0.0.1:5000/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password }),
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message);
            window.location.href = '/'; // Redirect to login page
        } else {
            alert(data.message);
        }
    } catch (error) {document.getElementById('signUpForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();

    if (!username || !email || !password) {
        alert('Please fill in all fields.');
        return;
    }

    try {
        const response = await fetch('http://127.0.0.1:5000/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password }),
        });

        if (!response.ok) {
            const data = await response.json();
            alert(data.message);
            return;
        }

        const data = await response.json();
        alert(data.message);
        window.location.href = '/'; // Redirect to login page
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
});document.getElementById('signUpForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();

    if (!username || !email || !password) {
        alert('Please fill in all fields.');
        return;
    }

    try {
        const response = await fetch('http://127.0.0.1:5000/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password }),
        });

        if (!response.ok) {
            const data = await response.json();
            alert(data.message);
            return;
        }

        const data = await response.json();
        alert(data.message);
        window.location.href = '/'; // Redirect to login page
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
});document.getElementById('signUpForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();

    if (!username || !email || !password) {
        alert('Please fill in all fields.');
        return;
    }

    try {
        const response = await fetch('http://127.0.0.1:5000/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password }),
        });

        if (!response.ok) {
            const data = await response.json();
            alert(data.message);
            return;
        }

        const data = await response.json();
        alert(data.message);
        window.location.href = '/'; // Redirect to login page
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
});
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
});
