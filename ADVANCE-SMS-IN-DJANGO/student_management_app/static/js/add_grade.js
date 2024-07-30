document.getElementById('sessionYear').addEventListener('change', function() {
    var sessionYearId = this.value;
    updateStudentDropdown(sessionYearId);
});

document.getElementById('studentDropdown').addEventListener('change', function() {
    var studentId = this.value;
    updateSubjectsAndGrades(studentId);
});

function updateStudentDropdown(sessionYearId) {
    fetch(`/load_students?session_year_id=${sessionYearId}`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('studentDropdown').innerHTML = html;
            updateSubjectsAndGrades(document.getElementById('studentDropdown').value);
        })
        .catch(error => console.error('Error loading students:', error));
}

function updateSubjectsAndGrades(studentId) {
    if (!studentId) return;  // Avoid querying if no student is selected
    fetch(`/load_subjects_and_grades?student_id=${studentId}`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('gradesTableBody').innerHTML = html;
            document.getElementById('gradesSection').style.display = 'block';
        })
        .catch(error => console.error('Error loading grades:', error));
}
