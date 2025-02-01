;'use strict'


// Get the login form element
const loginForm = document.getElementById('login-form');

loginForm.addEventListener('submit', function(){
    event.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (email && password) {
        window.location.href = '/templates/html/dashboard.html';
    } else {
        alert('Please enter both email and password.');
    }
});