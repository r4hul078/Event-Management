document.getElementById('login-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (!email || !password) {
        alert('Enter both email and password.');
        return;
    }

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();
        console.log('Login response:', data);  // Debug log
        if (response.ok && data.redirect) {
            window.location.href = '/dashboard';
        } else {
            alert(data.error || 'Failed.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Some error');
    }
});