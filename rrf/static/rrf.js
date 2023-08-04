function submitForm(event) {
  event.preventDefault(); // Prevent the default form submission behavior

  const form = event.target; // Get the form element
  const prog = document.getElementById('progress');
  prog.classList.remove('is-invisible');
  const formData = new FormData(form); // Create a new FormData object from the form data

  // Perform an AJAX request using Fetch API
  fetch(form.action, {
    method: form.method,
    body: formData
  })
    .then(response => response.text()) // Extract the response body as text
    .then(responseText => {
      console.log(responseText);
      const responseDiv = document.getElementById('report');
      responseDiv.innerHTML = responseText; // Display the response in the div
      prog.classList.add('is-invisible');
    })
    .catch(error => {
      console.error('Error:', error);
      // Optionally, you can display an error message in the div
      const responseDiv = document.getElementById('report');
      responseDiv.innerHTML = 'An error occurred while submitting the form.';
      prog.classList.add('is-invisible');
    });
}

// Add the submitForm function as a submit event listener to the form
document.getElementById('textForm').addEventListener('submit', submitForm);
