function redirectToLogin() {
	window.location.href = '/login'; // Redirects to the /login route
}

function redirectToRegister() {
	window.location.href = '/register'; // Redirects to the /register route
}

function redirectToHome() {
	window.location.href = '/'; // Redirects to the / route
}

function redirectToProfile() {

}
function redirectToDashboard() {
	// check if user is logged in
	const token = localStorage.getItem('token');
	if (!token) {
		return 
	}
	// decode jwt token
	const decoded = JSON.parse(atob(token.split('.')[1]));
	// check if token is expired
	if (Date.now() >= decoded.exp * 1000) {
		redirectToLogin();
	}
	else {
		window.location.href = '/'; // Redirects to the /dashboard route
	}
}

function logout() {
	localStorage.removeItem('token');
	redirectToLogin();
}
function get_username() {
	const token = localStorage.getItem('token');
	username = ""
	try {
		username = JSON.parse(atob(token.split('.')[1])).sub;
	} catch (e) {
		return null;
	}
	return username;
};

// // Bind event listeners once DOM is fully loaded
// document.addEventListener('DOMContentLoaded', function() {

// });
