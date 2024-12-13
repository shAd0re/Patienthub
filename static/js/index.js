// Main initialization
$(document).ready(function() {
    // Initialize date picker with minimum date
    const today = new Date().toISOString().split('T')[0];
    $('#date').attr('min', today);

    // Initialize event handlers
    initializeLoginHandler();
    initializeAppointmentHandlers();
    initializeRegistrationHandlers();
});

// Status message functionality
function showStatus(message, isError = false) {
    const statusDiv = $('#booking-status');
    statusDiv.removeClass('alert-success alert-danger')
        .addClass(isError ? 'alert alert-danger' : 'alert alert-success')
        .text(message)
        .show();
}

// Authentication Module
function initializeLoginHandler() {
    $('#loginForm').on('submit', function(e) {
        e.preventDefault();
        
        const username = $('#username').val();
        const password = $('#password').val();

        if (!username || !password) {
            alert('Please fill in all fields');
            return;
        }

        $.ajax({
            url: '/auth/login',
            method: 'POST',
            contentType: 'application/x-www-form-urlencoded',
            data: { username, password },
            success: function(response) {
                alert('Response received: ' + JSON.stringify(response)); // Debug alert
                localStorage.setItem('token', response.access_token);
                localStorage.setItem('userRole', response.role);
                
                alert('Role detected: ' + response.role); // Debug alert
                
                if (response.role === 'doctor') {
                    alert('Should redirect to doctor dashboard'); // Debug alert
                    window.location.href = '/appointments/doctor-dashboard';
                } else {
                    alert('Should redirect to all appointments'); // Debug alert
                    window.location.href = '/appointments/all-appointments';
                }
            },
            error: function(xhr, status, error) {
                console.error('Login error:', xhr.responseText);
                alert('Login failed: ' + error);
            }
        });
    });
}

// Appointment Module
function initializeAppointmentHandlers() {
    debugLog('Initializing appointment handlers');
    
    $('#doctor').on('change', function() {
        const doctorId = $(this).val();
        debugLog('Doctor selected:', doctorId);
        
        if (doctorId) {
            updateDateAvailability(doctorId);
        } else {
            const dateInput = document.querySelector('#date');
            if (dateInput._flatpickr) {
                dateInput._flatpickr.destroy();
            }
            $('#date').val('');
            $('#time').find('option:gt(0)').remove();
        }
    });

    $('.book-btn').on('click', function() {
        const appointmentData = {
            doctor_id: parseInt($('#doctor').val()),
            appointment_date: $('#date').val(),
            appointment_time: $('#time').val(),
            description: $('#description').val()
        };
        
        debugLog('Booking appointment:', appointmentData);

        if (!appointmentData.doctor_id || !appointmentData.appointment_date || !appointmentData.appointment_time) {
            showStatus('Please select doctor, date and time', true);
            return;
        }

        bookAppointment(appointmentData);
    });
}


function updateTimeSlots(doctorId, selectedDate) {
    if (!doctorId || !selectedDate) return;
    
    debugLog('Updating time slots for:', { doctorId, selectedDate });
    
    const timeSelect = $('#time');
    timeSelect.find('option:gt(0)').remove();
    
    $.ajax({
        url: `/appointments/doctors/${doctorId}/availability`,
        method: 'GET',
        data: { date: selectedDate },
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        success: function(response) {
            const availableTimes = response.available_times;
            debugLog('Available times:', availableTimes);
            
            if (availableTimes.length === 0) {
                showStatus('No available time slots for selected date', true);
                return;
            }

            availableTimes.sort().forEach(time => {
                timeSelect.append(`<option value="${time}">${time}</option>`);
            });
            
            $('#booking-status').hide();
        },
        error: function(xhr, status, error) {
            console.error('Error fetching time slots:', error);
            showStatus('Error fetching time slots: ' + error, true);
        }
    });
}

function bookAppointment(appointmentData) {
    $.ajax({
        url: '/appointments/',
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
        },
        data: JSON.stringify(appointmentData),
        success: function(response) {
            alert('Appointment booked successfully!');
            showStatus('Appointment booked successfully!');
            setTimeout(() => {
                window.location.href = '/appointments/all-appointments';
            }, 2000);
        },
        error: function(xhr, status, error) {
            alert('Failed to book appointment: ' + error);
            showStatus('Failed to book appointment: ' + error, true);
        }
    });
}

// Registration Module
function initializeRegistrationHandlers() {
    // Role selection handler
    $('#role').on('change', function() {
        const selectedRole = $(this).val();
        $('#patientFields, #doctorFields').hide();
        $(`#${selectedRole}Fields`).show();
    });

    // Registration form submission
    $('#registerForm').on('submit', async function(e) {
        e.preventDefault();
        
        const role = $('#role').val();
        const registrationData = buildRegistrationData(role);
        
        try {
            const response = await fetch(`/auth/register/${role}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(registrationData)
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || 'Registration failed');
            }
            
            window.location.href = '/auth/login-page';
        } catch (error) {
            alert('Error: ' + error.message);
            showStatus('Error: ' + error.message, true);
        }
    });
}

function buildRegistrationData(role) {
    const baseUserData = {
        user: {
            user_name: $('#username').val(),
            password: $('#password').val(),
            dob: $('#dob').val(),
            role: role
        }
    };

    if (role === 'doctor') {
        return {
            ...baseUserData,
            doctor: {
                first_name: $('#doctorFirstName').val(),
                last_name: $('#doctorLastName').val(),
                phone: $('#doctorPhone').val(),
                specialization: $('#specialization').val(),
                available_days: getSelectedDays(),
                available_times: getSelectedTimes()
            }
        };
    }

    return {
        ...baseUserData,
        patient: {
            first_name: $('#patientFirstName').val(),
            last_name: $('#patientLastName').val(),
            gender: $('#gender').val(),
            phone: $('#patientPhone').val()
        }
    };
}

function getSelectedDays() {
    return ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        .filter(day => $(`#${day}`).is(':checked'))
        .map(day => day.charAt(0).toUpperCase() + day.slice(1));
}

function getSelectedTimes() {
    return Array.from({length: 9}, (_, i) => i + 9)
        .filter(hour => $(`#time-${hour}`).is(':checked'))
        .map(hour => `${hour}:00`);
}

//function to handle date restrictions based on doctor's schedule
function updateDateAvailability(doctorId) {
    if (!doctorId) return;
    
    debugLog('Fetching availability for doctor:', doctorId);
    
    $.ajax({
        url: `/appointments/doctors/${doctorId}/availability`,
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        success: function(response) {
            debugLog('Received response:', response);
            
            const availableDays = response.available_days;
            debugLog('Available days:', availableDays);
            
            const dateInput = document.querySelector('#date');
            
            // Clear any existing flatpickr instance
            if (dateInput._flatpickr) {
                dateInput._flatpickr.destroy();
            }
            
            // Initialize flatpickr
            flatpickr(dateInput, {
                dateFormat: 'Y-m-d',
                minDate: 'today',
                enable: [
                    function(date) {
                        const dayName = date.toLocaleDateString('en-US', { weekday: 'long' });
                        debugLog('Checking day:', dayName);
                        return availableDays.includes(dayName);
                    }
                ],
                onChange: function(selectedDates, dateStr) {
                    debugLog('Date selected:', dateStr);
                    if (selectedDates.length > 0) {
                        updateTimeSlots(doctorId, dateStr);
                    }
                }
            });
        },
        error: function(xhr, status, error) {
            console.error('Error fetching availability:', error);
            showStatus('Error fetching doctor availability: ' + error, true);
        }
    });
}

// function to check if a date should be enabled
function isDateAvailable(date, availableDays) {
    const dayOfWeek = date.toLocaleDateString('en-US', { weekday: 'long' });
    return availableDays.includes(dayOfWeek);
}

function disableDates(date, availableDays) {
    const dayOfWeek = date.toLocaleDateString('en-US', { weekday: 'long' });
    return availableDays.includes(dayOfWeek);
}

function debugLog(message, data) {
    console.log(message, data);
}