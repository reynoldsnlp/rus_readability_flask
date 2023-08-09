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

const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

const comparer = (idx, asc) => (a, b) => ((v1, v2) =>
  v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
)(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

const sortTable = (th) => {
  const table = th.closest('table');
  const tbody = table.querySelector('tbody');
  Array.from(tbody.querySelectorAll('tr'))
    .sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
    .forEach(tr => tbody.appendChild(tr));
}
