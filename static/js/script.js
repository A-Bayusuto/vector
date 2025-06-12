function toggleFileNameInput() {
    const fileNameSection = document.getElementById("fileNameSection");
    if (fileNameSection.style.display === "none") {
        fileNameSection.style.display = "block";
    } else {
        fileNameSection.style.display = "none";
    }
}

function scrollToBottom() {
    const chatMessages = document.getElementById("messages");
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function updateTemperature(value) {
    // Update hidden sliders
    const inputElements = document.querySelectorAll(".sliderInputValue");
    inputElements.forEach((el) => {
        if (el.tagName === "INPUT") {
            el.value = value; // Update the value of input elements
        } else {
            el.textContent = value; // Update the content of span elements
        }
    });
    // Update the display span
    document.getElementById("displaySliderValue").textContent = value;

    // Send the updated value to the server
    fetch('/update_temperature', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ temperature: value }),
    })
        .then(response => response.json())
        .then(data => console.log(data));
}

function setSystem() {
    // Get values from the inputs
    const defaultDb = document.getElementById("default_db").value;
    const sliderValue = document.getElementById("sliderValue").value;
    const systemBehavior = document.getElementById("sys_input").value;

    // Create the payload to send to the server
    const data = {
        default_db: defaultDb,
        temperature: sliderValue,
        system_role: systemBehavior,
    };

    // Send the data to the server using Fetch API
    fetch('/set_system', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data), // Convert JavaScript object to JSON
    })
        .then(response => response.json())
        .then(data => {
            console.log(data); // Handle the server's response
            alert("System behavior updated successfully!");
        })
        .catch(error => {
            console.error('Error:', error); // Handle errors
            alert("An error occurred while updating the system behavior.");
        });
}

function handleKeypress(e) {
    console.log("see keypress"); // Debugging log

    if (e.key === "Enter" && !e.shiftKey) {
        console.log("see"); // Debugging log for Enter key detection

        e.preventDefault(); // Prevent default new line behavior

        // Find the closest form and submit it
        const form = e.currentTarget.closest("form");
        if (form) {
            form.submit();
        } else {
            console.error("No form found for textarea"); // Log error if no form is found
        }
    }
}

document.getElementById("userForm").addEventListener("submit", function (event) {
    // Show the loading icon
    document.getElementById("loadingIcon").style.display = "inline";

    // Optionally disable the submit button to prevent multiple submissions
    const submitButton = this.querySelector("button[type='submit']");
    submitButton.disabled = true;

});

// Call the function after the page loads
window.onload = function () {
    // Scroll to bottom
    scrollToBottom();
};


function toggleFileNameInput() {
    const fileNameSection = document.getElementById("fileNameSection");
    if (fileNameSection.style.display === "none") {
        fileNameSection.style.display = "block";
    } else {
        fileNameSection.style.display = "none";
    }
}

function scrollToBottom() {
    const chatMessages = document.getElementById("messages");
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function updateTemperature(value) {
    // Update hidden sliders
    const inputElements = document.querySelectorAll(".sliderInputValue");
    inputElements.forEach((el) => {
        if (el.tagName === "INPUT") {
            el.value = value; // Update the value of input elements
        } else {
            el.textContent = value; // Update the content of span elements
        }
    });
    // Update the display span
    document.getElementById("displaySliderValue").textContent = value;

    // Send the updated value to the server
    fetch('/update_temperature', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ temperature: value }),
    })
        .then(response => response.json())
        .then(data => console.log(data));
}

function setSystem() {
    // Get values from the inputs
    const defaultDb = document.getElementById("default_db").value;
    const sliderValue = document.getElementById("sliderValue").value;
    const systemBehavior = document.getElementById("sys_input").value;

    // Create the payload to send to the server
    const data = {
        default_db: defaultDb,
        temperature: sliderValue,
        system_role: systemBehavior,
    };

    // Send the data to the server using Fetch API
    fetch('/set_system', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data), // Convert JavaScript object to JSON
    })
        .then(response => response.json())
        .then(data => {
            console.log(data); // Handle the server's response
            alert("System behavior updated successfully!");
        })
        .catch(error => {
            console.error('Error:', error); // Handle errors
            alert("An error occurred while updating the system behavior.");
        });
}

function handleKeypress(e) {
    console.log("see keypress"); // Debugging log

    if (e.key === "Enter" && !e.shiftKey) {
        console.log("see"); // Debugging log for Enter key detection

        e.preventDefault(); // Prevent default new line behavior

        // Find the closest form and submit it
        const form = e.currentTarget.closest("form");
        if (form) {
            form.submit();
        } else {
            console.error("No form found for textarea"); // Log error if no form is found
        }
    }
}


document.getElementById("userForm").addEventListener("submit", function (event) {
    // Show the loading icon
    document.getElementById("loadingIcon").style.display = "inline";

    // Optionally disable the submit button to prevent multiple submissions
    const submitButton = this.querySelector("button[type='submit']");
    submitButton.disabled = true;

});

// Call the function after the page loads
window.onload = function () {
    // Scroll to bottom
    scrollToBottom();
};

//------------------------------------------------------

document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    console.log('fileinput: ', fileInput)
    console.log('uploadForm: ', uploadForm)
    if (fileInput && uploadForm) {
        fileInput.addEventListener('change', function () {
            console.log("Entered file input change listener");

            if (this.files.length > 0) {
                console.log("Files selected: " + this.files.length);
                uploadForm.submit();
            } else {
                console.log("No files selected.");
            }
        });
    } else {
        console.error("File input or upload form element not found.");
    }
});

/* =========================================  */
// Helper function to get a cookie by name
function getCookie(name) {
    let cookieArr = document.cookie.split(';');
    for (let i = 0; i < cookieArr.length; i++) {
        let cookie = cookieArr[i].trim();
        if (cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1);
        }
    }
    return null;
}

// Helper function to set a cookie
function setCookie(name, value, days) {
    let d = new Date();
    d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000)); // Expiry time in days
    let expires = "expires=" + d.toUTCString();
    document.cookie = name + "=" + value + ";" + expires + ";path=/";
}


/* =========================================  */

document.addEventListener('DOMContentLoaded', function () {
    const chatItems = document.querySelectorAll('.chat-item');

    const selectedChat = getCookie('chat');
    if (selectedChat) {
        chatItems.forEach(function (item) {
            if (item.getAttribute('data-chat') === selectedChat) {
                item.classList.add('selected');
            }
        });
    }

    chatItems.forEach(function (item) {
        item.addEventListener('click', function () {
            // Get chat value from a data attribute; fallback to inner text
            const chatValue = this.getAttribute('data-chat') || this.textContent.trim();
            // Set the value in the hidden input
            document.getElementById('chatNameInput').value = chatValue;
            setCookie('chat', chatValue, 1);

            // Remove 'selected' class from all chat items
            chatItems.forEach(function (chatItem) {
                chatItem.classList.remove('selected');
            });

            // Add 'selected' class to the clicked chat item
            this.classList.add('selected');

            // Submit the form to load the selected chat
            document.getElementById('loadChatForm').submit();
        });
    });
});

// document.addEventListener("DOMContentLoaded", function () {
//     const userForm = document.getElementById("userForm");
//     const sendButton = document.getElementById("sendButton");

//     // Prevent form submission when the button is clicked
//     userForm.addEventListener("submit", function (event) {
//         event.preventDefault(); // Prevent the default form submit behavior

//         // Get the values from the inputs
//         const userInput = document.getElementById("userInput").value;
//         const vectordb = document.getElementById("vectordbDropdown").value;

//         // Create the payload to send to the server
//         const data = {
//             userInput: userInput,
//             vectordb: vectordb,
//         };

//         // Send the data to the server using Fetch API
//         fetch("/", {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json", // Set content type to JSON
//             },
//             body: JSON.stringify(data), // Convert JavaScript object to JSON
//         })
//             .then((response) => response.json()) // Parse JSON response
//             .then((responseData) => {
//                 console.log(responseData); // Handle the server's response (e.g., show a message)
//                 alert("Your message was sent successfully!");
//                 // Optionally, reset the form or handle response data (e.g., clear the input fields)
//                 userForm.reset(); // Reset form fields after successful submission
//             })
//             .catch((error) => {
//                 console.error("Error:", error); // Handle errors
//                 alert("An error occurred while sending your message.");
//             });
//     });

//     sendButton.addEventListener("click", function (event) {
//         event.preventDefault(); // Prevent the default form submit behavior

//         // Get the values from the inputs
//         const userInput = document.getElementById("userInput").value;
//         const vectordb = document.getElementById("vectordbDropdown").value;

//         // Create the payload to send to the server
//         const data = {
//             userInput: userInput,
//             vectordb: vectordb,
//         };

//         // Send the data to the server using Fetch API
//         fetch("/", {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json", // Set content type to JSON
//             },
//             body: JSON.stringify(data), // Convert JavaScript object to JSON
//         })
//             .then((response) => response.json()) // Parse JSON response
//             .then((responseData) => {
//                 console.log(responseData); // Handle the server's response (e.g., show a message)
//                 alert("Your message was sent successfully!");
//                 // Optionally, reset the form or handle response data (e.g., clear the input fields)
//                 userForm.reset(); // Reset form fields after successful submission
//             })
//             .catch((error) => {
//                 console.error("Error:", error); // Handle errors
//                 alert("An error occurred while sending your message.");
//             });
//     });
// });
