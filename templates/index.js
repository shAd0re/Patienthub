$(document).ready(function() {
    $('#loginForm').on('submit', function(e) {
        e.preventDefault();
        
        const username = $('#username').val();
        const password = $('#password').val();

        // Basic validation
        if (!username || !password) {
            alert('Please fill in all fields');
            return;
        }

        // TODO: Add API call here
        $.ajax({
            url: '/auth/login',  // Your FastAPI endpoint
            method: 'POST',
            contentType: 'application/x-www-form-urlencoded',
            data: {
                username: username,
                password: password
            },
            success: function(response) {
                // Store token and redirect
                localStorage.setItem('token', response.access_token);
                window.location.href = '/dashboard.html';
            },
            error: function(xhr, status, error) {
                alert('Login failed: ' + error);
            }
        });
    });
});