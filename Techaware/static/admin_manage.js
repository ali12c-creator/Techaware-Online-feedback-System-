let activeStudentId = null;

async function manageStudentCourses(
    studentId, studentName) {
    activeStudentId = studentId;
    
    document.getElementById(
        'courses-modal-student').textContent = 
        `Student: ${studentName}`;
    
    // Load current courses
    await loadCurrentCourses(studentId);
    
    // Load all available courses
    const res = await fetch(
        '/api/admin/courses', 
        {credentials: 'include'});
    const data = await res.json();
    const courses = data.courses || [];
    
    const select = document.getElementById(
        'new-course-for-student');
    select.innerHTML = 
        '<option value="">Select Course</option>';
    courses.forEach(c => {
        select.innerHTML += 
            `<option value="${c.id}">${c.name} (${c.code})</option>`;
    });
    
    const modal = document.getElementById(
        'courses-modal');
    modal.style.display = 'flex';
}

async function loadCurrentCourses(studentId) {
    const res = await fetch(
        `/api/admin/student-courses/${studentId}`,
        {credentials: 'include'});
    const data = await res.json();
    const enrollments = data.enrollments || [];
    
    const container = document.getElementById(
        'current-courses-list');
    
    if (enrollments.length === 0) {
        container.innerHTML = 
            '<p style="color:#999;">No courses enrolled yet</p>';
        return;
    }
    
    container.innerHTML = enrollments.map(e => `
        <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 12px; background:#f9f9f9; border-radius:8px; margin-bottom:6px;">
            <span>${e.course_name} <small style="color:#999;">${e.semester || ''}</small></span>
            <button onclick="removeCourse(${e.id})" style="background:#ff5252; color:white; border:none; padding:2px 8px; border-radius:4px; cursor:pointer; font-size:12px;">Remove</button>
        </div>
    `).join('');
}

async function addNewCourse() {
    const courseId = document.getElementById(
        'new-course-for-student').value;
    if (!courseId) {
        alert('Please select a course!');
        return;
    }
    
    const res = await fetch(
        '/api/admin/student-courses', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            student_id: activeStudentId,
            course_id: parseInt(courseId)
        })
    });
    
    const data = await res.json();
    if (data.success) {
        showMessage('Course added!');
        loadCurrentCourses(activeStudentId);
    } else {
        showMessage(data.message || 'Error!', true);
    }
}

async function removeCourse(enrollmentId) {
    if (!confirm('Remove this course?')) return;
    
    const res = await fetch(
        `/api/admin/student-courses/${enrollmentId}`,
        {
        method: 'DELETE',
        credentials: 'include'
    });
    
    const data = await res.json();
    if (data.success) {
        showMessage('Course removed!');
        loadCurrentCourses(activeStudentId);
    } else {
        showMessage('Error removing!', true);
    }
}

function closeCoursesModal() {
    document.getElementById(
        'courses-modal').style.display = 'none';
}

// Admin Management Panel JavaScript

// Tab switching
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.admin-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.admin-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Show selected tab
    const selectedTab = document.querySelector(`.admin-tab[data-tab="${tabName}"]`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Show selected content
    const contentDiv = document.getElementById(`tab-${tabName}`);
    if (contentDiv) {
        contentDiv.classList.add('active');
    }
    
    // Load data for the tab
    loadTabData(tabName);
}

function loadTabData(tabName) {
    switch(tabName) {
        case 'users':
            loadUsers();
            break;
        case 'students':
            loadDepartmentsForStudents();
            loadBatchesForStudents();
            loadSectionsForStudents();
            loadStudents();
            break;
        case 'departments':
            loadDepartments();
            break;
        case 'batches':
            loadDepartmentsForBatches();
            loadBatches();
            break;
        case 'sections':
            loadDepartmentsForSections();
            loadBatchesForSectionFilter();
            loadSections();
            break;
        case 'courses':
            loadDepartmentsForCourse();
            loadCourses();
            break;
        case 'batch-subjects':
            loadDepartmentsForBatchSubjects();
            loadCoursesForBatchSubject();
            loadBatchSubjects();
            break;
        case 'teacher-assignments':
            loadDepartmentsForTeacherAssignments();
            loadTeachersForAssignment();
            loadTeacherAssignments();
            // Also load batches for filter section
            setTimeout(() => {
                const deptSelect = document.getElementById('ta-dept-id');
                if (deptSelect && deptSelect.value) {
                    loadBatchesForTeacherAssignment();
                }
            }, 100);
            break;
        case 'timetable':
            loadDepartmentsForTimetable();
            loadCoursesForTimetable();
            loadTeachersForTimetable();
            loadBatchesForTimetableFilter();
            loadTimetable();
            break;
        case 'teachers':
            loadDepartmentsForTeachers();
            loadTeachers();
            break;
        case 'feedback':
            loadFeedback();
            break;
        case 'smtp':
            loadSMTPConfig();
            break;
        case 'email':
            loadEmailSettings();
            break;
        case 'database':
            loadDatabaseStats();
            break;
        case 'settings':
            loadSystemSettings();
            break;
        case 'analytics':
            loadAnalytics();
            break;
        case 'reports':
            loadDepartmentsForReports();
            break;
    }
}

// Show message
function showMessage(text, isError = false) {
    const msg = document.getElementById('messageBox');
    msg.textContent = text;
    msg.className = 'message-box-admin' + (isError ? ' error' : ' success');
    msg.style.display = 'block';
    setTimeout(() => {
        msg.style.display = 'none';
    }, 5000);
}

// Load statistics
async function loadStats() {
    try {
        const res = await fetch('/api/admin/stats', {
            credentials: 'include'
        });
        const data = await res.json();
        
        document.getElementById('stat-users').textContent = data.users || 0;
        document.getElementById('stat-teachers').textContent = data.teachers || 0;
        document.getElementById('stat-feedback').textContent = data.feedback || 0;
        document.getElementById('stat-pending').textContent = data.pending || 0;
        
        // Update analytics stats if analytics tab is active
        const analyticsUsers = document.getElementById('analytics-users');
        if (analyticsUsers) {
            analyticsUsers.textContent = data.users || 0;
            document.getElementById('analytics-students').textContent = data.students || 0;
            document.getElementById('analytics-teachers').textContent = data.teachers || 0;
            document.getElementById('analytics-courses').textContent = data.courses || 0;
            document.getElementById('analytics-departments').textContent = data.departments || 0;
            document.getElementById('analytics-batches').textContent = data.batches || 0;
            document.getElementById('analytics-sections').textContent = data.sections || 0;
            document.getElementById('analytics-feedback').textContent = data.feedback || 0;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// User Management
async function loadUsers() {
    try {
        const res = await fetch('/api/admin/users', {
            credentials: 'include'
        });
        const data = await res.json();
        const allUsers = data.users || [];
        const users = allUsers.filter(u => u.role !== 'teacher');
        
        const tbody = document.getElementById('usersTableBody');
        tbody.innerHTML = '';
        
        if (users.length > 0) {
            users.forEach(user => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${user.id}</td>
                    <td>${user.username}</td>
                    <td>${user.name}</td>
                    <td>${user.email || 'N/A'}</td>
                    <td><span class="badge badge-info">${user.role}</span></td>
                    <td><span class="badge ${user.is_active ? 'badge-success' : 'badge-danger'}">${user.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td>${user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}</td>
                    <td class="action-buttons">
                        <button class="btn-admin btn-small btn-warning-admin" onclick="editUser(${user.id})">✏️ Edit</button>
                        <button class="btn-admin btn-small btn-danger-admin" onclick="deleteUser(${user.id})">🗑️ Delete</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 2rem;">No users found</td></tr>';
        }
    } catch (error) {
        console.error('Error loading users:', error);
        showMessage('Error loading users: ' + error.message, true);
    }
}

async function createUser() {
    const name = document.getElementById('new-name').value.trim();
    const email = document.getElementById('new-email').value.trim();
    const role = document.getElementById('new-role').value;
    
    // Validate required fields (only Name, Email, Role - no password)
    if (!name || !email || !role) {
        showMessage('Please fill all required fields (Name, Email, Role)!', true);
        return;
    }
    
    // Basic email validation
    if (!email.includes('@') || !email.includes('.')) {
        showMessage('Please enter a valid email address!', true);
        return;
    }
    
    try {
        const res = await fetch('/admin/add-user', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, role })
        });
        
        const data = await res.json();
        
        if (data.success) {
            // Display success message with the generated password
            const password = data.temporary_password || 'Not available';
            const emailStatus = data.email_sent ? 'Email sent successfully.' : 'Email failed to send.';
            
            // Show alert with password
            alert(`User created! Temporary Password: ${password}\n\n${emailStatus}\n\nPlease copy this password and share it with the user if email failed.`);
            
            // Also show in the message system
            showMessage(`✅ User created successfully! Temporary Password: ${password}`, false);
            
            // Clear form fields
            document.getElementById('new-name').value = '';
            document.getElementById('new-email').value = '';
            document.getElementById('new-role').value = 'admin'; // Reset to default
            
            // Reload users list and stats
            loadUsers();
            loadStats();
        } else {
            showMessage(data.message || 'Error creating user', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

async function deleteUser(userId) {
    console.log('Deleting user:', userId);
    if (!confirm('Are you sure you want to delete this user?')) return;
    
    try {
        const res = await fetch(`/api/admin/users/${userId}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' }
        });
        
        console.log('Response status:', res.status);
        
        const data = await res.json();
        console.log('Response data:', data);
        
        if (data.success) {
            showMessage('User deleted!');
            loadUsers();
            loadStats();
        } else {
            showMessage(
                data.message || 'Error!', true);
        }
    } catch (error) {
        console.log('Error:', error);
        showMessage('Error: ' + error.message, true);
    }
}

async function editUser(userId) {
    try {
        // Try to fetch single user first
        let res = await fetch(`/api/admin/users/${userId}`, {
            credentials: 'include'
        });

        let userData = null;
        if (res.ok) {
            const obj = await res.json();
            userData = obj.user || obj;
        } else {
            // Fallback to fetching all users and finding the one we need
            res = await fetch('/api/admin/users', { credentials: 'include' });
            const list = await res.json();
            const users = list.users || [];
            userData = users.find(u => parseInt(u.id) === parseInt(userId));
        }

        if (!userData) {
            showMessage('User not found', true);
            return;
        }

        // If an edit form exists in the page, try to fill it; otherwise use prompts
        const formNameEl = document.getElementById('edit-user-name');
        if (formNameEl) {
            document.getElementById('edit-user-id').value = userData.id;
            document.getElementById('edit-user-name').value = userData.name || '';
            document.getElementById('edit-user-email').value = userData.email || '';
            const roleEl = document.getElementById('edit-user-role');
            if (roleEl) roleEl.value = userData.role || '';
            // Assume there's a save button wired to submitEditUser()
            return;
        }

        const newName = prompt('Edit full name:', userData.name || '');
        if (newName === null) return; // cancelled
        const newEmail = prompt('Edit email:', userData.email || '');
        if (newEmail === null) return;
        const newRole = prompt('Edit role (admin / batch advisor):', userData.role || 'admin');
        if (newRole === null) return;

        const putRes = await fetch(`/api/admin/users/${userId}`, {
            method: 'PUT',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: newName.trim(), email: newEmail.trim(), role: newRole.trim() })
        });

        const putData = await putRes.json();
        if (putData.success) {
            showMessage('✅ User updated successfully!');
            loadUsers();
            loadStats();
        } else {
            showMessage(putData.message || 'Error updating user', true);
        }
    } catch (error) {
        console.error('Edit user error:', error);
        showMessage('Error: ' + error.message, true);
    }
}

// Course Management
async function loadCourses() {
    try {
        const res = await fetch('/api/admin/courses', {
            credentials: 'include'
        });
        const data = await res.json();
        
        const tbody = document.getElementById('coursesTableBody');
        const assignSelect = document.getElementById('assign-course');
        
        tbody.innerHTML = '';
        assignSelect.innerHTML = '<option value="">-- Select Course --</option>';
        
        if (data.courses && data.courses.length > 0) {
            data.courses.forEach(course => {
                // Table row
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${course.id}</td>
                    <td><strong>${course.code}</strong></td>
                    <td>${course.name}</td>
                    <td>${course.department || 'N/A'}</td>
                    <td>${course.credit_hours || 3}</td>
                    <td><span class="badge ${course.is_active ? 'badge-success' : 'badge-danger'}">${course.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td class="action-buttons">
                        <button class="btn-admin btn-small btn-warning-admin" onclick="editCourse(${course.id})">✏️ Edit</button>
                        <button class="btn-admin btn-small btn-danger-admin" onclick="deleteCourse(${course.id})">🗑️ Delete</button>
                    </td>
                `;
                tbody.appendChild(row);
                
                // Dropdown option
                const option = document.createElement('option');
                option.value = course.id;
                option.textContent = `${course.code} - ${course.name}`;
                assignSelect.appendChild(option);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2rem;">No courses found. Click "Add Course" to create one.</td></tr>';
        }
    } catch (error) {
        console.error('Error loading courses:', error);
        showMessage('Error loading courses: ' + error.message, true);
    }
}

async function loadDepartmentsForCourse() {
    try {
        const res = await fetch('/api/admin/departments', {
            credentials: 'include'
        });
        const data = await res.json();
        
        const select = document.getElementById('course-department');
        if (select) {
            // Keep the first option (-- Select Department --)
            const firstOption = select.querySelector('option[value=""]');
            select.innerHTML = '';
            if (firstOption) {
                select.appendChild(firstOption);
            } else {
                select.innerHTML = '<option value="">-- Select Department (Optional) --</option>';
            }
            
            if (data.departments && data.departments.length > 0) {
                data.departments.forEach(dept => {
                    if (dept.is_active) {
                        const option = document.createElement('option');
                        option.value = dept.name;  // Send department name to backend
                        option.textContent = `${dept.code} - ${dept.name}`;
                        select.appendChild(option);
                    }
                });
            }
        }
    } catch (error) {
        console.error('Error loading departments for course:', error);
    }
}

async function createCourse() {
    const code = document.getElementById('course-code').value.trim();
    const name = document.getElementById('course-name').value.trim();
    const department = document.getElementById('course-department').value.trim();
    const credit_hours = document.getElementById('course-credit-hours').value.trim();
    const description = document.getElementById('course-description').value.trim();
    
    if (!code || !name) {
        showMessage('Please fill Course Code and Name!', true);
        return;
    }
    
    try {
        const res = await fetch('/api/admin/courses', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, name, department, credit_hours, description })
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Course created successfully!');
            document.getElementById('course-code').value = '';
            document.getElementById('course-name').value = '';
            document.getElementById('course-department').value = '';
            document.getElementById('course-credit-hours').value = '3';
            document.getElementById('course-description').value = '';
            loadCourses();
        } else {
            showMessage(data.message || 'Error creating course', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

async function deleteCourse(courseId) {
    if (!courseId) {
        showMessage('❌ Invalid course ID!', true);
        return;
    }
    
    if (!confirm(`Are you sure you want to delete this course? This will also remove all related records (batch assignments, student registrations, etc.).`)) {
        return;
    }
    
    try {
        const res = await fetch(`/api/admin/courses/${courseId}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!res.ok) {
            const errorText = await res.text();
            throw new Error(`HTTP ${res.status}: ${errorText}`);
        }
        
        const data = await res.json();
        
        if (data.success) {
            showMessage(data.message || '✅ Course deleted successfully!');
            loadCourses();
        } else {
            showMessage(data.message || '❌ Error deleting course', true);
        }
    } catch (error) {
        console.error('Delete course error:', error);
        showMessage('❌ Error deleting course: ' + error.message, true);
    }
}

// Teacher Management
async function loadTeachers() {
    try {
        const res = await fetch('/api/admin/teachers', {
            credentials: 'include'
        });
        const data = await res.json();
        
        const tbody = document.getElementById('teachersTableBody');
        const assignSelect = document.getElementById('assign-teacher');
        
        tbody.innerHTML = '';
        assignSelect.innerHTML = '<option value="">-- Select Teacher --</option>';
        
        if (data.teachers && data.teachers.length > 0) {
            data.teachers.forEach(teacher => {
                // Table row
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${teacher.id}</td>
                    <td>${teacher.name}</td>
                    <td>${teacher.email || 'N/A'}</td>
                    <td>${teacher.employee_id || 'N/A'}</td>
                    <td>${teacher.department || 'N/A'}</td>
                    <td>${teacher.designation || 'N/A'}</td>
                    <td><span class="badge ${teacher.is_active ? 'badge-success' : 'badge-danger'}">${teacher.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td class="action-buttons">
                        <button class="btn-admin btn-small btn-warning-admin" onclick="editTeacher(${teacher.id})">✏️ Edit</button>
                        <button class="btn-admin btn-small btn-danger-admin" onclick="deleteTeacher(${teacher.id})">🗑️ Delete</button>
                    </td>
                `;
                tbody.appendChild(row);
                
                // Dropdown option
                const option = document.createElement('option');
                option.value = teacher.id;
                option.textContent = teacher.name;
                assignSelect.appendChild(option);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 2rem;">No teachers found</td></tr>';
        }
    } catch (error) {
        console.error('Error loading teachers:', error);
        showMessage('Error loading teachers: ' + error.message, true);
    }
}

async function createTeacher() {
    const name = document.getElementById('teacher-name').value.trim();
    const email = document.getElementById('teacher-email').value.trim();
    const department_id = document.getElementById('teacher-department').value;
    const designation = document.getElementById('teacher-designation').value;
    
    if (!name) {
        showMessage('Please fill Teacher Name!', true);
        return;
    }
    
    try {
        const res = await fetch('/api/admin/teachers', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                email,
                department_id: department_id ? parseInt(department_id) : null,
                designation
            })
        });
        
        const data = await res.json();
        
        if (data.success) {
            let msg = '✅ Teacher added successfully!';
            if (data.auto_password) {
                msg += `\n\n🔑 Password: ${data.auto_password}`;
                msg += `\n👤 Employee ID: ${data.employee_id}`;
                if (data.email_sent) {
                    msg += '\n📧 Credentials email sent!';
                }
                alert(msg);
            }
            showMessage('✅ Teacher created successfully!');
            document.getElementById('teacher-name').value = '';
            document.getElementById('teacher-email').value = '';
            document.getElementById('teacher-department').value = '';
            loadTeachers();
            loadStats();
        } else {
            showMessage(data.message || 'Error creating teacher', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

async function deleteTeacher(teacherId) {
    if (!confirm('Are you sure you want to delete this teacher?')) return;
    
    try {
        const res = await fetch(`/api/admin/teachers/${teacherId}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Teacher deleted successfully!');
            loadTeachers();
            loadStats();
        } else {
            showMessage(data.message || 'Error deleting teacher', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

async function editTeacher(teacherId) {
    try {
        // Try fetching single teacher
        let res = await fetch(`/api/admin/teachers/${teacherId}`, { credentials: 'include' });
        let teacher = null;
        if (res.ok) {
            const obj = await res.json();
            teacher = obj.teacher || obj;
        } else {
            // fallback to list
            res = await fetch('/api/admin/teachers', { credentials: 'include' });
            const list = await res.json();
            teacher = (list.teachers || []).find(t => parseInt(t.id) === parseInt(teacherId));
        }

        if (!teacher) {
            showMessage('Teacher not found', true);
            return;
        }

        const name = prompt('Teacher name:', teacher.name || '');
        if (name === null) return;
        const email = prompt('Teacher email:', teacher.email || '');
        if (email === null) return;
        const department = prompt('Department:', teacher.department || '');
        if (department === null) return;
        const designation = prompt('Designation:', teacher.designation || '');
        if (designation === null) return;

        const putRes = await fetch(`/api/admin/teachers/${teacherId}`, {
            method: 'PUT',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name.trim(), email: email.trim(), department: department.trim(), designation: designation.trim() })
        });

        const putData = await putRes.json();
        if (putData.success) {
            showMessage('✅ Teacher updated successfully!');
            loadTeachers();
        } else {
            showMessage(putData.message || 'Error updating teacher', true);
        }
    } catch (error) {
        console.error('Edit teacher error:', error);
        showMessage('Error: ' + error.message, true);
    }
}

async function assignCourseTeacher() {
    const courseId = document.getElementById('assign-course').value;
    const teacherId = document.getElementById('assign-teacher').value;
    const section = document.getElementById('assign-section').value.trim();
    
    if (!courseId || !teacherId) {
        showMessage('Please select both Course and Teacher!', true);
        return;
    }
    
    try {
        const res = await fetch('/api/admin/course-teachers', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ course_id: parseInt(courseId), teacher_id: parseInt(teacherId), section })
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Teacher assigned to course successfully!');
            document.getElementById('assign-course').value = '';
            document.getElementById('assign-teacher').value = '';
            document.getElementById('assign-section').value = '';
        } else {
            showMessage(data.message || 'Error assigning teacher', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

// Feedback Management
async function loadFeedback() {
    try {
        const filter = document.getElementById('feedback-filter')?.value || 'all';
        const res = await fetch(`/api/admin/feedback?status=${filter}`, {
            credentials: 'include'
        });
        const data = await res.json();
        
        const tbody = document.getElementById('feedbackTableBody');
        tbody.innerHTML = '';
        
        if (data.feedback && data.feedback.length > 0) {
            data.feedback.forEach(fb => {
                const statusBadge = fb.status === 'approved' ? 'badge-success' : 
                                   fb.status === 'rejected' ? 'badge-danger' : 'badge-warning';
                const statusText = fb.status === 'approved' ? 'Approved' : 
                                  fb.status === 'rejected' ? 'Rejected' : 'Pending';
                
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${fb.id}</td>
                    <td>${fb.student_name} (${fb.registration_number})</td>
                    <td>${fb.course ? fb.course.code : 'N/A'}</td>
                    <td>${fb.teacher ? fb.teacher.name : 'N/A'}</td>
                    <td>${fb.sentiment}</td>
                    <td>${fb.rating_overall ? '⭐'.repeat(fb.rating_overall) : 'N/A'}</td>
                    <td><span class="badge ${statusBadge}">${statusText}</span></td>
                    <td>${new Date(fb.created_at).toLocaleDateString()}</td>
                    <td class="action-buttons">
                        <button class="btn-admin btn-small btn-success-admin" onclick="approveFeedback(${fb.id})">✅ Approve</button>
                        <button class="btn-admin btn-small btn-danger-admin" onclick="rejectFeedback(${fb.id})">❌ Reject</button>
                        <button class="btn-admin btn-small btn-info-admin" onclick="viewFeedback(${fb.id})">👁️ View</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; padding: 2rem;">No feedback found</td></tr>';
        }
    } catch (error) {
        console.error('Error loading feedback:', error);
        showMessage('Error loading feedback: ' + error.message, true);
    }
}

async function approveFeedback(feedbackId) {
    try {
        const res = await fetch(`/api/admin/feedback/${feedbackId}/approve`, {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Feedback approved successfully!');
            loadFeedback();
            loadStats();
        } else {
            showMessage(data.message || 'Error approving feedback', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

async function rejectFeedback(feedbackId) {
    if (!confirm('Are you sure you want to reject this feedback?')) return;
    
    try {
        const res = await fetch(`/api/admin/feedback/${feedbackId}/reject`, {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Feedback rejected!');
            loadFeedback();
            loadStats();
        } else {
            showMessage(data.message || 'Error rejecting feedback', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

function viewFeedback(feedbackId) {
    // Open feedback details in modal or new page
    window.location.href = `/api/admin/feedback/${feedbackId}`;
}

// SMTP Configuration
async function loadSMTPConfig() {
    try {
        const res = await fetch('/api/admin/smtp-config', {
            credentials: 'include'
        });
        const data = await res.json();
        
        if (data.config) {
            document.getElementById('smtp-server').value = data.config.server || 'smtp.gmail.com';
            document.getElementById('smtp-port').value = data.config.port || 587;
            document.getElementById('smtp-tls').checked = data.config.use_tls !== false;
            document.getElementById('smtp-email').value = data.config.email || '';
            // Don't load password for security
        }
    } catch (error) {
        console.error('Error loading SMTP config:', error);
    }
}

async function saveSMTPConfig() {
    const server = document.getElementById('smtp-server').value.trim();
    const port = parseInt(document.getElementById('smtp-port').value);
    const use_tls = document.getElementById('smtp-tls').checked;
    const email = document.getElementById('smtp-email').value.trim();
    const password = document.getElementById('smtp-password').value.trim();
    
    if (!server || !port || !email || !password) {
        showMessage('Please fill all required fields!', true);
        return;
    }
    
    try {
        const res = await fetch('/api/admin/smtp-config', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ server, port, use_tls, email, password })
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ SMTP configuration saved successfully!');
            document.getElementById('smtp-password').value = '';
        } else {
            showMessage(data.message || 'Error saving SMTP config', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

async function testSMTP() {
    const email = document.getElementById('test-email').value.trim();
    
    if (!email) {
        showMessage('Please enter test email address!', true);
        return;
    }
    
    try {
        const res = await fetch('/api/admin/test-smtp', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Test email sent successfully! Check your inbox.');
        } else {
            showMessage(data.message || 'Error sending test email', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

// Email Settings
async function loadEmailSettings() {
    try {
        const res = await fetch('/api/admin/email-settings', {
            credentials: 'include'
        });
        const data = await res.json();
        
        if (data.settings) {
            document.getElementById('email-new-feedback').checked = data.settings.notify_new_feedback !== false;
            document.getElementById('email-daily-summary').checked = data.settings.daily_summary || false;
            document.getElementById('email-weekly-report').checked = data.settings.weekly_report || false;
            document.getElementById('email-feedback-approved').checked = data.settings.notify_approved || false;
            document.getElementById('default-teacher-email').value = data.settings.default_teacher_email || '';
            document.getElementById('email-subject-prefix').value = data.settings.subject_prefix || '[TechAware]';
            document.getElementById('reply-to-email').value = data.settings.reply_to || '';
        }
    } catch (error) {
        console.error('Error loading email settings:', error);
    }
}

async function saveEmailSettings() {
    const settings = {
        notify_new_feedback: document.getElementById('email-new-feedback').checked,
        daily_summary: document.getElementById('email-daily-summary').checked,
        weekly_report: document.getElementById('email-weekly-report').checked,
        notify_approved: document.getElementById('email-feedback-approved').checked,
        default_teacher_email: document.getElementById('default-teacher-email').value.trim(),
        subject_prefix: document.getElementById('email-subject-prefix').value.trim(),
        reply_to: document.getElementById('reply-to-email').value.trim()
    };
    
    try {
        const res = await fetch('/api/admin/email-settings', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Email settings saved successfully!');
        } else {
            showMessage(data.message || 'Error saving email settings', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

// Database Management
async function loadDatabaseStats() {
    try {
        const res = await fetch('/api/admin/database/stats', {
            credentials: 'include'
        });
        const data = await res.json();
        
        const statsDiv = document.getElementById('dbStats');
        const modelsBody = document.getElementById('modelsTableBody');
        
        if (data.stats) {
            statsDiv.innerHTML = `
                <p><strong>Database Type:</strong> ${data.stats.database_type || 'SQLite'}</p>
                <p><strong>Total Tables:</strong> ${data.stats.total_tables || 0}</p>
                <p><strong>Database Size:</strong> ${data.stats.database_size || 'N/A'}</p>
                <p><strong>Last Backup:</strong> ${data.stats.last_backup || 'Never'}</p>
            `;
            
            if (data.models) {
                modelsBody.innerHTML = '';
                data.models.forEach(model => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${model.name}</td>
                        <td>${model.table}</td>
                        <td>${model.count}</td>
                        <td>${model.description}</td>
                    `;
                    modelsBody.appendChild(row);
                });
            }
        }
    } catch (error) {
        console.error('Error loading database stats:', error);
    }
}

async function backupDatabase() {
    if (!confirm('Create a backup of the database?')) return;
    
    try {
        const res = await fetch('/api/admin/database/backup', {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Database backup created successfully!');
        } else {
            showMessage(data.message || 'Error creating backup', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

async function optimizeDatabase() {
    if (!confirm('Optimize database? This may take a few moments.')) return;
    
    try {
        const res = await fetch('/api/admin/database/optimize', {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Database optimized successfully!');
        } else {
            showMessage(data.message || 'Error optimizing database', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

async function resetDatabase() {
    if (!confirm('⚠️ WARNING: This will delete ALL data! Type "RESET" to confirm.')) return;
    
    const confirmText = prompt('Type "RESET" to confirm database reset:');
    if (confirmText !== 'RESET') {
        showMessage('Database reset cancelled.', true);
        return;
    }
    
    try {
        const res = await fetch('/api/admin/database/reset', {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Database reset successfully!');
            setTimeout(() => location.reload(), 2000);
        } else {
            showMessage(data.message || 'Error resetting database', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

// System Settings
async function loadSystemSettings() {
    try {
        const res = await fetch('/api/admin/system-settings', {
            credentials: 'include'
        });
        const data = await res.json();
        
        if (data.settings) {
            document.getElementById('system-name').value = data.settings.system_name || 'TechAware Feedback System';
            document.getElementById('require-approval').checked = data.settings.require_approval || false;
            document.getElementById('allow-anonymous').checked = data.settings.allow_anonymous !== false;
            document.getElementById('enable-ai').checked = data.settings.enable_ai !== false;
            document.getElementById('ai-threshold').value = data.settings.ai_threshold || 0.5;
        }
    } catch (error) {
        console.error('Error loading system settings:', error);
    }
}

async function saveSystemSettings() {
    const settings = {
        system_name: document.getElementById('system-name').value.trim(),
        require_approval: document.getElementById('require-approval').checked,
        allow_anonymous: document.getElementById('allow-anonymous').checked,
        enable_ai: document.getElementById('enable-ai').checked,
        ai_threshold: parseFloat(document.getElementById('ai-threshold').value)
    };
    
    try {
        const res = await fetch('/api/admin/system-settings', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ System settings saved successfully!');
        } else {
            showMessage(data.message || 'Error saving system settings', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

// ========== DEPARTMENT MANAGEMENT ==========
async function loadDepartments() {
    try {
        const res = await fetch('/api/admin/departments', {
            credentials: 'include'
        });
        const data = await res.json();
        
        const tbody = document.getElementById('departmentsTableBody');
        if (!tbody) return;
        tbody.innerHTML = '';
        
        if (data.departments && data.departments.length > 0) {
            data.departments.forEach(dept => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${dept.id}</td>
                    <td>${dept.code}</td>
                    <td>${dept.name}</td>
                    <td>${dept.description || 'N/A'}</td>
                    <td>${dept.batch_count || 0}</td>
                    <td><span class="badge ${dept.is_active ? 'badge-success' : 'badge-danger'}">${dept.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td class="action-buttons">
                        <button class="btn-admin btn-small btn-warning-admin" onclick="editDepartment(${dept.id}, ${JSON.stringify(dept.code)}, ${JSON.stringify(dept.name)}, ${JSON.stringify(dept.description || '')})">✏️ Edit</button>
                        <button class="btn-admin btn-small btn-warning-admin" onclick="deleteDepartment(${dept.id})">🗑️ Delete</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2rem;">No departments found</td></tr>';
        }
    } catch (error) {
        console.error('Error loading departments:', error);
    }
}

async function createDepartment() {
    const code = document.getElementById('dept-code').value.trim().toUpperCase();
    const name = document.getElementById('dept-name').value.trim();
    const description = document.getElementById('dept-description').value.trim();
    
    if (!code || !name) {
        showMessage('Please fill Department Code and Name!', true);
        return;
    }
    
    try {
        const res = await fetch('/api/admin/departments', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, name, description })
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Department created successfully!');
            document.getElementById('dept-code').value = '';
            document.getElementById('dept-name').value = '';
            document.getElementById('dept-description').value = '';
            loadDepartments();
        } else {
            showMessage(data.message || 'Error creating department', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

async function deleteDepartment(deptId) {
    if (!confirm('Are you sure you want to delete this department? This will also delete all associated batches and sections.')) return;
    
    try {
        const res = await fetch(`/api/admin/departments/${deptId}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Department deleted successfully!');
            loadDepartments();
        } else {
            showMessage(data.message || 'Error deleting department', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

async function editDepartment(
    deptId, code, name, description) {
    const newCode = prompt('Code:', code);
    if (newCode === null) return;
    const newName = prompt('Name:', name);
    if (newName === null) return;
    const newDesc = prompt('Description:',
        description);

    const res = await fetch(
        `/api/admin/departments/${deptId}`, {
        method: 'PUT',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            code: newCode.trim().toUpperCase(),
            name: newName.trim(),
            description: newDesc || ''
        })
    });

    const data = await res.json();
    if (data.success) {
        showMessage('Department updated!');
        loadDepartments();
    } else {
        showMessage(data.message || 'Error!', true);
    }
}

// ========== BATCH MANAGEMENT ==========
async function loadDepartmentsForBatches() {
    try {
        const res = await fetch('/api/admin/departments', {
            credentials: 'include'
        });
        const data = await res.json();
        
        const select1 = document.getElementById('batch-dept-id');
        const select2 = document.getElementById('filter-batch-dept');
        
        [select1, select2].forEach(select => {
            if (select) {
                select.innerHTML = '<option value="">-- Select Department --</option>';
                if (data.departments) {
                    data.departments.forEach(dept => {
                        const option = document.createElement('option');
                        option.value = dept.id;
                        option.textContent = `${dept.code} - ${dept.name}`;
                        select.appendChild(option);
                    });
                }
            }
        });
    } catch (error) {
        console.error('Error loading departments:', error);
    }
}

async function loadBatches() {
    try {
        const deptId = document.getElementById('filter-batch-dept')?.value || '';
        const url = deptId ? `/api/admin/batches?department_id=${deptId}` : '/api/admin/batches';
        const res = await fetch(url, {
            credentials: 'include'
        });
        const data = await res.json();
        
        const tbody = document.getElementById('batchesTableBody');
        tbody.innerHTML = '';
        
        if (data.batches && data.batches.length > 0) {
            data.batches.forEach(batch => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${batch.id}</td>
                    <td>${batch.department ? batch.department.code : 'N/A'}</td>
                    <td>${batch.name}</td>
                    <td>${batch.year}</td>
                    <td>${batch.semester}</td>
                    <td>${batch.section_count || 0}</td>
                    <td>${batch.start_date || 'N/A'}</td>
                    <td>${batch.end_date || 'N/A'}</td>
                    <td><span class="badge ${batch.is_active ? 'badge-success' : 'badge-danger'}">${batch.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td class="action-buttons">
                        <button class="btn-admin btn-small btn-warning-admin" onclick="editBatch(${batch.id}, ${JSON.stringify(batch.name)}, ${JSON.stringify(batch.year)}, ${JSON.stringify(batch.semester)}, ${JSON.stringify(batch.start_date || '')}, ${JSON.stringify(batch.end_date || '')})">✏️ Edit</button>
                        <button class="btn-admin btn-small btn-danger-admin" onclick="deleteBatch(${batch.id})">🗑️ Delete</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; padding: 2rem;">No batches found</td></tr>';
        }
    } catch (error) {
        console.error('Error loading batches:', error);
        showMessage('Error loading batches: ' + error.message, true);
    }
}

async function createBatch() {
    const department_id = document.getElementById('batch-dept-id').value;
    const name = document.getElementById('batch-name').value.trim();
    const year = parseInt(document.getElementById('batch-year').value);
    const semester = document.getElementById('batch-semester').value;
    const start_date = document.getElementById('batch-start-date').value;
    const end_date = document.getElementById('batch-end-date').value;
    
    if (!department_id || !name || !year || !semester) {
        showMessage('Please fill all required fields!', true);
        return;
    }
    
    try {
        const res = await fetch('/api/admin/batches', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ department_id: parseInt(department_id), name, year, semester, start_date, end_date })
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Batch created successfully!');
            document.getElementById('batch-dept-id').value = '';
            document.getElementById('batch-name').value = '';
            document.getElementById('batch-year').value = '';
            document.getElementById('batch-start-date').value = '';
            document.getElementById('batch-end-date').value = '';
            loadBatches();
        } else {
            showMessage(data.message || 'Error creating batch', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

async function deleteBatch(batchId) {
    if (!confirm('Are you sure you want to delete this batch? This will also delete all associated sections.')) return;
    
    try {
        const res = await fetch(`/api/admin/batches/${batchId}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Batch deleted successfully!');
            loadBatches();
        } else {
            showMessage(data.message || 'Error deleting batch', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

async function editBatch(
    batchId, name, year, semester,
    startDate, endDate) {
    const newName = prompt('Name:', name);
    if (newName === null) return;
    const newYear = prompt('Year:', year);
    if (newYear === null) return;
    const newSemester = prompt('Semester:', semester);
    if (newSemester === null) return;
    const newStartDate = prompt('Start Date (YYYY-MM-DD):', startDate || '');
    if (newStartDate === null) return;
    const newEndDate = prompt('End Date (YYYY-MM-DD):', endDate || '');
    if (newEndDate === null) return;

    const res = await fetch(`/api/admin/batches/${batchId}`, {
        method: 'PUT',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: newName.trim(),
            year: parseInt(newYear, 10) || year,
            semester: newSemester.trim(),
            start_date: newStartDate.trim(),
            end_date: newEndDate.trim()
        })
    });

    const data = await res.json();
    if (data.success) {
        showMessage('Batch updated!');
        loadBatches();
    } else {
        showMessage(data.message || 'Error!', true);
    }
}

// ========== SECTION MANAGEMENT ==========
async function loadDepartmentsForSections() {
    try {
        const res = await fetch('/api/admin/departments', {
            credentials: 'include'
        });
        const data = await res.json();
        
        const select1 = document.getElementById('section-dept-id');
        const select2 = document.getElementById('filter-section-dept');
        
        [select1, select2].forEach(select => {
            if (select) {
                select.innerHTML = '<option value="">-- Select Department --</option>';
                if (data.departments) {
                    data.departments.forEach(dept => {
                        const option = document.createElement('option');
                        option.value = dept.id;
                        option.textContent = `${dept.code} - ${dept.name}`;
                        select.appendChild(option);
                    });
                }
            }
        });
    } catch (error) {
        console.error('Error loading departments:', error);
    }
}

async function loadBatchesForSection() {
    const deptId = document.getElementById('section-dept-id').value;
    if (!deptId) {
        document.getElementById('section-batch-id').innerHTML = '<option value="">-- Select Batch --</option>';
        return;
    }
    
    try {
        const res = await fetch(`/api/admin/batches?department_id=${deptId}`, {
            credentials: 'include'
        });
        const data = await res.json();
        
        const select = document.getElementById('section-batch-id');
        select.innerHTML = '<option value="">-- Select Batch --</option>';
        
        if (data.batches) {
            data.batches.forEach(batch => {
                const option = document.createElement('option');
                option.value = batch.id;
                option.textContent = batch.name;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading batches:', error);
    }
}

async function loadBatchesForSectionFilter() {
    const deptId = document.getElementById('filter-section-dept')?.value || '';
    if (!deptId) {
        document.getElementById('filter-section-batch').innerHTML = '<option value="">All Batches</option>';
        return;
    }
    
    try {
        const res = await fetch(`/api/admin/batches?department_id=${deptId}`, {
            credentials: 'include'
        });
        const data = await res.json();
        
        const select = document.getElementById('filter-section-batch');
        select.innerHTML = '<option value="">All Batches</option>';
        
        if (data.batches) {
            data.batches.forEach(batch => {
                const option = document.createElement('option');
                option.value = batch.id;
                option.textContent = batch.name;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading batches:', error);
    }
}

async function loadSections() {
    try {
        const deptId = document.getElementById('filter-section-dept')?.value || '';
        const batchId = document.getElementById('filter-section-batch')?.value || '';
        
        let url = '/api/admin/sections';
        const params = [];
        if (deptId) params.push(`department_id=${deptId}`);
        if (batchId) params.push(`batch_id=${batchId}`);
        if (params.length > 0) url += '?' + params.join('&');
        
        const res = await fetch(url, {
            credentials: 'include'
        });
        const data = await res.json();
        
        const tbody = document.getElementById('sectionsTableBody');
        if (!tbody) return;
        tbody.innerHTML = '';
        
        if (data.sections && data.sections.length > 0) {
            data.sections.forEach(section => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${section.id}</td>
                    <td>${section.batch?.department?.code || 'N/A'}</td>
                    <td>${section.batch?.name || 'N/A'}</td>
                    <td>${section.name}</td>
                    <td>${section.capacity}</td>
                    <td>${section.current_students || 0}</td>
                    <td><span class="badge ${section.is_active ? 'badge-success' : 'badge-danger'}">${section.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td class="action-buttons">
                        <button class="btn-admin btn-small btn-warning-admin" onclick="editSection(${section.id}, ${JSON.stringify(section.name)}, ${JSON.stringify(section.capacity)})">✏️ Edit</button>
                        <button class="btn-admin btn-small btn-danger-admin" onclick="deleteSection(${section.id})">🗑️ Delete</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 2rem;">No sections found</td></tr>';
        }
    } catch (error) {
        console.error('Error loading sections:', error);
    }
}

async function createSection() {
    const batch_id = document.getElementById('section-batch-id').value;
    const name = document.getElementById('section-name').value.trim().toUpperCase();
    const capacity = parseInt(document.getElementById('section-capacity').value) || 50;
    
    if (!batch_id || !name) {
        showMessage('Please select Batch and enter Section Name!', true);
        return;
    }
    
    try {
        const res = await fetch('/api/admin/sections', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ batch_id: parseInt(batch_id), name, capacity })
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Section created successfully!');
            document.getElementById('section-dept-id').value = '';
            document.getElementById('section-batch-id').value = '';
            document.getElementById('section-name').value = '';
            document.getElementById('section-capacity').value = '50';
            loadSections();
        } else {
            showMessage(data.message || 'Error creating section', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

async function deleteSection(sectionId) {
    if (!confirm('Are you sure you want to delete this section?')) return;
    
    try {
        const res = await fetch(`/api/admin/sections/${sectionId}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Section deleted successfully!');
            loadSections();
        } else {
            showMessage(data.message || 'Error deleting section', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

async function editSection(
    sectionId, name, capacity) {
    const newName = prompt('Name:', name);
    if (newName === null) return;
    const newCapacity = prompt('Capacity:', capacity);
    if (newCapacity === null) return;

    const res = await fetch(`/api/admin/sections/${sectionId}`, {
        method: 'PUT',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: newName.trim().toUpperCase(),
            capacity: parseInt(newCapacity, 10) || capacity
        })
    });

    const data = await res.json();
    if (data.success) {
        showMessage('Section updated!');
        loadSections();
    } else {
        showMessage(data.message || 'Error!', true);
    }
}

async function showSectionCounts() {
    try {
        const res = await fetch('/api/admin/departments', {
            credentials: 'include'
        });
        const data = await res.json();
        
        if (!data.departments || data.departments.length === 0) {
            showMessage('No departments found', true);
            return;
        }
        
        let message = '📊 Section Counts by Department:\n\n';
        for (const dept of data.departments) {
            const countRes = await fetch(`/api/admin/departments/${dept.id}/section-count`, {
                credentials: 'include'
            });
            const countData = await countRes.json();
            
            if (countData.success) {
                message += `${dept.code} - ${dept.name}: ${countData.total_sections} total sections\n`;
                if (countData.sections_by_batch) {
                    Object.entries(countData.sections_by_batch).forEach(([batch, count]) => {
                        message += `  └─ ${batch}: ${count} sections\n`;
                    });
                }
            }
        }
        
        alert(message);
    } catch (error) {
        showMessage('Error loading section counts: ' + error.message, true);
    }
}

// ========== BATCH-SUBJECT ASSIGNMENT ==========
async function loadDepartmentsForBatchSubjects() {
    try {
        const res = await fetch('/api/admin/departments', {
            credentials: 'include'
        });
        const data = await res.json();
        
        const select = document.getElementById('bs-dept-id');
        if (select) {
            select.innerHTML = '<option value="">-- Select Department --</option>';
            if (data.departments) {
                data.departments.forEach(dept => {
                    const option = document.createElement('option');
                    option.value = dept.id;
                    option.textContent = `${dept.code} - ${dept.name}`;
                    select.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('Error loading departments:', error);
    }
}

async function loadBatchesForBatchSubject() {
    const deptId = document.getElementById('bs-dept-id').value;
    if (!deptId) {
        document.getElementById('bs-batch-id').innerHTML = '<option value="">-- Select Batch --</option>';
        return;
    }
    
    try {
        const res = await fetch(`/api/admin/batches?department_id=${deptId}`, {
            credentials: 'include'
        });
        const data = await res.json();
        
        const select1 = document.getElementById('bs-batch-id');
        const select2 = document.getElementById('filter-bs-batch');
        
        [select1, select2].forEach(select => {
            if (select) {
                select.innerHTML = '<option value="">-- Select Batch --</option>';
                if (data.batches) {
                    data.batches.forEach(batch => {
                        const option = document.createElement('option');
                        option.value = batch.id;
                        option.textContent = batch.name;
                        select.appendChild(option);
                    });
                }
            }
        });
    } catch (error) {
        console.error('Error loading batches:', error);
    }
}

async function loadCoursesForBatchSubject() {
    try {
        const res = await fetch('/api/admin/courses', {
            credentials: 'include'
        });
        const data = await res.json();
        
        const select = document.getElementById('bs-course-id');
        if (select) {
            select.innerHTML = '<option value="">-- Select Course --</option>';
            if (data.courses) {
                data.courses.forEach(course => {
                    const option = document.createElement('option');
                    option.value = course.id;
                    option.textContent = `${course.code} - ${course.name}`;
                    select.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('Error loading courses:', error);
    }
}

async function loadBatchSubjects() {
    try {
        const batchId = document.getElementById('filter-bs-batch')?.value || document.getElementById('bs-batch-id')?.value || '';
        const url = batchId ? `/api/admin/batch-subjects?batch_id=${batchId}` : '/api/admin/batch-subjects';
        const res = await fetch(url, {
            credentials: 'include'
        });
        const data = await res.json();
        
        const tbody = document.getElementById('batchSubjectsTableBody');
        tbody.innerHTML = '';
        
        if (data.batch_subjects && data.batch_subjects.length > 0) {
            data.batch_subjects.forEach(bs => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${bs.id}</td>
                    <td>${bs.batch?.name || 'N/A'}</td>
                    <td>${bs.batch?.department?.code || 'N/A'}</td>
                    <td>${bs.course?.code || 'N/A'}</td>
                    <td>${bs.course?.name || 'N/A'}</td>
                    <td><span class="badge ${bs.is_required ? 'badge-success' : 'badge-info'}">${bs.is_required ? 'Required' : 'Elective'}</span></td>
                    <td class="action-buttons">
                        <button class="btn-admin btn-small btn-danger-admin" onclick="deleteBatchSubject(${bs.id})">🗑️ Remove</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2rem;">No subjects assigned</td></tr>';
        }
    } catch (error) {
        console.error('Error loading batch subjects:', error);
        showMessage('Error loading batch subjects: ' + error.message, true);
    }
}

async function assignBatchSubject() {
    const batch_id = document.getElementById('bs-batch-id').value;
    const course_id = document.getElementById('bs-course-id').value;
    const is_required = document.getElementById('bs-is-required').checked;
    
    if (!batch_id || !course_id) {
        showMessage('Please select Batch and Course!', true);
        return;
    }
    
    try {
        const res = await fetch('/api/admin/batch-subjects', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ batch_id: parseInt(batch_id), course_id: parseInt(course_id), is_required })
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Subject assigned to batch successfully!');
            document.getElementById('bs-course-id').value = '';
            loadBatchSubjects();
        } else {
            showMessage(data.message || 'Error assigning subject', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

async function deleteBatchSubject(bsId) {
    if (!confirm('Are you sure you want to remove this subject from the batch?')) return;
    
    try {
        const res = await fetch(`/api/admin/batch-subjects/${bsId}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Subject removed from batch successfully!');
            loadBatchSubjects();
        } else {
            showMessage(data.message || 'Error removing subject', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

// ========== TEACHER ASSIGNMENT ==========
async function loadDepartmentsForTeacherAssignments() {
    try {
        const res = await fetch('/api/admin/departments', {
            credentials: 'include'
        });
        const data = await res.json();
        
        const select = document.getElementById('ta-dept-id');
        if (select) {
            select.innerHTML = '<option value="">-- Select Department --</option>';
            if (data.departments) {
                data.departments.forEach(dept => {
                    const option = document.createElement('option');
                    option.value = dept.id;
                    option.textContent = `${dept.code} - ${dept.name}`;
                    select.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('Error loading departments:', error);
    }
}

async function loadBatchesForTeacherAssignment() {
    const deptId = document.getElementById('ta-dept-id').value;
    if (!deptId) {
        document.getElementById('ta-batch-id').innerHTML = '<option value="">-- Select Batch --</option>';
        document.getElementById('ta-batch-subject-id').innerHTML = '<option value="">-- Select Subject --</option>';
        document.getElementById('ta-section-id').innerHTML = '<option value="">-- All Sections --</option>';
        return;
    }
    
    try {
        const res = await fetch(`/api/admin/batches?department_id=${deptId}`, {
            credentials: 'include'
        });
        const data = await res.json();
        
        // Update form batch dropdown
        const formSelect = document.getElementById('ta-batch-id');
        if (formSelect) {
            formSelect.innerHTML = '<option value="">-- Select Batch --</option>';
            if (data.batches) {
                data.batches.forEach(batch => {
                    const option = document.createElement('option');
                    option.value = batch.id;
                    option.textContent = batch.name;
                    formSelect.appendChild(option);
                });
            }
        }
        
        // Update filter batch dropdown with different default
        const filterSelect = document.getElementById('filter-ta-batch');
        if (filterSelect) {
            filterSelect.innerHTML = '<option value="">All Batches</option>';
            if (data.batches) {
                data.batches.forEach(batch => {
                    const option = document.createElement('option');
                    option.value = batch.id;
                    option.textContent = batch.name;
                    filterSelect.appendChild(option);
                });
            }
        }
        
        // Clear subjects and sections when department changes
        document.getElementById('ta-batch-subject-id').innerHTML = '<option value="">-- Select Subject --</option>';
        document.getElementById('ta-section-id').innerHTML = '<option value="">-- All Sections --</option>';
        
    } catch (error) {
        console.error('Error loading batches:', error);
    }
}

async function loadSubjectsForTeacherAssignment() {
    const batchId = document.getElementById('ta-batch-id').value;
    const subjectSelect = document.getElementById('ta-batch-subject-id');
    
    if (!batchId) {
        if (subjectSelect) {
            subjectSelect.innerHTML = '<option value="">-- Select Subject --</option>';
        }
        return;
    }
    
    try {
        const res = await fetch(`/api/admin/batch-subjects?batch_id=${batchId}`, {
            credentials: 'include'
        });
        
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const data = await res.json();
        
        if (subjectSelect) {
            subjectSelect.innerHTML = '<option value="">-- Select Subject --</option>';
            
            if (data.batch_subjects && data.batch_subjects.length > 0) {
                data.batch_subjects.forEach(bs => {
                    const option = document.createElement('option');
                    option.value = bs.id;
                    option.textContent = `${bs.course?.code || 'N/A'} - ${bs.course?.name || 'N/A'}`;
                    subjectSelect.appendChild(option);
                });
                console.log(`Loaded ${data.batch_subjects.length} subjects for batch ${batchId}`);
            } else {
                console.log(`No subjects found for batch ${batchId}`);
            }
        }
    } catch (error) {
        console.error('Error loading batch subjects:', error);
        if (subjectSelect) {
            subjectSelect.innerHTML = '<option value="">-- Error loading subjects --</option>';
        }
    }
}

async function loadSectionsForTeacherAssignment() {
    const batchId = document.getElementById('ta-batch-id').value;
    if (!batchId) {
        document.getElementById('ta-section-id').innerHTML = '<option value="">-- All Sections --</option>';
        return;
    }
    
    try {
        const res = await fetch(`/api/admin/sections?batch_id=${batchId}`, {
            credentials: 'include'
        });
        const data = await res.json();
        
        const select = document.getElementById('ta-section-id');
        select.innerHTML = '<option value="">-- All Sections --</option>';
        
        if (data.sections) {
            data.sections.forEach(section => {
                const option = document.createElement('option');
                option.value = section.id;
                option.textContent = `Section ${section.name}`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading sections:', error);
    }
}

async function loadTeachersForAssignment() {
    try {
        const res = await fetch('/api/admin/teachers', {
            credentials: 'include'
        });
        const data = await res.json();
        
        const select1 = document.getElementById('ta-teacher-id');
        const select2 = document.getElementById('filter-ta-teacher');
        
        [select1, select2].forEach(select => {
            if (select) {
                select.innerHTML = '<option value="">-- Select Teacher --</option>';
                if (data.teachers) {
                    data.teachers.forEach(teacher => {
                        const option = document.createElement('option');
                        option.value = teacher.id;
                        option.textContent = teacher.name;
                        select.appendChild(option);
                    });
                }
            }
        });
    } catch (error) {
        console.error('Error loading teachers:', error);
    }
}

async function loadTeacherAssignments() {
    try {
        const batchId = document.getElementById('filter-ta-batch')?.value || '';
        const teacherId = document.getElementById('filter-ta-teacher')?.value || '';
        
        let url = '/api/admin/teacher-assignments';
        const params = [];
        if (batchId) params.push(`batch_id=${batchId}`);
        if (teacherId) params.push(`teacher_id=${teacherId}`);
        if (params.length > 0) url += '?' + params.join('&');
        
        const res = await fetch(url, {
            credentials: 'include'
        });
        const data = await res.json();
        
        const tbody = document.getElementById('teacherAssignmentsTableBody');
        tbody.innerHTML = '';
        
        if (data.assignments && data.assignments.length > 0) {
            data.assignments.forEach(assignment => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${assignment.id}</td>
                    <td>${assignment.batch_subject?.batch?.name || 'N/A'}</td>
                    <td>${assignment.batch_subject?.course?.code || 'N/A'} - ${assignment.batch_subject?.course?.name || 'N/A'}</td>
                    <td>${assignment.teacher?.name || 'N/A'}</td>
                    <td>${assignment.section ? `Section ${assignment.section.name}` : 'All Sections'}</td>
                    <td>${assignment.lecture_type || 'Theory'}</td>
                    <td class="action-buttons">
                        <button class="btn-admin btn-small btn-danger-admin" onclick="deleteTeacherAssignment(${assignment.id})">🗑️ Remove</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2rem;">No assignments found</td></tr>';
        }
    } catch (error) {
        console.error('Error loading teacher assignments:', error);
        showMessage('Error loading teacher assignments: ' + error.message, true);
    }
}

async function assignTeacherToBatch() {
    const batch_subject_id = document.getElementById('ta-batch-subject-id').value;
    const teacher_id = document.getElementById('ta-teacher-id').value;
    const section_id = document.getElementById('ta-section-id').value || null;
    const lecture_type = document.getElementById('ta-lecture-type').value;
    
    if (!batch_subject_id || !teacher_id) {
        showMessage('Please select Subject and Teacher!', true);
        return;
    }
    
    try {
        const res = await fetch('/api/admin/teacher-assignments', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                batch_subject_id: parseInt(batch_subject_id),
                teacher_id: parseInt(teacher_id),
                section_id: section_id ? parseInt(section_id) : null,
                lecture_type
            })
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Teacher assigned successfully!');
            document.getElementById('ta-batch-subject-id').value = '';
            document.getElementById('ta-teacher-id').value = '';
            document.getElementById('ta-section-id').value = '';
            loadTeacherAssignments();
        } else {
            showMessage(data.message || 'Error assigning teacher', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

async function deleteTeacherAssignment(assignmentId) {
    if (!confirm('Are you sure you want to remove this teacher assignment?')) return;
    
    try {
        const res = await fetch(`/api/admin/teacher-assignments/${assignmentId}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Assignment removed successfully!');
            loadTeacherAssignments();
        } else {
            showMessage(data.message || 'Error removing assignment', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

// ========== STUDENT MANAGEMENT ==========
async function loadDepartmentsForStudents() {
    try {
        const res = await fetch('/api/admin/departments', {
            credentials: 'include'
        });
        const data = await res.json();
        
        const selects = [
            'student-department',
            'student-filter-department',
            'report-department'
        ];
        
        selects.forEach(selectId => {
            const select = document.getElementById(selectId);
            if (select) {
                const currentValue = select.value;
                select.innerHTML = selectId === 'student-department' || selectId === 'report-department'
                    ? '<option value="">-- Select Department --</option>'
                    : '<option value="">-- All Departments --</option>';
                
                if (data.departments) {
                    data.departments.forEach(dept => {
                        const option = document.createElement('option');
                        option.value = dept.id;
                        option.textContent = `${dept.name} (${dept.code})`;
                        select.appendChild(option);
                    });
                }
                
                if (currentValue) select.value = currentValue;
            }
        });
    } catch (error) {
        console.error('Error loading departments for students:', error);
    }
}

async function loadDepartmentsForTeachers() {
    try {
        const res = await fetch('/api/admin/departments', {
            credentials: 'include'
        });
        const data = await res.json();

        const select = document.getElementById('teacher-department');
        if (select) {
            const currentValue = select.value;
            select.innerHTML = '<option value="">-- Select Department --</option>';

            if (data.departments) {
                data.departments.forEach(dept => {
                    const option = document.createElement('option');
                    option.value = dept.id;
                    option.textContent = `${dept.code} - ${dept.name}`;
                    select.appendChild(option);
                });
            }

            if (currentValue) select.value = currentValue;
        }
    } catch (error) {
        console.error('Error loading departments for teachers:', error);
    }
}

async function loadBatchesForStudents() {
    try {
        const res = await fetch('/api/admin/batches', {
            credentials: 'include'
        });
        const data = await res.json();
        
        const selects = ['student-batch', 'student-filter-batch'];
        
        selects.forEach(selectId => {
            const select = document.getElementById(selectId);
            if (select) {
                const currentValue = select.value;
                select.innerHTML = selectId === 'student-batch'
                    ? '<option value="">-- Select Batch --</option>'
                    : '<option value="">-- All Batches --</option>';
                
                if (data.batches) {
                    data.batches.forEach(batch => {
                        const option = document.createElement('option');
                        option.value = batch.id;
                        option.textContent = batch.name;
                        select.appendChild(option);
                    });
                }
                
                if (currentValue) select.value = currentValue;
            }
        });
    } catch (error) {
        console.error('Error loading batches for students:', error);
    }
}

async function loadSectionsForStudents() {
    try {
        const res = await fetch('/api/admin/sections', {
            credentials: 'include'
        });
        const data = await res.json();
        
        const selects = ['student-section', 'student-filter-section'];
        
        selects.forEach(selectId => {
            const select = document.getElementById(selectId);
            if (select) {
                const currentValue = select.value;
                select.innerHTML = selectId === 'student-section'
                    ? '<option value="">-- Select Section --</option>'
                    : '<option value="">-- All Sections --</option>';
                
                if (data.sections) {
                    data.sections.forEach(section => {
                        const option = document.createElement('option');
                        option.value = section.id;
                        option.textContent = `${section.name} (Batch: ${section.batch?.name || 'N/A'})`;
                        select.appendChild(option);
                    });
                }
                
                if (currentValue) select.value = currentValue;
            }
        });

        // Additionally, if a department select exists, load courses for that department
        const deptSelect = document.getElementById('student-department');
        if (deptSelect && deptSelect.value) {
            loadCoursesForStudent(deptSelect.value);
        }
    } catch (error) {
        console.error('Error loading sections for students:', error);
    }
}

async function loadCoursesForStudent(deptId) {
    if (!deptId) return;
    try {
        const res = await fetch(`/api/admin/courses?department_id=${deptId}`, { credentials: 'include' });
        const data = await res.json();
        const courses = data.courses || [];
        const container = document.getElementById('student-courses-list');
        if (!container) return;

        if (courses.length === 0) {
            container.innerHTML = '<p style="color:#999;">No courses found</p>';
            return;
        }

        container.innerHTML = courses.map(c => `
            <label style="display:flex; align-items:center; gap:8px; padding:6px; cursor:pointer; border-radius:4px;" onmouseover="this.style.background='#f5f5f5'" onmouseout="this.style.background=''">
                <input type="checkbox" value="${c.id}" class="student-course-checkbox" style="width:16px; height:16px;">
                <span>${c.name} <small style="color:#999;">(${c.code})</small></span>
            </label>
        `).join('');
    } catch (error) {
        console.error('Error loading courses for student:', error);
    }
}

async function loadStudents() {
    try {
        const department_id = document.getElementById('student-filter-department')?.value;
        const batch_id = document.getElementById('student-filter-batch')?.value;
        const section_id = document.getElementById('student-filter-section')?.value;
        const search = document.getElementById('student-search')?.value.trim();
        
        let url = '/api/admin/students?';
        const params = new URLSearchParams();
        if (department_id) params.append('department_id', department_id);
        if (batch_id) params.append('batch_id', batch_id);
        if (section_id) params.append('section_id', section_id);
        if (search) params.append('search', search);
        url += params.toString();
        
        const res = await fetch(url, {
            credentials: 'include'
        });
        const data = await res.json();
        
        const tbody = document.getElementById('studentsTableBody');
        tbody.innerHTML = '';
        
        if (data.students && data.students.length > 0) {
            data.students.forEach(student => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${student.id}</td>
                    <td>${student.registration_number}</td>
                    <td>${student.name}</td>
                    <td>${student.email || 'N/A'}</td>
                    <td>${student.department?.name || 'N/A'}</td>
                    <td>${student.batch?.name || 'N/A'}</td>
                    <td>${student.section || student.section_obj?.name || 'N/A'}</td>
                    <td>${student.phone || 'N/A'}</td>
                    <td><span class="badge ${student.is_active !== false ? 'badge-success' : 'badge-danger'}">${student.is_active !== false ? 'Active' : 'Inactive'}</span></td>
                    <td class="action-buttons">
                        <button class="btn-admin btn-small btn-warning-admin" onclick="editStudent(${student.id})">✏️ Edit</button>
                        <button class="btn-admin btn-small btn-danger-admin" onclick="deleteStudent(${student.id})">🗑️ Delete</button>
                        <button onclick="manageStudentCourses(${student.id}, '${(student.name||'').replace(/'/g, "\\'") }')" style="background:#667eea; color:white; border:none; padding:4px 10px; border-radius:6px; cursor:pointer; font-size:12px; margin-left:6px;">📚 Courses</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; padding: 2rem;">No students found</td></tr>';
        }
    } catch (error) {
        console.error('Error loading students:', error);
        showMessage('Error loading students: ' + error.message, true);
    }
}

async function createStudent() {
    const registration_number = document.getElementById('student-registration').value.trim().toUpperCase();
    const name = document.getElementById('student-name').value.trim();
    const email = document.getElementById('student-email').value.trim();
    const department_id = document.getElementById('student-department').value;
    const batch_id = document.getElementById('student-batch').value;
    const section_id = document.getElementById('student-section').value;
    const phone = document.getElementById('student-phone').value.trim();
    const section = document.getElementById('student-section')?.selectedOptions?.[0]?.textContent.split(' (')[0].trim() || '';
    
    if (!registration_number || !name) {
        showMessage('Roll number and name are required!', true);
        return;
    }
    
    try {
        // Get selected courses
        const selectedCourses = Array.from(
            document.querySelectorAll('.student-course-checkbox:checked')
        ).map(cb => parseInt(cb.value));

        const res = await fetch('/api/admin/students', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                registration_number,
                name,
                email: email || null,
                department_id: department_id ? parseInt(department_id) : null,
                batch_id: batch_id ? parseInt(batch_id) : null,
                section_id: section_id ? parseInt(section_id) : null,
                section: section || null,
                phone: phone || null,
                course_ids: selectedCourses
            })
        });
        
        const data = await res.json();
        
        if (data.success) {
            let msg = '✅ Student added!';
            if (data.auto_password) {
                msg += `\n\n🔑 Password: ${data.auto_password}`;
                alert(msg);
            }
            showMessage('✅ Student added!');
            document.getElementById('student-registration').value = '';
            document.getElementById('student-name').value = '';
            document.getElementById('student-email').value = '';
            document.getElementById('student-department').value = '';
            document.getElementById('student-batch').value = '';
            document.getElementById('student-section').value = '';
            document.getElementById('student-phone').value = '';
            loadStudents();
            loadStats();
        } else {
            showMessage(data.message || 'Error creating student', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

async function editStudent(studentId) {
    try {
        const res = await fetch('/api/admin/students', {
            credentials: 'include'
        });
        const data = await res.json();
        const student = (data.students || []).find(
            item => parseInt(item.id) === parseInt(studentId));

        if (!student) {
            showMessage('Student not found', true);
            return;
        }

        const name = prompt('Student name:', student.name || '');
        if (name === null) return;
        const email = prompt('Student email:', student.email || '');
        if (email === null) return;
        const departmentId = prompt('Department ID:', student.department?.id || student.department_id || '');
        if (departmentId === null) return;
        const batchId = prompt('Batch ID:', student.batch?.id || student.batch_id || '');
        if (batchId === null) return;
        const sectionId = prompt('Section ID:', student.section_obj?.id || student.section_id || '');
        if (sectionId === null) return;
        const section = prompt('Section:', student.section || student.section_obj?.name || '');
        if (section === null) return;
        const phone = prompt('Phone:', student.phone || '');
        if (phone === null) return;

        const putRes = await fetch(`/api/admin/students/${studentId}`, {
            method: 'PUT',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name.trim(),
                email: email.trim(),
                department_id: departmentId ? parseInt(departmentId, 10) : null,
                batch_id: batchId ? parseInt(batchId, 10) : null,
                section_id: sectionId ? parseInt(sectionId, 10) : null,
                section: section.trim(),
                phone: phone.trim()
            })
        });

        const putData = await putRes.json();
        if (putData.success) {
            showMessage('✅ Student updated successfully!');
            loadStudents();
            loadStats();
        } else {
            showMessage(putData.message || 'Error updating student', true);
        }
    } catch (error) {
        console.error('Edit student error:', error);
        showMessage('Error: ' + error.message, true);
    }
}

async function deleteStudent(studentId) {
    if (!confirm('Are you sure you want to delete this student? This action cannot be undone.')) return;
    
    try {
        const res = await fetch(`/api/admin/students/${studentId}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Student deleted successfully!');
            loadStudents();
            loadStats();
        } else {
            showMessage(data.message || 'Error deleting student', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

// ========== ANALYTICS ==========
async function loadAnalytics() {
    await loadStats(); // Load stats which updates analytics cards
    
    // Load teacher performance data
    try {
        const res = await fetch('/api/admin/teachers', {
            credentials: 'include'
        });
        const data = await res.json();
        
        if (data.teachers && data.teachers.length > 0) {
            const chartDiv = document.getElementById('teacher-performance-chart');
            let html = '<table style="width: 100%; border-collapse: collapse;">';
            html += '<thead><tr><th style="padding: 0.5rem; border-bottom: 2px solid #ddd;">Teacher</th><th style="padding: 0.5rem; border-bottom: 2px solid #ddd;">Department</th><th style="padding: 0.5rem; border-bottom: 2px solid #ddd;">Courses</th></tr></thead><tbody>';
            
            data.teachers.slice(0, 10).forEach(teacher => {
                html += `<tr><td style="padding: 0.5rem; border-bottom: 1px solid #eee;">${teacher.name}</td>`;
                html += `<td style="padding: 0.5rem; border-bottom: 1px solid #eee;">${teacher.department || 'N/A'}</td>`;
                html += `<td style="padding: 0.5rem; border-bottom: 1px solid #eee;">${teacher.courses_count || 0}</td></tr>`;
            });
            
            html += '</tbody></table>';
            chartDiv.innerHTML = html;
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// ========== REPORTS ==========
async function loadDepartmentsForReports() {
    await loadDepartmentsForStudents(); // Reuse the same function
}

async function generateReport() {
    const reportType = document.getElementById('report-type').value;
    const format = document.getElementById('report-format').value;
    const dateFrom = document.getElementById('report-date-from').value;
    const dateTo = document.getElementById('report-date-to').value;
    const department = document.getElementById('report-department').value;
    
    if (!reportType || !format) {
        showMessage('Please select report type and format!', true);
        return;
    }
    
    try {
        showMessage('Generating report... Please wait.', false);
        
        // For now, show a message. Actual report generation can be implemented
        setTimeout(() => {
            showMessage(`✅ Report generated: ${reportType} (${format.toUpperCase()}) - Coming soon!`, false);
        }, 1000);
        
        // TODO: Implement actual report generation endpoint
    } catch (error) {
        showMessage('Error generating report: ' + error.message, true);
    }
}

// ========== TIMETABLE MANAGEMENT ==========
async function loadDepartmentsForTimetable() {
    try {
        const res = await fetch('/api/admin/departments', {
            credentials: 'include'
        });
        const data = await res.json();
        
        const selects = ['timetable-department', 'timetable-filter-department'];
        
        selects.forEach(selectId => {
            const select = document.getElementById(selectId);
            if (select) {
                const currentValue = select.value;
                select.innerHTML = selectId === 'timetable-department'
                    ? '<option value="">-- Select Department --</option>'
                    : '<option value="">-- All Departments --</option>';
                
                if (data.departments) {
                    data.departments.forEach(dept => {
                        const option = document.createElement('option');
                        option.value = dept.id;
                        option.textContent = `${dept.name} (${dept.code})`;
                        select.appendChild(option);
                    });
                }
                
                if (currentValue) select.value = currentValue;
            }
        });
    } catch (error) {
        console.error('Error loading departments for timetable:', error);
    }
}

async function loadCoursesForTimetable() {
    try {
        const res = await fetch('/api/admin/courses', {
            credentials: 'include'
        });
        const data = await res.json();
        
        const selects = ['timetable-course', 'timetable-filter-course'];
        
        selects.forEach(selectId => {
            const select = document.getElementById(selectId);
            if (select) {
                const currentValue = select.value;
                select.innerHTML = selectId === 'timetable-course'
                    ? '<option value="">-- Select Course --</option>'
                    : '<option value="">-- All Courses --</option>';
                
                if (data.courses) {
                    data.courses.forEach(course => {
                        const option = document.createElement('option');
                        option.value = course.id;
                        option.textContent = `${course.code} - ${course.name}`;
                        select.appendChild(option);
                    });
                }
                
                if (currentValue) select.value = currentValue;
            }
        });
    } catch (error) {
        console.error('Error loading courses for timetable:', error);
    }
}

async function loadTeachersForTimetable() {
    try {
        const res = await fetch('/api/admin/teachers', {
            credentials: 'include'
        });
        const data = await res.json();
        
        const selects = ['timetable-teacher', 'timetable-filter-teacher'];
        
        selects.forEach(selectId => {
            const select = document.getElementById(selectId);
            if (select) {
                const currentValue = select.value;
                select.innerHTML = selectId === 'timetable-teacher'
                    ? '<option value="">-- Select Teacher --</option>'
                    : '<option value="">-- All Teachers --</option>';
                
                if (data.teachers) {
                    data.teachers.forEach(teacher => {
                        const option = document.createElement('option');
                        option.value = teacher.id;
                        option.textContent = teacher.name;
                        select.appendChild(option);
                    });
                }
                
                if (currentValue) select.value = currentValue;
            }
        });
    } catch (error) {
        console.error('Error loading teachers for timetable:', error);
    }
}

async function loadBatchesForTimetable() {
    const departmentId = document.getElementById('timetable-department')?.value;
    if (!departmentId) return;
    
    try {
        const res = await fetch(`/api/admin/batches?department_id=${departmentId}`, {
            credentials: 'include'
        });
        const data = await res.json();
        
        const select = document.getElementById('timetable-batch');
        if (select) {
            select.innerHTML = '<option value="">-- Select Batch --</option>';
            if (data.batches) {
                data.batches.forEach(batch => {
                    const option = document.createElement('option');
                    option.value = batch.id;
                    option.textContent = batch.name;
                    select.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('Error loading batches for timetable:', error);
    }
}

async function loadSectionsForTimetable() {
    const batchId = document.getElementById('timetable-batch')?.value;
    if (!batchId) return;
    
    try {
        const res = await fetch(`/api/admin/sections?batch_id=${batchId}`, {
            credentials: 'include'
        });
        const data = await res.json();
        
        const select = document.getElementById('timetable-section');
        if (select) {
            select.innerHTML = '<option value="">-- Select Section --</option>';
            if (data.sections) {
                data.sections.forEach(section => {
                    const option = document.createElement('option');
                    option.value = section.id;
                    option.textContent = section.name;
                    select.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('Error loading sections for timetable:', error);
    }
}

async function loadBatchesForTimetableFilter() {
    const departmentId = document.getElementById('timetable-filter-department')?.value;
    
    try {
        const url = departmentId 
            ? `/api/admin/batches?department_id=${departmentId}`
            : '/api/admin/batches';
        const res = await fetch(url, {
            credentials: 'include'
        });
        const data = await res.json();
        
        const select = document.getElementById('timetable-filter-batch');
        if (select) {
            select.innerHTML = '<option value="">-- All Batches --</option>';
            if (data.batches) {
                data.batches.forEach(batch => {
                    const option = document.createElement('option');
                    option.value = batch.id;
                    option.textContent = batch.name;
                    select.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('Error loading batches for timetable filter:', error);
    }
}

async function loadSectionsForTimetableFilter() {
    const batchId = document.getElementById('timetable-filter-batch')?.value;
    
    try {
        const url = batchId 
            ? `/api/admin/sections?batch_id=${batchId}`
            : '/api/admin/sections';
        const res = await fetch(url, {
            credentials: 'include'
        });
        const data = await res.json();
        
        const select = document.getElementById('timetable-filter-section');
        if (select) {
            select.innerHTML = '<option value="">-- All Sections --</option>';
            if (data.sections) {
                data.sections.forEach(section => {
                    const option = document.createElement('option');
                    option.value = section.id;
                    option.textContent = `${section.name} (${section.batch?.name || 'N/A'})`;
                    select.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('Error loading sections for timetable filter:', error);
    }
}

async function loadTimetable() {
    try {
        const department_id = document.getElementById('timetable-filter-department')?.value;
        const batch_id = document.getElementById('timetable-filter-batch')?.value;
        const section_id = document.getElementById('timetable-filter-section')?.value;
        const teacher_id = document.getElementById('timetable-filter-teacher')?.value;
        const course_id = document.getElementById('timetable-filter-course')?.value;
        const semester = document.getElementById('timetable-filter-semester')?.value.trim();
        const is_active = document.getElementById('timetable-filter-active')?.checked;
        
        let url = '/api/admin/timetable?';
        const params = new URLSearchParams();
        if (department_id) params.append('department_id', department_id);
        if (batch_id) params.append('batch_id', batch_id);
        if (section_id) params.append('section_id', section_id);
        if (teacher_id) params.append('teacher_id', teacher_id);
        if (course_id) params.append('course_id', course_id);
        if (semester) params.append('semester', semester);
        if (is_active !== undefined) params.append('is_active', is_active);
        url += params.toString();
        
        const res = await fetch(url, {
            credentials: 'include'
        });
        const data = await res.json();
        
        const tbody = document.getElementById('timetableTableBody');
        tbody.innerHTML = '';
        
        if (data.timetables && data.timetables.length > 0) {
            data.timetables.forEach(tt => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${tt.id}</td>
                    <td>${tt.course?.code || 'N/A'} - ${tt.course?.name || 'N/A'}</td>
                    <td>${tt.teacher?.name || 'N/A'}</td>
                    <td>${tt.section?.name || 'N/A'}</td>
                    <td>${tt.batch?.name || 'N/A'}</td>
                    <td>${tt.day_name || 'N/A'}</td>
                    <td>${tt.start_time || 'N/A'} - ${tt.end_time || 'N/A'}</td>
                    <td>${tt.room || 'N/A'}</td>
                    <td>${tt.semester || 'N/A'}</td>
                    <td>${tt.session_type || 'N/A'}</td>
                    <td><span class="badge ${tt.is_active ? 'badge-success' : 'badge-danger'}">${tt.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td class="action-buttons">
                        <button class="btn-admin btn-small btn-warning-admin" onclick="editTimetable(${tt.id})">✏️ Edit</button>
                        <button class="btn-admin btn-small btn-danger-admin" onclick="deleteTimetable(${tt.id})">🗑️ Delete</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="12" style="text-align: center; padding: 2rem;">No timetable entries found</td></tr>';
        }
    } catch (error) {
        console.error('Error loading timetable:', error);
        showMessage('Error loading timetable: ' + error.message, true);
    }
}

async function createTimetable() {
    const course_id = document.getElementById('timetable-course').value;
    const teacher_id = document.getElementById('timetable-teacher').value;
    const batch_id = document.getElementById('timetable-batch').value;
    const section_id = document.getElementById('timetable-section').value;
    const day_of_week = document.getElementById('timetable-day').value;
    const start_time = document.getElementById('timetable-start-time').value;
    const end_time = document.getElementById('timetable-end-time').value;
    const room = document.getElementById('timetable-room').value.trim();
    const semester = document.getElementById('timetable-semester').value.trim();
    const session_type = document.getElementById('timetable-session-type').value;
    
    if (!course_id || !teacher_id || !batch_id || !section_id || day_of_week === '' || !start_time || !end_time || !semester) {
        showMessage('Please fill all required fields!', true);
        return;
    }
    
    try {
        const res = await fetch('/api/admin/timetable', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                course_id: parseInt(course_id),
                teacher_id: parseInt(teacher_id),
                batch_id: parseInt(batch_id),
                section_id: parseInt(section_id),
                day_of_week: parseInt(day_of_week),
                start_time,
                end_time,
                room: room || null,
                semester,
                session_type: session_type || null
            })
        });
        
        const data = await res.json();
        
        if (data.success) {
            if (data.conflicts && data.conflicts.length > 0) {
                const conflictsDiv = document.getElementById('timetable-conflicts');
                const conflictsList = document.getElementById('conflicts-list');
                conflictsList.innerHTML = '';
                data.conflicts.forEach(conflict => {
                    const li = document.createElement('li');
                    li.textContent = conflict;
                    conflictsList.appendChild(li);
                });
                conflictsDiv.style.display = 'block';
            } else {
                document.getElementById('timetable-conflicts').style.display = 'none';
            }
            
            showMessage(data.message);
            // Clear form
            document.getElementById('timetable-course').value = '';
            document.getElementById('timetable-teacher').value = '';
            document.getElementById('timetable-batch').value = '';
            document.getElementById('timetable-section').value = '';
            document.getElementById('timetable-day').value = '0';
            document.getElementById('timetable-start-time').value = '';
            document.getElementById('timetable-end-time').value = '';
            document.getElementById('timetable-room').value = '';
            document.getElementById('timetable-semester').value = '';
            document.getElementById('timetable-session-type').value = '';
            loadTimetable();
        } else {
            showMessage(data.message || 'Error creating timetable', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

async function editTimetable(timetableId) {
    showMessage('Edit functionality will be implemented', false);
}

async function deleteTimetable(timetableId) {
    if (!confirm('Are you sure you want to delete this timetable entry? This action cannot be undone.')) return;
    
    try {
        const res = await fetch(`/api/admin/timetable/${timetableId}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await res.json();
        
        if (data.success) {
            showMessage('✅ Timetable entry deleted successfully!');
            loadTimetable();
        } else {
            showMessage(data.message || 'Error deleting timetable', true);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, true);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    loadUsers(); // Load default tab data
    
    // Refresh stats every 30 seconds
    setInterval(loadStats, 30000);
});

