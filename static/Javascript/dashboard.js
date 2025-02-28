// This list will hold all our events
let events = [];

// This function changes which page we see
function changePage(sectionId) {
    let allPages = document.getElementsByClassName("content-section");
    for (let i = 0; i < allPages.length; i++) {
        allPages[i].style.display = "none";
    }
    document.getElementById(sectionId).style.display = "block";
}

// This function shows the events on the Dashboard
function showEvents(eventList) {
    let eventListArea = document.getElementById("events-list");
    eventListArea.innerHTML = ""; // Clear the list
    if (eventList.length === 0) {
        eventListArea.innerHTML = "<li>No events found!</li>";
        return;
    }
    for (let i = 0; i < eventList.length; i++) {
        let event = eventList[i];
        let newItem = document.createElement("li");
        newItem.className = event.paid ? "paid" : "unpaid";
        newItem.innerHTML = "<b>" + event.name + "</b><br>" +
                            "Date: " + event.date + "<br>" +
                            "Venue: " + event.venue + "<br>" +
                            "Address: " + event.address + "<br>" +
                            "Description: " + event.description + "<br>" +
                            "Phone: " + event.phone_number + "<br>" +
                            "Status: " + (event.paid ? "Paid" : "Not Paid");
        let deleteButton = document.createElement("button");
        deleteButton.innerText = "Delete";
        deleteButton.setAttribute("data-event-id", event.id);
        deleteButton.onclick = function() {
            deleteEvent(event.id);
        };
        newItem.appendChild(deleteButton);
        eventListArea.appendChild(newItem);
    }
}

// This function shows the bills on the Bills page
function showBills(eventList) {
    let billListArea = document.getElementById("bill-list");
    billListArea.innerHTML = ""; // Clear the list
    if (eventList.length === 0) {
        billListArea.innerHTML = "<li>No bills found!</li>";
        return;
    }
    for (let i = 0; i < eventList.length; i++) {
        let event = eventList[i];
        let newItem = document.createElement("li");
        newItem.className = event.paid ? "paid" : "unpaid";
        newItem.innerHTML = "<b>" + event.name + "</b><br>" +
                            "Date: " + event.date + "<br>" +
                            "Venue: " + event.venue + "<br>" +
                            "Address: " + event.address + "<br>" +
                            "Phone: " + event.phone_number + "<br>" +
                            "Description: " + event.description + "<br>" +
                            "Amount: Rs 10,000<br>" +
                            "Status: " + (event.paid ? "Paid" : "Not Paid");
        if (!event.paid) {
            let payButton = document.createElement("button");
            payButton.innerText = "Pay Now";
            payButton.setAttribute("data-event-id", event.id);
            payButton.onclick = function() {
                let eventId = this.getAttribute("data-event-id");
                let event = events.find(e => e.id == eventId);
                showReceipt(event);
            };
            newItem.appendChild(payButton);
        }
        let deleteButton = document.createElement("button");
        deleteButton.innerText = "Delete";
        deleteButton.setAttribute("data-event-id", event.id);
        deleteButton.onclick = function() {
            deleteEvent(event.id);
        };
        newItem.appendChild(deleteButton);
        billListArea.appendChild(newItem);
    }
}

// Popup for confirmation
function showReceipt(event) {
    let popup = document.createElement("div");
    popup.className = "receipt";
    popup.innerHTML = "<h2>Payment Receipt</h2>" +
                      "<p>Event: " + event.name + "</p>" +
                      "<p>Date: " + event.date + "</p>" +
                      "<p>Venue: " + event.venue + "</p>" +
                      "<p>Address: " + event.address + "</p>" +
                      "<p>Phone: " + event.phone_number + "</p>" +
                      "<p>Description: " + event.description + "</p>" +
                      "<p>Amount: Rs 10,000</p>" +
                      "<p>Date Paid: " + new Date().toLocaleDateString() + "</p>" +
                      "<button id='confirm-pay'>Confirm Payment</button>" +
                      "<button id='cancel-pay'>Cancel</button>";
    document.body.appendChild(popup);

    document.getElementById("confirm-pay").onclick = function() {
        confirmPayment(event.id);
    };
    document.getElementById("cancel-pay").onclick = function() {
        popup.remove();
    };
}

// A window for payment confirmation
function confirmPayment(eventId) {
    let request = new XMLHttpRequest();
    request.open("POST", "/pay/" + eventId);
    request.setRequestHeader("Content-Type", "application/json");
    request.onreadystatechange = function() {
        if (request.readyState === 4) {
            let response = JSON.parse(request.responseText);
            if (response.success) {
                let popup = document.querySelector(".receipt");
                if (popup) popup.remove();
                alert("Payment done!");
                loadEvents();
            } else {
                alert("Payment failed!");
            }
        }
    };
    request.send();
}

// Delete the function
function deleteEvent(eventId) {
    if (!confirm("Are you sure you want to delete this event?")) return;
    let request = new XMLHttpRequest();
    request.open("DELETE", "/events/" + eventId);
    request.setRequestHeader("Content-Type", "application/json");
    request.onreadystatechange = function() {
        if (request.readyState === 4) {
            if (request.status === 200) {
                let response = JSON.parse(request.responseText);
                if (response.success) {
                    alert("Event deleted!");
                    loadEvents(); // Refresh the lists
                } else {
                    alert("Deletion failed: " + response.error);
                }
            } else {
                alert("Error deleting event!");
            }
        }
    };
    request.send();
}

// Fetch the events from server
function loadEvents() {
    let request = new XMLHttpRequest();
    request.open("GET", "/events");
    request.onreadystatechange = function() {
        if (request.readyState === 4 && request.status === 200) {
            let data = JSON.parse(request.responseText);
            console.log("Events:", data);
            events = data.events || [];
            showEvents(events);
            showBills(events);
        } else if (request.readyState === 4) {
            console.log("Error loading events:", request.status);
        }
    };
    request.send();
}

// Searching event
function searchEvents() {
    let searchText = document.getElementById("event-search").value.toLowerCase();
    let foundEvents = [];
    for (let i = 0; i < events.length; i++) {
        if (events[i].name.toLowerCase().includes(searchText) || 
            events[i].venue.toLowerCase().includes(searchText) || 
            events[i].address.toLowerCase().includes(searchText)) {
            foundEvents.push(events[i]);
        }
    }
    showEvents(foundEvents);
    showBills(foundEvents);
}

// Logout
function logout() {
    let request = new XMLHttpRequest();
    request.open("POST", "/logout");
    request.setRequestHeader("Content-Type", "application/json");
    request.onreadystatechange = function() {
        if (request.readyState === 4 && request.status === 200) {
            let data = JSON.parse(request.responseText);
            if (data.success) {
                window.location.href = data.redirect;
            } else {
                alert("Logout failed!");
            }
        } else if (request.readyState === 4) {
            console.log("Error logging out:", request.status);
        }
    };
    request.send();
}

// After the page loads
window.onload = function() {
    console.log("Page is ready!");
    loadEvents();

    let form = document.getElementById("booking-form");
    form.onsubmit = function(event) {
        event.preventDefault();
        let eventName = document.getElementById("event-name").value;
        let eventDate = document.getElementById("event-date").value;
        let venue = document.getElementById("venue").value;
        let description = document.getElementById("description").value;
        let address = document.getElementById("address").value;
        let phoneNumber = document.getElementById("phone-number").value;

        if (!eventName || !eventDate || !venue || !description || !address || !phoneNumber) {
            alert("Please fill in everything!");
            return;
        }

        let request = new XMLHttpRequest();
        request.open("POST", "/events");
        request.setRequestHeader("Content-Type", "application/json");
        request.onreadystatechange = function() {
            if (request.readyState === 4 && request.status === 200) {
                let data = JSON.parse(request.responseText);
                if (data.success) {
                    alert("Event booked!");
                    form.reset();
                    loadEvents();
                } else {
                    alert("Booking failed!");
                }
            } else if (request.readyState === 4) {
                console.log("Error booking:", request.status);
            }
        };
        let dataToSend = {
            event_name: eventName,
            event_date: eventDate,
            venue: venue,
            description: description,
            address: address,
            phone_number: phoneNumber
        };
        request.send(JSON.stringify(dataToSend));
    };

    // Move logout button initialization here
    let logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
        logoutBtn.onclick = logout;
    }

    document.getElementById("event-search").onkeypress = function(e) {
        if (e.key === "Enter") {
            searchEvents();
        }
    };
};