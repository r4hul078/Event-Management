'use strict';

document.getElementById('register-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const address = document.getElementById('address').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    if (!email || !password || !confirmPassword) {
        alert('Please fill in all fields.');
        return;
    }

    if (password !== confirmPassword) {
        alert('Passwords do not match!');
        return;
    }

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const contentType = response.headers.get('content-type');

        if (contentType && contentType.includes('application/json')) {
            const data = await response.json();
            
            if (response.ok) {
                alert('Registration successful! Please log in.');
                window.location.href = '/login';
            } else {
                alert(data.error || 'Registration failed.');
            }
        } else {
            const errorText = await response.text();  // Log the HTML error
            console.error('Server Response:', errorText);
            alert('Check Console for erro');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Some error.');
    }
});
